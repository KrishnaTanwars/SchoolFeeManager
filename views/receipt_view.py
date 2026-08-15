"""
Fee Collection & Receipt Generation Form View with Instant Non-Focus-Stealing Autocomplete,
Right-Side Student Search Sidebar, Left-Side Fee Particulars & Payment Details,
Course-Based Fee Head Filtering, Zero-Clipping Panels, and Real-Time Calculation Engine.
"""

from typing import Dict, List, Optional
from datetime import date, datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QCheckBox, QTextEdit, QListWidget,
    QListWidgetItem, QFrame, QDateEdit, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QPoint, QEvent
from PySide6.QtGui import QKeySequence, QFont, QColor, QShortcut
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from controllers.settings_controller import SettingsController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from utils.helpers import format_currency, format_date
from utils.number_to_words import number_to_words_indian
from utils.table_delegate import apply_responsive_table_formatting

COMMON_INDIAN_BANKS = [
    "State Bank of India (SBI)",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Punjab National Bank (PNB)",
    "Bank of Baroda",
    "Kotak Mahindra Bank",
    "Canara Bank",
    "Union Bank of India",
    "IDFC FIRST Bank",
    "IndusInd Bank",
    "Bank of Maharashtra",
    "Central Bank of India",
    "Other Bank"
]

class StudentSearchPopup(QListWidget):
    """Floating non-activating popup list widget for instant student search autocomplete."""
    def __init__(self, parent_input: QLineEdit, parent_view=None):
        super().__init__(parent_view)
        self.parent_input = parent_input
        self.parent_view = parent_view

        # Qt.ToolTip prevents active window activation and focus stealing on Windows/Qt!
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setStyleSheet("""
            QListWidget {
                border: 2px solid #2563eb;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 12px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }
            QListWidget::item:hover {
                background-color: #f0f9ff;
                color: #0284c7;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
                font-weight: bold;
            }
        """)
        self.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item: QListWidgetItem):
        if self.parent_view and hasattr(self.parent_view, "select_student_from_item"):
            self.parent_view.select_student_from_item(item)
        self.hide()


class SearchLineEdit(QLineEdit):
    """Custom LineEdit to intercept Up/Down/Enter/Escape for Autocomplete Navigation while keeping focus."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view_ref = None

    def keyPressEvent(self, event):
        if self.view_ref and hasattr(self.view_ref, "handle_search_key_event"):
            if self.view_ref.handle_search_key_event(event):
                return
        super().keyPressEvent(event)


class ReceiptView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_student = None
        self._user_edited_paid = False
        self.current_course_filter = "All"
        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 10, 12, 10)

        # ---------------- TOP HEADER ----------------
        hdr = QHBoxLayout()
        title_lbl = QLabel("Fee Collection & Receipt Generation")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a8a;")
        hdr.addWidget(title_lbl)

        hdr.addStretch()

        self.lbl_next_rec = QLabel("Next Receipt No: <b>Auto</b>")
        self.lbl_next_rec.setStyleSheet("font-size: 13px; color: #334155; background: #f1f5f9; padding: 4px 10px; border-radius: 4px;")
        hdr.addWidget(self.lbl_next_rec)

        main_layout.addLayout(hdr)

        # =========================================================================
        # MAIN 2-COLUMN CONTENT LAYOUT
        # =========================================================================
        main_content = QHBoxLayout()
        main_content.setSpacing(12)

        # =========================================================================
        # LEFT COLUMN (65% Width): Full Height Fee Particulars Table
        # =========================================================================
        fee_box = QGroupBox("1. Fee Heads Particulars")
        fee_box.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        fee_layout = QVBoxLayout(fee_box)
        fee_layout.setContentsMargins(10, 10, 10, 10)
        fee_layout.setSpacing(8)

        # Top Bar above Fee Table
        fee_top_bar = QHBoxLayout()
        self.lbl_course_badge = QLabel("Fee Heads Filter: <b>ALL</b>")
        self.lbl_course_badge.setStyleSheet("font-size: 12px; color: #2563eb; background: #eff6ff; padding: 3px 8px; border-radius: 4px;")
        fee_top_bar.addWidget(self.lbl_course_badge)
        
        fee_top_bar.addStretch()

        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.setFixedHeight(26)
        self.btn_select_all.setToolTip("Check all fee heads")
        self.btn_select_all.setStyleSheet("padding: 2px 10px; font-size: 11px;")
        self.btn_select_all.clicked.connect(self.select_all_fees)

        self.btn_deselect_all = QPushButton("Deselect All")
        self.btn_deselect_all.setFixedHeight(26)
        self.btn_deselect_all.setToolTip("Uncheck all fee heads")
        self.btn_deselect_all.setStyleSheet("padding: 2px 10px; font-size: 11px;")
        self.btn_deselect_all.clicked.connect(self.deselect_all_fees)

        fee_top_bar.addWidget(self.btn_select_all)
        fee_top_bar.addWidget(self.btn_deselect_all)
        fee_layout.addLayout(fee_top_bar)

        # Fee Particulars Table with Intelligent Auto Column Width Calculation
        self.table_fees = QTableWidget()
        self.table_fees.setColumnCount(4)
        self.table_fees.setHorizontalHeaderLabels(["Select", "Fee Head Description", "Course", "Amount (₹)"])
        self.table_fees.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_fees.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_fees.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_fees.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        apply_responsive_table_formatting(self.table_fees)

        # Stretch table vertically to consume entire left column
        fee_layout.addWidget(self.table_fees, stretch=1)
        main_content.addWidget(fee_box, stretch=65)

        # =========================================================================
        # RIGHT COLUMN (35% Width): Split Vertically into Top & Bottom Panels
        # =========================================================================
        right_column_layout = QVBoxLayout()
        right_column_layout.setSpacing(10)

        # TOP RIGHT PANEL (55% Height): Student Search & Profile Summary
        student_box = QGroupBox("2. Student Search & Profile Summary")
        student_box.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        student_layout = QVBoxLayout(student_box)
        student_layout.setSpacing(8)
        student_layout.setContentsMargins(10, 10, 10, 10)

        lbl_search_title = QLabel("Search Student (Name / Adm No / Father / Mobile):")
        lbl_search_title.setStyleSheet("font-weight: 600; color: #334155; font-size: 12px;")
        student_layout.addWidget(lbl_search_title)

        # Custom Search LineEdit
        search_row = QHBoxLayout()
        search_row.setSpacing(6)

        self.txt_student_search = SearchLineEdit()
        self.txt_student_search.view_ref = self
        self.txt_student_search.setPlaceholderText("Type student name, adm no, father, mobile... (Alt+S)")
        self.txt_student_search.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding: 5px 8px;
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                background-color: #ffffff;
                height: 28px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
                background-color: #f8fafc;
            }
        """)
        self.txt_student_search.textChanged.connect(self.on_search_text_changed)

        self.btn_clear_search = QPushButton("Clear")
        self.btn_clear_search.setFixedHeight(30)
        self.btn_clear_search.setToolTip("Clear search and reset student selection (Esc)")
        self.btn_clear_search.setStyleSheet("padding: 4px 10px; font-weight: bold; font-size: 12px;")
        self.btn_clear_search.clicked.connect(self.clear_student_card)

        search_row.addWidget(self.txt_student_search, stretch=1)
        search_row.addWidget(self.btn_clear_search)
        student_layout.addLayout(search_row)

        # Autocomplete Suggestions Popup List Widget
        self.popup_suggestions = StudentSearchPopup(self.txt_student_search, self)
        self.popup_suggestions.hide()

        # Student Details Card (Zero-Clipping Responsive Layout filling Full Top Panel)
        self.card_student = QGroupBox("Selected Student Summary")
        self.card_student.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 6px;
                background-color: #f8fafc;
            }
        """)
        card_form = QFormLayout(self.card_student)
        card_form.setContentsMargins(8, 6, 8, 6)
        card_form.setSpacing(4)

        self.lbl_adm_no = QLabel("-")
        self.lbl_name = QLabel("-")
        self.lbl_course = QLabel("-")
        self.lbl_yr_sem = QLabel("-")
        self.lbl_father = QLabel("-")
        self.lbl_mobile = QLabel("-")
        self.lbl_session = QLabel("-")
        self.lbl_status = QLabel("-")
        self.lbl_total_paid = QLabel("₹ 0.00")
        self.lbl_total_paid.setStyleSheet("font-weight: bold; color: #059669; font-size: 12px;")
        self.lbl_prev_due = QLabel("₹ 0.00")
        self.lbl_prev_due.setStyleSheet("font-weight: bold; color: #dc2626; font-size: 12px;")

        for lbl in [self.lbl_adm_no, self.lbl_name, self.lbl_course, self.lbl_yr_sem, self.lbl_father, self.lbl_mobile, self.lbl_session, self.lbl_status]:
            lbl.setStyleSheet("font-weight: bold; color: #0f172a; font-size: 12px;")
            lbl.setWordWrap(True)

        card_form.addRow("Admission No:", self.lbl_adm_no)
        card_form.addRow("Student Name:", self.lbl_name)
        card_form.addRow("Course / Branch:", self.lbl_course)
        card_form.addRow("Year & Semester:", self.lbl_yr_sem)
        card_form.addRow("Father's Name:", self.lbl_father)
        card_form.addRow("Mobile No:", self.lbl_mobile)
        card_form.addRow("Session:", self.lbl_session)
        card_form.addRow("Status:", self.lbl_status)
        card_form.addRow("Total Paid:", self.lbl_total_paid)
        card_form.addRow("Outstanding Due:", self.lbl_prev_due)

        student_layout.addWidget(self.card_student, stretch=1)
        right_column_layout.addWidget(student_box, stretch=55)

        # BOTTOM RIGHT PANEL (45% Height): Side-by-Side Calculation & Payment Details
        bottom_right_widget = QWidget()
        bottom_right_layout = QHBoxLayout(bottom_right_widget)
        bottom_right_layout.setContentsMargins(0, 0, 0, 0)
        bottom_right_layout.setSpacing(8)

        # Bottom Sub-Panel 1: Real-Time Calculation Summary
        totals_group = QGroupBox("3. Calculation Summary")
        totals_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        totals_form = QFormLayout(totals_group)
        totals_form.setContentsMargins(8, 8, 8, 8)
        totals_form.setSpacing(4)
        totals_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.lbl_subtotal = QLabel("₹ 0.00")
        self.lbl_subtotal.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b;")
        totals_form.addRow("Subtotal:", self.lbl_subtotal)

        self.spn_discount = QDoubleSpinBox()
        self.spn_discount.setRange(0.0, 1000000.0)
        self.spn_discount.setPrefix("₹ ")
        self.spn_discount.setDecimals(2)
        self.spn_discount.setStyleSheet("font-size: 12px; font-weight: bold; padding: 2px 4px;")
        self.spn_discount.valueChanged.connect(self.recalculate_totals)
        totals_form.addRow("Discount (-):", self.spn_discount)

        self.spn_fine = QDoubleSpinBox()
        self.spn_fine.setRange(0.0, 500000.0)
        self.spn_fine.setPrefix("₹ ")
        self.spn_fine.setDecimals(2)
        self.spn_fine.setStyleSheet("font-size: 12px; font-weight: bold; padding: 2px 4px;")
        self.spn_fine.valueChanged.connect(self.recalculate_totals)
        totals_form.addRow("Fine (+):", self.spn_fine)

        self.lbl_total = QLabel("₹ 0.00")
        self.lbl_total.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e3a8a;")
        totals_form.addRow("Total Payable:", self.lbl_total)

        self.spn_paid_amount = QDoubleSpinBox()
        self.spn_paid_amount.setRange(0.0, 5000000.0)
        self.spn_paid_amount.setPrefix("₹ ")
        self.spn_paid_amount.setDecimals(2)
        self.spn_paid_amount.setStyleSheet("font-size: 12px; font-weight: bold; color: #059669; padding: 2px 4px;")
        self.spn_paid_amount.valueChanged.connect(self.on_paid_amount_edited)
        totals_form.addRow("<b>ACTUAL PAID:</b>", self.spn_paid_amount)

        self.lbl_due_amount = QLabel("₹ 0.00")
        self.lbl_due_amount.setStyleSheet("font-size: 12px; font-weight: bold; color: #dc2626;")
        totals_form.addRow("<b>Remaining Due:</b>", self.lbl_due_amount)

        self.lbl_words = QLabel("Zero Rupees Only")
        self.lbl_words.setStyleSheet("font-size: 10px; font-weight: bold; color: #475569; font-style: italic;")
        self.lbl_words.setWordWrap(True)
        totals_form.addRow("In Words:", self.lbl_words)

        bottom_right_layout.addWidget(totals_group, stretch=1)

        # Bottom Sub-Panel 2: Payment Details & Actions (Expanding Bank Combo)
        pay_group = QGroupBox("4. Payment Details & Actions")
        pay_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        pay_box = QVBoxLayout(pay_group)
        pay_box.setContentsMargins(8, 8, 8, 8)
        pay_box.setSpacing(4)

        pay_form = QFormLayout()
        pay_form.setContentsMargins(0, 0, 0, 0)
        pay_form.setSpacing(4)
        pay_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                font-size: 11px;
                padding: 2px 4px;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: #ffffff;
                height: 24px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #2563eb;
                background-color: #f8fafc;
            }
        """
        pay_group.setStyleSheet(field_style)

        self.cmb_pay_mode = QComboBox()
        self.cmb_pay_mode.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmb_pay_mode.addItems(["Cash", "UPI / QR", "Cheque", "Demand Draft (DD)", "Net Banking / NEFT", "Card"])
        self.cmb_pay_mode.currentIndexChanged.connect(self.update_payment_mode_fields)
        pay_form.addRow("Mode:", self.cmb_pay_mode)

        self.txt_utr_no = QLineEdit()
        self.txt_utr_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.txt_utr_no.setPlaceholderText("12-digit UTR / Txn No")
        self.lbl_utr_no = QLabel("UTR / Txn:")

        self.txt_cheque_no = QLineEdit()
        self.txt_cheque_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.txt_cheque_no.setPlaceholderText("6-digit Cheque / DD No")
        self.lbl_cheque_no = QLabel("Cheque / DD:")

        self.dt_cheque_date = QDateEdit()
        self.dt_cheque_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dt_cheque_date.setCalendarPopup(True)
        self.dt_cheque_date.setDate(QDate.currentDate())
        self.lbl_cheque_date = QLabel("Cheque Date:")

        self.cmb_bank_name = QComboBox()
        self.cmb_bank_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmb_bank_name.setEditable(True)
        self.cmb_bank_name.addItems(COMMON_INDIAN_BANKS)
        self.cmb_bank_name.view().setMinimumWidth(260)
        self.lbl_bank_name = QLabel("Bank Name:")

        self.dt_payment_date = QDateEdit()
        self.dt_payment_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dt_payment_date.setCalendarPopup(True)
        self.dt_payment_date.setDate(QDate.currentDate())
        self.lbl_payment_date = QLabel("Payment Date:")

        self.txt_ref_no = QLineEdit()
        self.txt_ref_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.txt_ref_no.setPlaceholderText("Optional reference no")
        self.lbl_ref_no = QLabel("Ref No:")

        pay_form.addRow(self.lbl_utr_no, self.txt_utr_no)
        pay_form.addRow(self.lbl_cheque_no, self.txt_cheque_no)
        pay_form.addRow(self.lbl_cheque_date, self.dt_cheque_date)
        pay_form.addRow(self.lbl_bank_name, self.cmb_bank_name)
        pay_form.addRow(self.lbl_payment_date, self.dt_payment_date)
        pay_form.addRow(self.lbl_ref_no, self.txt_ref_no)

        self.txt_remarks = QLineEdit()
        self.txt_remarks.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.txt_remarks.setPlaceholderText("Optional fee remarks/notes")
        pay_form.addRow("Remarks:", self.txt_remarks)

        pay_box.addLayout(pay_form)

        self.btn_generate = QPushButton("GENERATE & PRINT RECEIPT")
        self.btn_generate.setFixedHeight(36)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #059669;
                color: #ffffff;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
            QPushButton:pressed {
                background-color: #065f46;
            }
        """)
        self.btn_generate.clicked.connect(self.generate_receipt)

        pay_box.addWidget(self.btn_generate)

        bottom_right_layout.addWidget(pay_group, stretch=1)

        right_column_layout.addWidget(bottom_right_widget, stretch=45)

        main_content.addLayout(right_column_layout, stretch=35)
        main_layout.addLayout(main_content, stretch=1)

        scroll.setWidget(container)
        main_vbox.addWidget(scroll)

        self.update_payment_mode_fields()
        self.refresh_view()

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for high-speed ERP operation."""
        # Alt+S to focus Student Search Box
        self.shortcut_search = QShortcut(QKeySequence("Alt+S"), self)
        self.shortcut_search.activated.connect(self.focus_search_box)

        # Ctrl+S to Generate Receipt
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.generate_receipt)

    def focus_search_box(self):
        self.txt_student_search.setFocus(Qt.OtherFocusReason)
        self.txt_student_search.selectAll()

    # ---------------- INSTANT NON-FOCUS-STEALING AUTOCOMPLETE SEARCH LOGIC ----------------
    def on_search_text_changed(self, text: str):
        query = text.strip()
        if not query:
            self.popup_suggestions.hide()
            return

        students = StudentController.get_all_students(search_query=query, status_filter="Active")
        self.popup_suggestions.clear()

        if not students:
            item = QListWidgetItem("No active student matches search")
            item.setFlags(Qt.NoItemFlags)
            self.popup_suggestions.addItem(item)
        else:
            for s in students:
                crs_br = f"{s.course or 'UG'}" + (f" ({s.branch})" if getattr(s, "branch", None) else "")
                yr_sem = f"{s.year or ''} - {s.semester or ''}".strip(" -") or "N/A"
                disp = f"{s.admission_no}  |  {s.name}  |  {crs_br}  |  {yr_sem}  |  Father: {s.father_name}"
                item = QListWidgetItem(disp)
                item.setData(Qt.UserRole, s)
                self.popup_suggestions.addItem(item)

        # Show & Position popup suggestion list directly below search box with exact matching width
        input_pos = self.txt_student_search.mapToGlobal(QPoint(0, self.txt_student_search.height()))
        exact_width = max(self.txt_student_search.width(), 450)
        item_count = len(students) if students else 1
        
        # Enforce minimum height 72px for single result to prevent text clipping
        max_height = 72 if item_count == 1 else min(240, max(72, item_count * 38 + 12))

        self.popup_suggestions.setGeometry(input_pos.x(), input_pos.y(), exact_width, max_height)
        self.popup_suggestions.show()

        # Explicitly keep active keyboard focus inside search input box
        self.txt_student_search.setFocus(Qt.OtherFocusReason)

    def handle_search_key_event(self, event) -> bool:
        """Handles arrow keys, enter, and escape inside search line edit without stealing focus."""
        if not self.popup_suggestions.isVisible():
            return False

        key = event.key()

        if key == Qt.Key_Down:
            curr = self.popup_suggestions.currentRow()
            if curr < self.popup_suggestions.count() - 1:
                self.popup_suggestions.setCurrentRow(curr + 1)
            elif curr == -1 and self.popup_suggestions.count() > 0:
                self.popup_suggestions.setCurrentRow(0)
            return True

        elif key == Qt.Key_Up:
            curr = self.popup_suggestions.currentRow()
            if curr > 0:
                self.popup_suggestions.setCurrentRow(curr - 1)
            return True

        elif key in (Qt.Key_Return, Qt.Key_Enter):
            curr_row = self.popup_suggestions.currentRow()
            item = self.popup_suggestions.item(curr_row) if curr_row >= 0 else self.popup_suggestions.item(0)
            if item and item.flags() & Qt.ItemIsSelectable:
                self.select_student_from_item(item)
                self.popup_suggestions.hide()
                return True

        elif key == Qt.Key_Escape:
            self.popup_suggestions.hide()
            return True

        return False

    def select_student_from_item(self, item: QListWidgetItem):
        student = item.data(Qt.UserRole)
        if student:
            self.selected_student = student
            self.txt_student_search.blockSignals(True)
            self.txt_student_search.setText(f"{student.name} ({student.admission_no})")
            self.txt_student_search.blockSignals(False)
            self.update_student_card(student)
            self.popup_suggestions.hide()

    def update_student_card(self, s):
        self.lbl_adm_no.setText(s.admission_no)
        self.lbl_name.setText(s.name)
        crs_br = f"{s.course or 'UG'}" + (f" ({s.branch})" if getattr(s, "branch", None) else "")
        self.lbl_course.setText(crs_br)
        yr_sem = f"{s.year or ''} - {s.semester or ''}".strip(" -") or "N/A"
        self.lbl_yr_sem.setText(yr_sem)
        self.lbl_father.setText(s.father_name)
        self.lbl_mobile.setText(s.mobile)
        self.lbl_session.setText(s.academic_session)
        self.lbl_status.setText(s.status)

        if s.status == "Active":
            self.lbl_status.setStyleSheet("font-weight: bold; color: #059669;")
        else:
            self.lbl_status.setStyleSheet("font-weight: bold; color: #dc2626;")

        # Query student fee summary
        summary = ReceiptController.get_student_fee_summary(s.id)
        self.lbl_total_paid.setText(format_currency(summary['total_paid']))
        self.lbl_prev_due.setText(format_currency(summary['latest_due']))

        # Auto filter Fee Heads by Student's Course
        self.load_fee_heads_for_student(s)

    def clear_student_card(self):
        self.selected_student = None
        self.txt_student_search.blockSignals(True)
        self.txt_student_search.clear()
        self.txt_student_search.blockSignals(False)
        self.popup_suggestions.hide()

        self.lbl_adm_no.setText("-")
        self.lbl_name.setText("-")
        self.lbl_course.setText("-")
        self.lbl_class.setText("-")
        self.lbl_father.setText("-")
        self.lbl_mobile.setText("-")
        self.lbl_session.setText("-")
        self.lbl_status.setText("-")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #0f172a;")
        self.lbl_total_paid.setText("₹ 0.00")
        self.lbl_prev_due.setText("₹ 0.00")

        self.current_course_filter = "All"
        self.lbl_course_badge.setText("Fee Heads Filter: <b>ALL</b>")
        self.load_fee_heads()

    # ---------------- COURSE & SEMESTER BASED FEE HEAD FILTERING ----------------
    def load_fee_heads_for_student(self, student):
        st_course = str(student.course or "").strip()
        st_sem = str(getattr(student, "semester", "") or "").strip()
        badge_text = st_course if st_course else "All"
        if st_sem:
            badge_text += f" ({st_sem})"
        self.lbl_course_badge.setText(f"Fee Heads Filter: <b>{badge_text}</b>")
        self.load_fee_heads()

    def load_fee_heads(self):
        if self.selected_student:
            categories = FeeController.get_applicable_categories(self.selected_student)
        else:
            categories = FeeController.get_all_categories(active_only=True, course_filter=self.current_course_filter)
        
        self.table_fees.setRowCount(len(categories))

        for row_idx, cat in enumerate(categories):
            chk = QCheckBox()
            chk.setChecked(True)
            chk.stateChanged.connect(self.recalculate_totals)
            chk.setProperty("cat_data", cat)

            self.table_fees.setCellWidget(row_idx, 0, chk)

            lbl_name = QTableWidgetItem(cat.name)
            lbl_name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_fees.setItem(row_idx, 1, lbl_name)

            lbl_crs = QTableWidgetItem(getattr(cat, "course", "UG"))
            lbl_crs.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_fees.setItem(row_idx, 2, lbl_crs)

            spn_amt = QDoubleSpinBox()
            spn_amt.setRange(0.0, 5000000.0)
            spn_amt.setValue(cat.default_amount)
            spn_amt.setPrefix("₹ ")
            spn_amt.setDecimals(2)
            spn_amt.setStyleSheet("""
                QDoubleSpinBox {
                    font-size: 12px;
                    font-weight: bold;
                    padding: 2px 4px;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    color: #0f172a;
                }
            """)
            spn_amt.valueChanged.connect(self.recalculate_totals)

            self.table_fees.setCellWidget(row_idx, 3, spn_amt)

        self._user_edited_paid = False
        self.recalculate_totals()
        self.auto_fit_columns()

    def auto_fit_columns(self):
        """
        Intelligent Auto Column Width Calculation for Fee Heads Particulars Table.
        Calculates exact width for each column: MAX(Header Width, Longest Cell Width) + 20px Padding.
        Does NOT stretch columns or distribute unallocated empty space.
        """
        font_metrics = self.table_fees.fontMetrics()
        header_font_metrics = self.table_fees.horizontalHeader().fontMetrics()
        padding = 22  # Consistent padding (15-25px range)

        for col in (0, 2, 3):
            # 1. Width of Column Header
            header_item = self.table_fees.horizontalHeaderItem(col)
            header_text = header_item.text() if header_item else ""
            header_w = header_font_metrics.horizontalAdvance(header_text)

            # 2. Width of Longest Cell Value in the Entire Column
            max_cell_w = 0
            for row in range(self.table_fees.rowCount()):
                cell_widget = self.table_fees.cellWidget(row, col)
                if cell_widget:
                    if isinstance(cell_widget, QCheckBox):
                        cell_w = 24
                    elif isinstance(cell_widget, QDoubleSpinBox):
                        val_str = f"₹ {cell_widget.value():,.2f}"
                        cell_w = font_metrics.horizontalAdvance(val_str) + 40
                    else:
                        cell_w = cell_widget.sizeHint().width()
                else:
                    item = self.table_fees.item(row, col)
                    txt = item.text() if item else ""
                    cell_w = font_metrics.horizontalAdvance(txt)

                if cell_w > max_cell_w:
                    max_cell_w = cell_w

            # Final Column Width = MAX(Header Width, Longest Cell Width) + Padding
            final_width = max(header_w, max_cell_w) + padding

            # Enforce minimum bounds for columns
            if col == 0:
                final_width = max(final_width, 55)
            elif col == 2:
                final_width = max(final_width, 75)
            elif col == 3:
                final_width = max(final_width, 165)

            self.table_fees.setColumnWidth(col, final_width)

    def select_all_fees(self):
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            if chk:
                chk.setChecked(True)

    def deselect_all_fees(self):
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            if chk:
                chk.setChecked(False)

    # ---------------- REAL-TIME CALCULATIONS ----------------
    def on_paid_amount_edited(self):
        self._user_edited_paid = True
        self.calculate_due()

    def calculate_due(self):
        subtotal = 0.0
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                subtotal += spn_amt.value()

        discount = self.spn_discount.value()
        fine = self.spn_fine.value()
        grand_total = max(0.0, subtotal - discount + fine)

        paid_val = self.spn_paid_amount.value()
        due_val = max(0.0, grand_total - paid_val)

        self.lbl_due_amount.setText(format_currency(due_val))
        self.lbl_words.setText(number_to_words_indian(paid_val))

    def recalculate_totals(self):
        subtotal = 0.0
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                subtotal += spn_amt.value()

        discount = self.spn_discount.value()
        fine = self.spn_fine.value()
        grand_total = max(0.0, subtotal - discount + fine)

        self.lbl_subtotal.setText(format_currency(subtotal))
        self.lbl_total.setText(format_currency(grand_total))

        if not self._user_edited_paid:
            self.spn_paid_amount.blockSignals(True)
            self.spn_paid_amount.setValue(grand_total)
            self.spn_paid_amount.blockSignals(False)

        self.calculate_due()

    # ---------------- DYNAMIC PAYMENT MODE FIELDS ----------------
    def update_payment_mode_fields(self):
        mode = self.cmb_pay_mode.currentText().upper()

        self.lbl_utr_no.hide()
        self.txt_utr_no.hide()
        self.lbl_cheque_no.hide()
        self.txt_cheque_no.hide()
        self.lbl_cheque_date.hide()
        self.dt_cheque_date.hide()
        self.lbl_bank_name.hide()
        self.cmb_bank_name.hide()
        self.lbl_payment_date.hide()
        self.dt_payment_date.hide()
        self.lbl_ref_no.hide()
        self.txt_ref_no.hide()

        if "CASH" in mode:
            self.lbl_payment_date.show()
            self.dt_payment_date.show()
        elif "UPI" in mode or "QR" in mode:
            self.lbl_utr_no.setText("UTR Number:")
            self.txt_utr_no.setPlaceholderText("12-digit UPI UTR / Txn No")
            self.lbl_utr_no.show()
            self.txt_utr_no.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
            self.lbl_payment_date.show()
            self.dt_payment_date.show()
        elif "CHEQUE" in mode or "DD" in mode or "DEMAND" in mode:
            if "DEMAND" in mode or "DD" in mode:
                self.lbl_cheque_no.setText("DD Number:")
                self.txt_cheque_no.setPlaceholderText("6-digit DD Number")
                self.lbl_cheque_date.setText("DD Date:")
            else:
                self.lbl_cheque_no.setText("Cheque Number:")
                self.txt_cheque_no.setPlaceholderText("6-digit Cheque Number")
                self.lbl_cheque_date.setText("Cheque Date:")
            self.lbl_cheque_no.show()
            self.txt_cheque_no.show()
            self.lbl_cheque_date.show()
            self.dt_cheque_date.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
        elif "NET" in mode or "NEFT" in mode or "CARD" in mode:
            self.lbl_utr_no.setText("Txn Number:")
            self.txt_utr_no.setPlaceholderText("Txn / Reference Number")
            self.lbl_utr_no.show()
            self.txt_utr_no.show()
            self.lbl_bank_name.show()
            self.cmb_bank_name.show()
            self.lbl_payment_date.show()
            self.dt_payment_date.show()
        else:
            self.lbl_ref_no.show()
            self.txt_ref_no.show()
            self.lbl_payment_date.show()
            self.dt_payment_date.show()

    def refresh_view(self):
        self.lbl_next_rec.setText(f"Next Receipt No: <b>{ReceiptController.generate_next_receipt_number()}</b>")
        if not self.selected_student:
            self.load_fee_heads()
        else:
            self.auto_fit_columns()

    # ---------------- RECEIPT GENERATION & VALIDATION ----------------
    def generate_receipt(self):
        if not self.selected_student:
            QMessageBox.warning(self, "Validation Error", "Please search and select a student first.")
            self.txt_student_search.setFocus()
            return

        selected_items = []
        for r in range(self.table_fees.rowCount()):
            chk = self.table_fees.cellWidget(r, 0)
            spn_amt = self.table_fees.cellWidget(r, 3)
            if chk and chk.isChecked() and spn_amt:
                cat = chk.property("cat_data")
                if spn_amt.value() <= 0:
                    QMessageBox.warning(self, "Validation Error", f"Fee head '{cat.name}' amount must be greater than zero.")
                    return
                selected_items.append({
                    "fee_category_id": cat.id,
                    "category_name": cat.name,
                    "amount": spn_amt.value()
                })

        if not selected_items:
            QMessageBox.warning(self, "Validation Error", "Please select at least one fee head.")
            return

        if self.spn_discount.value() < 0 or self.spn_fine.value() < 0 or self.spn_paid_amount.value() < 0:
            QMessageBox.warning(self, "Validation Error", "Discount, Fine, and Paid Amount cannot be negative.")
            return

        from services.session_service import session_manager
        current_session = session_manager.get_active_session()

        q_cq_date = self.dt_cheque_date.date()
        cq_date = date(q_cq_date.year(), q_cq_date.month(), q_cq_date.day())

        q_pay_date = self.dt_payment_date.date()
        pay_date = date(q_pay_date.year(), q_pay_date.month(), q_pay_date.day())

        success, msg, receipt = ReceiptController.create_receipt(
            student_id=self.selected_student.id,
            academic_session=current_session,
            items=selected_items,
            discount_amount=self.spn_discount.value(),
            fine_amount=self.spn_fine.value(),
            payment_mode=self.cmb_pay_mode.currentText(),
            reference_no=self.txt_ref_no.text().strip(),
            remarks=self.txt_remarks.text().strip(),
            paid_amount=self.spn_paid_amount.value(),
            utr_number=self.txt_utr_no.text().strip(),
            cheque_number=self.txt_cheque_no.text().strip(),
            cheque_date=cq_date,
            bank_name=self.cmb_bank_name.currentText().strip(),
            payment_date=pay_date
        )

        if success and receipt:
            try:
                # Re-query fresh eager-loaded receipt to prevent DetachedInstanceError or lazy load failures
                fresh_receipt = ReceiptController.get_receipt_by_id(receipt.id) or receipt

                # Pre-generate PDF file
                from services.pdf_service import PDFService
                pdf_path = PDFService.generate_receipt_pdf(fresh_receipt)

                QMessageBox.information(self, "Success", f"Receipt {fresh_receipt.receipt_no} generated successfully!")

                # Reset fields
                self.spn_discount.setValue(0.0)
                self.spn_fine.setValue(0.0)
                self.txt_utr_no.clear()
                self.txt_cheque_no.clear()
                self.txt_ref_no.clear()
                self.txt_remarks.clear()
                self._user_edited_paid = False
                self.clear_student_card()
                self.refresh_view()

                # Open Print Preview Dialog
                dlg = ReceiptPreviewDialog(self, receipt=fresh_receipt, pdf_path=pdf_path)
                dlg.exec()
            except Exception as preview_err:
                from utils.logger import logger
                logger.error(f"Error opening receipt preview: {preview_err}", exc_info=True)
                QMessageBox.information(self, "Success", f"Receipt {receipt.receipt_no} generated and saved successfully!")
        else:
            QMessageBox.critical(self, "Error", msg)
