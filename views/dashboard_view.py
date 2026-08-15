"""
Professional ERP Dashboard View with Responsive KPI Cards & Modern Analytics.
Expanded Recent Fee Receipts Ledger layout without Recent System Activity widget.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from controllers.report_controller import ReportController
from controllers.receipt_controller import ReceiptController
from utils.helpers import format_currency, format_date
from utils.table_delegate import apply_responsive_table_formatting
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from utils.logger import logger


class DashboardView(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Executive Dashboard & Key Performance Indicators")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_refresh = QPushButton("🔄  Refresh Data")
        self.btn_refresh.setProperty("class", "SecondaryBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_dashboard)
        hdr_layout.addWidget(self.btn_refresh)

        layout.addLayout(hdr_layout)

        # Quick Management Actions (Main Navigation Hub at Top)
        actions_group = QGroupBox("Quick Management Actions")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(12)

        btn_collect = QPushButton("💳  Collect Fee / Issue Receipt")
        btn_collect.setMinimumHeight(40)
        btn_collect.setProperty("class", "SuccessBtn")
        btn_collect.setCursor(Qt.PointingHandCursor)
        btn_collect.clicked.connect(lambda: self.navigate_requested.emit("receipt"))

        btn_student = QPushButton("👨‍🎓  + Register New Student")
        btn_student.setMinimumHeight(40)
        btn_student.setCursor(Qt.PointingHandCursor)
        btn_student.clicked.connect(lambda: self.navigate_requested.emit("students_add"))

        btn_reports = QPushButton("📈  Financial Reports & Audit")
        btn_reports.setMinimumHeight(40)
        btn_reports.setProperty("class", "SecondaryBtn")
        btn_reports.setCursor(Qt.PointingHandCursor)
        btn_reports.clicked.connect(lambda: self.navigate_requested.emit("reports"))

        btn_backup = QPushButton("⚙️  Database Backup & Restore")
        btn_backup.setMinimumHeight(40)
        btn_backup.setProperty("class", "SecondaryBtn")
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.clicked.connect(lambda: self.navigate_requested.emit("settings"))

        actions_layout.addWidget(btn_collect, stretch=1)
        actions_layout.addWidget(btn_student, stretch=1)
        actions_layout.addWidget(btn_reports, stretch=1)
        actions_layout.addWidget(btn_backup, stretch=1)

        layout.addWidget(actions_group)

        # Main Workspace Content: Expanded Recent Receipts Ledger (Left) + Right Panel Widgets
        main_split = QHBoxLayout()
        main_split.setSpacing(16)

        # Left Panel: Expanded Vertically Recent Fee Receipts Ledger
        recent_group = QGroupBox("Recent Fee Receipts Ledger")
        recent_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        recent_layout = QVBoxLayout(recent_group)
        recent_layout.setContentsMargins(12, 12, 12, 12)

        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(6)
        self.table_recent.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Student Name", "Course / Branch", "Paid (₹)", "Action"
        ])
        self.table_recent.setMinimumHeight(380)

        header = self.table_recent.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_recent.setColumnWidth(5, 140)

        self.table_recent.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_recent)

        recent_layout.addWidget(self.table_recent)
        main_split.addWidget(recent_group, stretch=2)

        # Right Panel: Stacked Analytics & Recently Opened Items
        right_vbox = QVBoxLayout()
        right_vbox.setSpacing(16)

        # 1. Student Statistics by Course
        analytics_group = QGroupBox("Student Statistics by Course")
        analytics_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        analytics_layout = QVBoxLayout(analytics_group)
        analytics_layout.setContentsMargins(10, 10, 10, 10)

        self.table_analytics = QTableWidget()
        self.table_analytics.setColumnCount(2)
        self.table_analytics.setHorizontalHeaderLabels(["Course Name", "Enrolled Students"])
        self.table_analytics.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_analytics.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_analytics)

        analytics_layout.addWidget(self.table_analytics)
        right_vbox.addWidget(analytics_group, stretch=1)

        # 2. Recently Opened Quick Access
        rec_opened_group = QGroupBox("📌  Recently Opened Items")
        rec_opened_group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        v_rec_opened = QVBoxLayout(rec_opened_group)
        v_rec_opened.setContentsMargins(10, 10, 10, 10)

        self.table_recently_opened = QTableWidget()
        self.table_recently_opened.setColumnCount(3)
        self.table_recently_opened.setHorizontalHeaderLabels(["Type", "Title / Item", "Time"])
        self.table_recently_opened.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recently_opened.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_recently_opened)

        v_rec_opened.addWidget(self.table_recently_opened)
        right_vbox.addWidget(rec_opened_group, stretch=1)

        main_split.addLayout(right_vbox, stretch=1)
        layout.addLayout(main_split, stretch=1)

        scroll.setWidget(container)
        main_vbox.addWidget(scroll)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        try:
            # Expanded Recent Receipts (top 25)
            recent_receipts = ReceiptController.get_all_receipts()[:25]
            self.table_recent.setRowCount(len(recent_receipts))

            for row_idx, r in enumerate(recent_receipts):
                self.table_recent.setItem(row_idx, 0, QTableWidgetItem(r.receipt_no))
                self.table_recent.setItem(row_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
                self.table_recent.setItem(row_idx, 2, QTableWidgetItem(r.student.name if r.student else "N/A"))
                crs_br = f"{r.student.course or 'General'}" + (f" ({r.student.branch})" if (r.student and getattr(r.student, "branch", None)) else "") if r.student else "N/A"
                self.table_recent.setItem(row_idx, 3, QTableWidgetItem(crs_br))
                paid_val = getattr(r, 'paid_amount', r.total_amount) or r.total_amount
                self.table_recent.setItem(row_idx, 4, QTableWidgetItem(format_currency(paid_val)))

                action_widget = QWidget()
                act_layout = QHBoxLayout(action_widget)
                act_layout.setContentsMargins(4, 2, 4, 2)
                act_layout.setAlignment(Qt.AlignCenter)

                btn_view = QPushButton("👁  View / Print")
                btn_view.setFixedHeight(28)
                btn_view.setStyleSheet("""
                    QPushButton {
                        background-color: #1e3a8a;
                        color: #ffffff;
                        font-size: 11px;
                        font-weight: bold;
                        border-radius: 4px;
                        border: none;
                        padding: 2px 8px;
                    }
                    QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
                btn_view.setCursor(Qt.PointingHandCursor)
                btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

                act_layout.addWidget(btn_view)
                self.table_recent.setCellWidget(row_idx, 5, action_widget)

            # Student Analytics by Course
            from controllers.student_controller import StudentController
            course_stats = StudentController.get_student_counts_by_course()
            self.table_analytics.setRowCount(len(course_stats))

            for r_idx, stat in enumerate(course_stats):
                self.table_analytics.setItem(r_idx, 0, QTableWidgetItem(stat["course_name"]))
                self.table_analytics.setItem(r_idx, 1, QTableWidgetItem(f"{stat['student_count']} Students"))

            # Recently Opened Widget
            from services.recently_opened_service import RecentlyOpenedService
            recent_items = RecentlyOpenedService.get_recent_items(limit=10)
            self.table_recently_opened.setRowCount(len(recent_items))

            for idx, item in enumerate(recent_items):
                self.table_recently_opened.setItem(idx, 0, QTableWidgetItem(item["category"]))
                self.table_recently_opened.setItem(idx, 1, QTableWidgetItem(item["title"]))
                self.table_recently_opened.setItem(idx, 2, QTableWidgetItem(item["timestamp"]))
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}", exc_info=True)

    def view_receipt(self, receipt):
        from services.recently_opened_service import RecentlyOpenedService
        RecentlyOpenedService.add_recent_item("Receipt", f"Receipt {receipt.receipt_no}", receipt.id, f"Amount: {format_currency(receipt.total_amount)}")
        fresh_rec = ReceiptController.get_receipt_by_id(receipt.id) or receipt
        dlg = ReceiptPreviewDialog(self, fresh_rec)
        dlg.exec()
