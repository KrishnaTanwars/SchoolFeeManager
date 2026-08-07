"""
Professional MIS Financial Reports & Executive Analytics Dashboard View for EduLedger ERP v1.8.0.
Features interactive Category Cards Dashboard, specialized report viewers, common filter panel,
real-time summary KPI cards, SQL/in-memory pagination, live search, and multi-format exports (CSV, Excel, PDF, Print).
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QFileDialog, QStackedWidget, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QDate

from controllers.report_controller import ReportController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.settings_controller import SettingsController
from services.pdf_service import PDFService
from services.export_service import ExportService
from services.print_service import PrintService
from utils.helpers import format_currency, format_date
from utils.logger import logger


class ReportCategoryCard(QFrame):
    """Clickable Visual Category Card for Reports Dashboard."""

    def __init__(self, icon: str, title: str, description: str, report_key: str, on_click_callback):
        super().__init__()
        self.report_key = report_key
        self.on_click_callback = on_click_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(140)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px;
            }
            QFrame:hover {
                border: 2px solid #2563eb;
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        hdr_layout = QHBoxLayout()
        hdr_layout.setSpacing(8)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #1e293b; background: transparent;")

        hdr_layout.addWidget(lbl_icon)
        hdr_layout.addWidget(lbl_title, stretch=1)

        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")

        btn_open = QPushButton("Generate Report →")
        btn_open.setFixedHeight(28)
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                color: #2563eb;
                font-weight: 700;
                font-size: 11px;
                border: 1px solid #bfdbfe;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2563eb;
                color: #ffffff;
            }
        """)
        btn_open.clicked.connect(lambda: self.on_click_callback(self.report_key))

        layout.addLayout(hdr_layout)
        layout.addWidget(lbl_desc, stretch=1)
        layout.addWidget(btn_open)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click_callback(self.report_key)
        super().mousePressEvent(event)


class ReportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_report_key = "daily"
        self.raw_report_data = None
        self.filtered_rows = []
        self.current_page = 1
        self.page_size = 50

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Header Frame
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background-color: #1e3a8a; border-radius: 8px; padding: 10px 14px;")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 6, 8, 6)

        self.btn_back_dashboard = QPushButton("⬅ Back to Reports Dashboard")
        self.btn_back_dashboard.setCursor(Qt.PointingHandCursor)
        self.btn_back_dashboard.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e3a8a;
                font-weight: bold;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_back_dashboard.clicked.connect(self.show_dashboard)
        self.btn_back_dashboard.hide()

        self.lbl_header_title = QLabel("Financial Analytics & MIS Reports Center")
        self.lbl_header_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800;")

        self.lbl_header_subtitle = QLabel("Generate financial, operational, ledger, and fee collection reports")
        self.lbl_header_subtitle.setStyleSheet("color: #93c5fd; font-size: 11px; font-weight: 600;")

        v_head = QVBoxLayout()
        v_head.setSpacing(2)
        v_head.addWidget(self.lbl_header_title)
        v_head.addWidget(self.lbl_header_subtitle)

        header_layout.addWidget(self.btn_back_dashboard)
        header_layout.addLayout(v_head, stretch=1)

        main_layout.addWidget(self.header_frame)

        # Stacked Widget for Router (Index 0 = Dashboard, Index 1 = Active Report View)
        self.stack = QStackedWidget()

        # Page 0: Reports Dashboard
        self.page_dashboard = QWidget()
        self.setup_dashboard_page()
        self.stack.addWidget(self.page_dashboard)

        # Page 1: Active Report Viewer
        self.page_report_viewer = QWidget()
        self.setup_report_viewer_page()
        self.stack.addWidget(self.page_report_viewer)

        main_layout.addWidget(self.stack)

        # Initial View
        self.show_dashboard()

    # ---------------- PAGE NAVIGATION ----------------
    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.lbl_header_title.setText("Financial Analytics & MIS Reports Center")
        self.lbl_header_subtitle.setText("Generate financial, operational, ledger, and fee collection reports")
        self.btn_back_dashboard.hide()

    def open_report(self, report_key: str):
        self.active_report_key = report_key
        titles = {
            "daily": ("📅 Daily Fee Collection Report", "Daily breakdown of receipts, collections, discounts, fines, and payment modes"),
            "monthly": ("🗓 Monthly Collection Report", "Monthly aggregated collection summary across the financial year"),
            "date_range": ("📆 Custom Date Range Collection Report", "Filter collection records across any custom date range and criteria"),
            "class_wise": ("🏫 Class-wise Collection Report", "Revenue and outstanding fee summary grouped by class and academic section"),
            "course_wise": ("🎓 Course-wise Collection Report", "Comparative fee collection and outstanding summary for UG and PG courses"),
            "outstanding": ("⚠️ Outstanding Fee Report", "Student-wise outstanding fee balances, total fees, and payment statuses"),
            "ledger": ("📖 Student Ledger Report", "Individual student ledger history with running balance, receipts, and dues"),
            "register": ("📜 Receipt Register Log", "Comprehensive receipt transaction register with operator tracking"),
            "fee_head": ("🏷 Fee Head Collection Report", "Fee collection aggregated by head categories (Tuition, Development, Lab, etc.)"),
            "payment_mode": ("💳 Payment Mode Breakdown Report", "Transaction volume and collection totals grouped by payment method")
        }

        if report_key in titles:
            title, subtitle = titles[report_key]
            self.lbl_header_title.setText(title)
            self.lbl_header_subtitle.setText(subtitle)
            self.btn_back_dashboard.show()
            self.stack.setCurrentIndex(1)
            self.configure_filters_for_report(report_key)
            self.generate_active_report()

    # ---------------- DASHBOARD PAGE ----------------
    def setup_dashboard_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        lbl_desc = QLabel("Select an Management Information System (MIS) report below to analyze financial statements and collection trends:")
        lbl_desc.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")
        layout.addWidget(lbl_desc)

        grid = QGridLayout()
        grid.setSpacing(12)

        reports = [
            ("📅", "Daily Collection Report", "Daily collection breakdown, receipt counts, discounts, fines, and payment modes.", "daily"),
            ("🗓", "Monthly Collection Report", "Monthly aggregated revenue totals, discounts, fines, and net total summary.", "monthly"),
            ("📆", "Date Range Collection", "Custom date range collection filtering by session, course, class, and payment mode.", "date_range"),
            ("🏫", "Class-wise Collection", "Class-wise revenue comparison, student counts, collections, and outstanding dues.", "class_wise"),
            ("🎓", "Course-wise Collection", "Separate UG and PG course collection totals, student counts, and outstanding balances.", "course_wise"),
            ("⚠️", "Outstanding Fee Report", "Student-wise outstanding balances, total fees demanded, and payment status breakdown.", "outstanding"),
            ("📖", "Student Ledger Report", "Complete student ledger history, running balance, receipt log, discounts, and fines.", "ledger"),
            ("📜", "Receipt Register Log", "Complete transaction register log with receipt numbers, dates, amounts, and operators.", "register"),
            ("🏷", "Fee Head Collection Report", "Fee revenue grouped by head categories (Tuition, Development, Laboratory, Sports, etc.).", "fee_head"),
            ("💳", "Payment Mode Report", "Collection breakdown by payment method (Cash, UPI, Cheque, Card, Net Banking, DD).", "payment_mode")
        ]

        row, col = 0, 0
        for icon, title, desc, key in reports:
            card = ReportCategoryCard(icon, title, desc, key, self.open_report)
            grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        layout.addLayout(grid)
        layout.addStretch()

        scroll.setWidget(container)
        p_layout = QVBoxLayout(self.page_dashboard)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(scroll)

    # ---------------- REPORT VIEWER PAGE ----------------
    def setup_report_viewer_page(self):
        layout = QVBoxLayout(self.page_report_viewer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. Filter Panel
        filter_box = QGroupBox("Report Filters & Selection Criteria")
        filter_box.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        self.filter_layout = QGridLayout(filter_box)
        self.filter_layout.setContentsMargins(10, 10, 10, 10)
        self.filter_layout.setSpacing(8)

        # Filter Inputs
        self.cmb_session = QComboBox()
        self.cmb_session.setFixedHeight(32)
        self.cmb_session.addItem("All Sessions", "All")

        self.cmb_course = QComboBox()
        self.cmb_course.setFixedHeight(32)
        self.cmb_course.addItems(["All Courses", "UG", "PG"])

        self.cmb_class = QComboBox()
        self.cmb_class.setFixedHeight(32)
        self.cmb_class.addItem("All Classes", "All")

        self.cmb_mode = QComboBox()
        self.cmb_mode.setFixedHeight(32)
        self.cmb_mode.addItems(["All Payment Modes", "Cash", "UPI", "Cheque", "Card", "Net Banking", "Demand Draft"])

        self.cmb_fee_head = QComboBox()
        self.cmb_fee_head.setFixedHeight(32)
        self.cmb_fee_head.addItem("All Fee Heads", "All")

        self.dt_from = QDateEdit()
        self.dt_from.setFixedHeight(32)
        self.dt_from.setCalendarPopup(True)
        self.dt_from.setDisplayFormat("dd-MM-yyyy")
        self.dt_from.setDate(QDate.currentDate())

        self.dt_to = QDateEdit()
        self.dt_to.setFixedHeight(32)
        self.dt_to.setCalendarPopup(True)
        self.dt_to.setDisplayFormat("dd-MM-yyyy")
        self.dt_to.setDate(QDate.currentDate())

        self.txt_student = QLineEdit()
        self.txt_student.setFixedHeight(32)
        self.txt_student.setPlaceholderText("Student Adm No or Name...")

        self.cmb_out_filter = QComboBox()
        self.cmb_out_filter.setFixedHeight(32)
        self.cmb_out_filter.addItems(["All Students", "Only Outstanding", "Only Fully Paid"])

        self.cmb_sort_by = QComboBox()
        self.cmb_sort_by.setFixedHeight(32)
        self.cmb_sort_by.addItems(["Highest Collection", "Lowest Collection", "Class Name"])

        # Filter Action Buttons
        self.btn_generate = QPushButton("📊  Generate Report")
        self.btn_generate.setFixedHeight(32)
        self.btn_generate.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 5px; padding: 0 12px;")
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.clicked.connect(self.generate_active_report)

        self.btn_reset = QPushButton("🔄  Reset Filters")
        self.btn_reset.setFixedHeight(32)
        self.btn_reset.setProperty("class", "SecondaryBtn")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filters)

        layout.addWidget(filter_box)

        # 2. Summary KPI Cards
        self.summary_container = QHBoxLayout()
        self.summary_container.setSpacing(10)
        
        self.card_1 = QLabel("Metric 1: <b>0</b>")
        self.card_2 = QLabel("Metric 2: <b>0</b>")
        self.card_3 = QLabel("Metric 3: <b>0</b>")
        self.card_4 = QLabel("Metric 4: <b>0</b>")
        self.card_5 = QLabel("Metric 5: <b>0</b>")

        for card in [self.card_1, self.card_2, self.card_3, self.card_4, self.card_5]:
            card.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; font-size: 12px; color: #1e3a8a;")
            self.summary_container.addWidget(card)

        layout.addLayout(self.summary_container)

        # 3. Pagination & Live Search Toolbar
        toolbar_layout = QHBoxLayout()

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(32)
        self.txt_search.setPlaceholderText("🔍  Live search in active report table...")
        self.txt_search.textChanged.connect(self.apply_search_and_pagination)
        toolbar_layout.addWidget(self.txt_search, stretch=2)

        toolbar_layout.addStretch(1)

        toolbar_layout.addWidget(QLabel("Rows per page:"))
        self.cmb_page_size = QComboBox()
        self.cmb_page_size.setFixedHeight(32)
        self.cmb_page_size.addItems(["25", "50", "100", "All"])
        self.cmb_page_size.setCurrentText("50")
        self.cmb_page_size.currentTextChanged.connect(self.on_page_size_changed)
        toolbar_layout.addWidget(self.cmb_page_size)

        nav_btn_style = """
            QPushButton {
                background-color: #ffffff;
                color: #1e3a8a;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
                min-height: 34px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #eff6ff;
                color: #2563eb;
                border-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #f8fafc;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
        """

        # Page Nav Buttons
        self.btn_first = QPushButton("<< First")
        self.btn_prev = QPushButton("< Prev")
        self.lbl_page_info = QLabel("Page 1 of 1")
        self.lbl_page_info.setStyleSheet("font-weight: bold; color: #334155;")
        self.btn_next = QPushButton("Next >")
        self.btn_last = QPushButton("Last >>")

        for b in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            b.setMinimumSize(80, 34)
            b.setStyleSheet(nav_btn_style)
            b.setCursor(Qt.PointingHandCursor)

        self.btn_first.setToolTip("First Page")
        self.btn_prev.setToolTip("Previous Page")
        self.btn_next.setToolTip("Next Page")
        self.btn_last.setToolTip("Last Page")

        self.btn_first.clicked.connect(lambda: self.go_to_page(1))
        self.btn_prev.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
        self.btn_next.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        self.btn_last.clicked.connect(lambda: self.go_to_page(999999))

        toolbar_layout.addWidget(self.btn_first)
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.lbl_page_info)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addWidget(self.btn_last)

        layout.addLayout(toolbar_layout)

        # 4. Report Results Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #e2e8f0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                color: #0f172a;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #cbd5e1;
            }
        """)
        layout.addWidget(self.table)

        # 5. Export & Print Toolbar
        exp_layout = QHBoxLayout()
        
        self.btn_export_pdf = QPushButton("📄  Export Report PDF")
        self.btn_export_pdf.setFixedHeight(36)
        self.btn_export_pdf.setProperty("class", "SecondaryBtn")
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        self.btn_export_csv = QPushButton("📥  Export CSV")
        self.btn_export_csv.setFixedHeight(36)
        self.btn_export_csv.setProperty("class", "SecondaryBtn")
        self.btn_export_csv.clicked.connect(self.export_csv)

        self.btn_export_excel = QPushButton("📊  Export Excel")
        self.btn_export_excel.setFixedHeight(36)
        self.btn_export_excel.setProperty("class", "SecondaryBtn")
        self.btn_export_excel.clicked.connect(self.export_excel)

        self.btn_print = QPushButton("🖨  Print Report")
        self.btn_print.setFixedHeight(36)
        self.btn_print.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; border-radius: 5px; padding: 0 14px;")
        self.btn_print.clicked.connect(self.print_report)

        exp_layout.addWidget(self.btn_export_pdf)
        exp_layout.addWidget(self.btn_export_csv)
        exp_layout.addWidget(self.btn_export_excel)
        exp_layout.addStretch()
        exp_layout.addWidget(self.btn_print)

        layout.addLayout(exp_layout)

        # Populate Dynamic Filter Options
        self.load_filter_options()

    def load_filter_options(self):
        # Academic Sessions
        self.cmb_session.clear()
        self.cmb_session.addItem("All Sessions", "All")
        sessions = SettingsController.get_academic_sessions()
        for s in sessions:
            self.cmb_session.addItem(s.session_name, s.session_name)

        # Classes
        self.cmb_class.clear()
        self.cmb_class.addItem("All Classes", "All")
        classes = StudentController.get_distinct_classes()
        for c in classes:
            self.cmb_class.addItem(c, c)

        # Fee Heads
        self.cmb_fee_head.clear()
        self.cmb_fee_head.addItem("All Fee Heads", "All")
        categories = FeeController.get_all_categories()
        for fc in categories:
            self.cmb_fee_head.addItem(fc.name, fc.name)

    def configure_filters_for_report(self, key: str):
        # Clear filter layout and re-populate relevant widgets
        while self.filter_layout.count():
            item = self.filter_layout.takeAt(0)
            if item.widget():
                item.widget().hide()

        r, c = 0, 0
        def add_filt(lbl_text, widget):
            nonlocal r, c
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("font-weight: 600; color: #334155;")
            lbl.show()
            widget.show()
            self.filter_layout.addWidget(lbl, r, c)
            self.filter_layout.addWidget(widget, r, c + 1)
            c += 2
            if c >= 6:
                c = 0
                r += 1

        add_filt("Session:", self.cmb_session)

        if key in ("daily", "date_range", "register", "fee_head", "payment_mode"):
            add_filt("Date From:", self.dt_from)
            if key != "daily":
                add_filt("Date To:", self.dt_to)

        if key in ("class_wise", "course_wise", "outstanding", "daily", "date_range", "fee_head"):
            add_filt("Course:", self.cmb_course)

        if key in ("daily", "date_range", "class_wise", "outstanding", "register"):
            add_filt("Class:", self.cmb_class)

        if key in ("daily", "date_range", "register"):
            add_filt("Payment Mode:", self.cmb_mode)

        if key in ("date_range", "fee_head"):
            add_filt("Fee Head:", self.cmb_fee_head)

        if key == "outstanding":
            add_filt("Status Filter:", self.cmb_out_filter)

        if key == "class_wise":
            add_filt("Sort By:", self.cmb_sort_by)

        if key == "ledger":
            add_filt("Student (Adm No / Name):", self.txt_student)

        # Add Generate and Reset Buttons
        self.btn_generate.show()
        self.btn_reset.show()
        self.filter_layout.addWidget(self.btn_generate, r, c)
        self.filter_layout.addWidget(self.btn_reset, r, c + 1)

    def reset_filters(self):
        self.cmb_session.setCurrentIndex(0)
        self.cmb_course.setCurrentIndex(0)
        self.cmb_class.setCurrentIndex(0)
        self.cmb_mode.setCurrentIndex(0)
        self.cmb_fee_head.setCurrentIndex(0)
        self.cmb_out_filter.setCurrentIndex(0)
        self.cmb_sort_by.setCurrentIndex(0)
        self.txt_student.clear()
        self.txt_search.clear()
        self.dt_from.setDate(QDate.currentDate())
        self.dt_to.setDate(QDate.currentDate())
        self.generate_active_report()

    # ---------------- GENERATE REPORT DISPATCHER ----------------
    def generate_active_report(self):
        key = self.active_report_key
        sess = self.cmb_session.currentData() or "All"
        crs = self.cmb_course.currentText().replace("All Courses", "All")
        cls_name = self.cmb_class.currentData() or "All"
        pmode = self.cmb_mode.currentText().replace("All Payment Modes", "All")
        fhead = self.cmb_fee_head.currentData() or "All"

        qfrom = self.dt_from.date()
        qto = self.dt_to.date()
        d_from = date(qfrom.year(), qfrom.month(), qfrom.day())
        d_to = date(qto.year(), qto.month(), qto.day())

        self.table.setSortingEnabled(False)

        if key == "daily":
            rep = ReportController.get_daily_collection_report(d_from, sess, cls_name, crs, pmode)
            self.render_daily_report(rep)
        elif key == "monthly":
            rep = ReportController.get_monthly_collection_report(d_from.year, sess, cls_name, crs, pmode)
            self.render_monthly_report(rep)
        elif key == "date_range":
            rep = ReportController.get_date_range_report(d_from, d_to, sess, cls_name, crs, pmode, fhead)
            self.render_date_range_report(rep)
        elif key == "class_wise":
            sort_val = self.cmb_sort_by.currentText()
            rep = ReportController.get_class_wise_report(sess, crs, sort_val)
            self.render_class_wise_report(rep)
        elif key == "course_wise":
            rep = ReportController.get_course_wise_report(sess)
            self.render_course_wise_report(rep)
        elif key == "outstanding":
            ofilter = self.cmb_out_filter.currentText()
            rep = ReportController.get_outstanding_report(sess, crs, cls_name, ofilter)
            self.render_outstanding_report(rep)
        elif key == "ledger":
            query = self.txt_student.text().strip() or "1"
            rep = ReportController.get_student_ledger(query)
            self.render_ledger_report(rep)
        elif key == "register":
            sq = self.txt_search.text().strip()
            rep = ReportController.get_receipt_register(d_from, d_to, sess, cls_name, pmode, sq)
            self.render_register_report(rep)
        elif key == "fee_head":
            rep = ReportController.get_fee_head_report(d_from, d_to, sess, crs)
            self.render_fee_head_report(rep)
        elif key == "payment_mode":
            rep = ReportController.get_payment_mode_report(d_from, d_to, sess)
            self.render_payment_mode_report(rep)

        self.apply_search_and_pagination()
        self.table.setSortingEnabled(True)

    # ---------------- RENDERING HELPERS ----------------
    def set_summary_cards(self, m1, m2, m3, m4, m5=None):
        self.card_1.setText(m1)
        self.card_2.setText(m2)
        self.card_3.setText(m3)
        self.card_4.setText(m4)
        if m5:
            self.card_5.setText(m5)
            self.card_5.show()
        else:
            self.card_5.hide()

    def render_daily_report(self, rep):
        headers = ["Receipt No", "Date", "Student Name", "Class", "Mode", "Subtotal", "Discount", "Fine", "Paid Amount"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["receipts"]:
            self.raw_rows.append([
                r.receipt_no,
                format_date(r.receipt_date),
                r.student.name if r.student else "N/A",
                r.student.class_name if r.student else "N/A",
                r.payment_mode or "Cash",
                f"{r.subtotal:,.2f}",
                f"{r.discount_amount:,.2f}",
                f"{r.fine_amount:,.2f}",
                format_currency(r.paid_amount or r.total_amount)
            ])

        avg_rcpt = rep["total_collection"] / rep["receipt_count"] if rep["receipt_count"] > 0 else 0.0
        self.set_summary_cards(
            f"Receipt Count: <b>{rep['receipt_count']}</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Discount: <b>{format_currency(rep['total_discount'])}</b>",
            f"Total Fine: <b>{format_currency(rep['total_fine'])}</b>",
            f"Average Receipt: <b>{format_currency(avg_rcpt)}</b>"
        )

    def render_monthly_report(self, rep):
        headers = ["Month", "Receipt Count", "Collection (₹)", "Discount (₹)", "Fine (₹)", "Net Total (₹)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["month"],
                str(r["receipt_count"]),
                f"{r['collection']:,.2f}",
                f"{r['discount']:,.2f}",
                f"{r['fine']:,.2f}",
                format_currency(r["net_total"])
            ])

        self.set_summary_cards(
            f"Year: <b>{rep['year']}</b>",
            f"Total Receipts: <b>{rep['total_receipts']}</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Discounts: <b>{format_currency(rep['total_discount'])}</b>",
            f"Total Fines: <b>{format_currency(rep['total_fine'])}</b>"
        )

    def render_date_range_report(self, rep):
        headers = ["Receipt No", "Date", "Student Name", "Class", "Payment Mode", "Subtotal", "Discount", "Fine", "Total Collected"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["receipts"]:
            self.raw_rows.append([
                r.receipt_no,
                format_date(r.receipt_date),
                r.student.name if r.student else "N/A",
                r.student.class_name if r.student else "N/A",
                r.payment_mode or "Cash",
                f"{r.subtotal:,.2f}",
                f"{r.discount_amount:,.2f}",
                f"{r.fine_amount:,.2f}",
                format_currency(r.paid_amount or r.total_amount)
            ])

        self.set_summary_cards(
            f"Total Receipts: <b>{rep['receipt_count']}</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Discount: <b>{format_currency(rep['total_discount'])}</b>",
            f"Total Fine: <b>{format_currency(rep['total_fine'])}</b>",
            f"Average Receipt: <b>{format_currency(rep['avg_receipt'])}</b>"
        )

    def render_class_wise_report(self, rep):
        headers = ["Class Name", "Students", "Receipts", "Collection (₹)", "Outstanding (₹)", "Discount (₹)", "Fine (₹)", "Grand Total (₹)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["class_name"],
                str(r["student_count"]),
                str(r["receipt_count"]),
                f"{r['collection']:,.2f}",
                f"{r['outstanding']:,.2f}",
                f"{r['discount']:,.2f}",
                f"{r['fine']:,.2f}",
                format_currency(r["grand_total"])
            ])

        self.set_summary_cards(
            f"Total Classes: <b>{rep['total_classes']}</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Outstanding: <b>{format_currency(rep['total_outstanding'])}</b>",
            f"Total Discounts: <b>{format_currency(rep['total_discount'])}</b>",
            f"Total Fines: <b>{format_currency(rep['total_fine'])}</b>"
        )

    def render_course_wise_report(self, rep):
        headers = ["Course Level", "Active Students", "Receipts", "Collection (₹)", "Outstanding Due (₹)", "Discount (₹)", "Fine (₹)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["course"],
                str(r["student_count"]),
                str(r["receipt_count"]),
                format_currency(r["collection"]),
                format_currency(r["outstanding"]),
                f"{r['discount']:,.2f}",
                f"{r['fine']:,.2f}"
            ])

        self.set_summary_cards(
            f"Courses Analyzed: <b>UG & PG</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Outstanding: <b>{format_currency(rep['total_outstanding'])}</b>",
            f"UG Collection: <b>{format_currency(next((r['collection'] for r in rep['rows'] if r['course'] == 'UG'), 0.0))}</b>",
            f"PG Collection: <b>{format_currency(next((r['collection'] for r in rep['rows'] if r['course'] == 'PG'), 0.0))}</b>"
        )

    def render_outstanding_report(self, rep):
        headers = ["Admission No", "Student Name", "Course", "Class", "Father Name", "Mobile", "Total Fee (₹)", "Paid (₹)", "Outstanding (₹)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["admission_no"],
                r["student_name"],
                r["course"],
                r["class_name"],
                r["father_name"],
                r["mobile"],
                f"{r['total_fee']:,.2f}",
                f"{r['paid_amount']:,.2f}",
                format_currency(r["outstanding"])
            ])

        self.set_summary_cards(
            f"Student Count: <b>{rep['student_count']}</b>",
            f"Total Demanded: <b>{format_currency(rep['total_demanded'])}</b>",
            f"Total Paid: <b>{format_currency(rep['total_paid'])}</b>",
            f"Total Outstanding: <b>{format_currency(rep['total_outstanding'])}</b>"
        )

    def render_ledger_report(self, rep):
        headers = ["Date", "Receipt No", "Payment Mode", "Paid Amount (₹)", "Discount (₹)", "Fine (₹)", "Running Due (₹)", "Remarks"]
        self.raw_headers = headers
        self.raw_rows = []

        if not rep.get("success"):
            self.set_summary_cards("Student: <b>Not Found</b>", "Paid: <b>₹ 0.00</b>", "Due: <b>₹ 0.00</b>", "Status: <b>Error</b>")
            return

        s = rep["student"]
        for r in rep["rows"]:
            self.raw_rows.append([
                r["date"],
                r["receipt_no"],
                r["payment_mode"],
                format_currency(r["paid_amount"]),
                f"{r['discount']:,.2f}",
                f"{r['fine']:,.2f}",
                format_currency(r["outstanding"]),
                r["remarks"]
            ])

        self.set_summary_cards(
            f"Student: <b>{s['name']} ({s['admission_no']})</b>",
            f"Class: <b>{s['class_name']} ({s['course']})</b>",
            f"Total Paid: <b>{format_currency(rep['total_paid'])}</b>",
            f"Total Discount: <b>{format_currency(rep['total_discount'])}</b>",
            f"Current Outstanding: <b>{format_currency(rep['current_due'])}</b>"
        )

    def render_register_report(self, rep):
        headers = ["Receipt No", "Date", "Student Name", "Admission No", "Course", "Class", "Amount Paid (₹)", "Mode", "Generated By"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["receipt_no"],
                r["date"],
                r["student_name"],
                r["admission_no"],
                r["course"],
                r["class_name"],
                format_currency(r["amount"]),
                r["payment_mode"],
                r["generated_by"]
            ])

        self.set_summary_cards(
            f"Register Receipts: <b>{rep['receipt_count']}</b>",
            f"Total Register Amount: <b>{format_currency(rep['total_amount'])}</b>",
            f"Date Range: <b>Active Selection</b>",
            f"Status: <b>Completed Logs</b>"
        )

    def render_fee_head_report(self, rep):
        headers = ["Fee Head Category Name", "Transactions Count", "Total Collection (₹)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["fee_head"],
                str(r["tx_count"]),
                format_currency(r["collection"])
            ])

        self.set_summary_cards(
            f"Fee Heads Recorded: <b>{rep['fee_head_count']}</b>",
            f"Total Fee Head Revenue: <b>{format_currency(rep['total_collection'])}</b>",
            f"Top Category: <b>{rep['rows'][0]['fee_head'] if rep['rows'] else 'N/A'}</b>",
            f"Status: <b>Active Category Aggregation</b>"
        )

    def render_payment_mode_report(self, rep):
        headers = ["Payment Method", "Transaction Count", "Total Collection (₹)", "Percentage (%)"]
        self.raw_headers = headers
        self.raw_rows = []
        for r in rep["rows"]:
            self.raw_rows.append([
                r["payment_mode"],
                str(r["tx_count"]),
                format_currency(r["collection"]),
                f"{r['percentage']}%"
            ])

        top_mode = max(rep["rows"], key=lambda x: x["collection"]) if rep["rows"] else {"payment_mode": "N/A"}
        self.set_summary_cards(
            f"Payment Modes: <b>{len(rep['rows'])} Methods</b>",
            f"Total Collection: <b>{format_currency(rep['total_collection'])}</b>",
            f"Total Transactions: <b>{rep['total_transactions']}</b>",
            f"Top Method: <b>{top_mode['payment_mode']}</b>"
        )

    # ---------------- PAGINATION & SEARCH ----------------
    def apply_search_and_pagination(self):
        query = self.txt_search.text().strip().lower()
        if query:
            self.filtered_rows = [
                row for row in self.raw_rows
                if any(query in str(cell).lower() for cell in row)
            ]
        else:
            self.filtered_rows = list(self.raw_rows)

        # Pagination calculations
        ps_str = self.cmb_page_size.currentText()
        if ps_str == "All":
            self.page_size = len(self.filtered_rows) if self.filtered_rows else 1
        else:
            self.page_size = int(ps_str)

        total_records = len(self.filtered_rows)
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)

        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        visible_rows = self.filtered_rows[start_idx:end_idx]

        # Render Table
        self.table.clear()
        self.table.setColumnCount(len(self.raw_headers))
        self.table.setHorizontalHeaderLabels(self.raw_headers)
        self.table.setRowCount(len(visible_rows))

        for r_idx, row in enumerate(visible_rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if c_idx in (len(row)-1, len(row)-2) and "₹" in str(val):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r_idx, c_idx, item)

        self.table.resizeColumnsToContents()
        self.lbl_page_info.setText(f"Page {self.current_page} of {total_pages} (Total: {total_records})")

        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)
        self.btn_last.setEnabled(self.current_page < total_pages)

    def on_page_size_changed(self):
        self.current_page = 1
        self.apply_search_and_pagination()

    def go_to_page(self, page_num: int):
        self.current_page = page_num
        self.apply_search_and_pagination()

    # ---------------- EXPORT & PRINT METHODS ----------------
    def get_export_data(self):
        """Returns title, headers, and filtered rows currently displayed/filtered."""
        title = self.lbl_header_title.text().replace("📅 ", "").replace("🗓 ", "").replace("📆 ", "").replace("🏫 ", "").replace("🎓 ", "").replace("⚠️ ", "").replace("📖 ", "").replace("📜 ", "").replace("🏷 ", "").replace("💳 ", "")
        return title, self.raw_headers, self.filtered_rows

    def export_csv(self):
        title, headers, rows = self.get_export_data()
        if not rows:
            QMessageBox.warning(self, "No Data", "There are no rows to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, f"Save {title} CSV", "", "CSV Files (*.csv)")
        if path:
            success, msg = ExportService.export_to_csv(headers, rows, filename_prefix=title.replace(" ", "_"), output_path=path)
            if success:
                QMessageBox.information(self, "Export Successful", f"Report exported to CSV:\n{msg}")
            else:
                QMessageBox.critical(self, "Export Failed", msg)

    def export_excel(self):
        title, headers, rows = self.get_export_data()
        if not rows:
            QMessageBox.warning(self, "No Data", "There are no rows to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, f"Save {title} Excel", "", "Excel Files (*.xlsx)")
        if path:
            success, msg = ExportService.export_to_excel(headers, rows, filename_prefix=title.replace(" ", "_"), output_path=path)
            if success:
                QMessageBox.information(self, "Export Successful", f"Report exported to Excel:\n{msg}")
            else:
                QMessageBox.critical(self, "Export Failed", msg)

    def export_pdf(self):
        title, headers, rows = self.get_export_data()
        if not rows:
            QMessageBox.warning(self, "No Data", "There are no rows to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, f"Save {title} PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf_path = PDFService.generate_report_pdf(title=title, headers=headers, rows=rows, output_path=path)
            QMessageBox.information(self, "Export Successful", f"Report PDF saved to:\n{pdf_path}")
            PrintService.preview_pdf(pdf_path, self)

    def print_report(self):
        title, headers, rows = self.get_export_data()
        if not rows:
            QMessageBox.warning(self, "No Data", "There are no rows to print.")
            return

        pdf_path = PDFService.generate_report_pdf(title=title, headers=headers, rows=rows)
        PrintService.preview_pdf(pdf_path, self)
