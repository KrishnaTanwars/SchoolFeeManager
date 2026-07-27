"""
Professional ERP Dashboard View with Responsive KPI Cards & Modern Analytics.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from controllers.report_controller import ReportController
from controllers.receipt_controller import ReceiptController
from utils.helpers import format_currency, format_date
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog

class DashboardView(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Header Title Banner
        hdr_layout = QHBoxLayout()
        title_lbl = QLabel("Executive Dashboard & Key Performance Indicators")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a;")
        hdr_layout.addWidget(title_lbl)
        hdr_layout.addStretch()

        self.btn_refresh = QPushButton("🔄  Refresh Data")
        self.btn_refresh.setProperty("class", "SecondaryBtn")
        self.btn_refresh.clicked.connect(self.refresh_dashboard)
        hdr_layout.addWidget(self.btn_refresh)

        layout.addLayout(hdr_layout)

        # Quick Management Actions (Main Navigation Hub at Top)
        actions_group = QGroupBox("Quick Management Actions")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(12)

        btn_collect = QPushButton("💳  Collect Fee / Issue Receipt")
        btn_collect.setFixedHeight(40)
        btn_collect.setProperty("class", "SuccessBtn")
        btn_collect.setCursor(Qt.PointingHandCursor)
        btn_collect.clicked.connect(lambda: self.navigate_requested.emit("receipt"))

        btn_student = QPushButton("👨‍🎓  + Register New Student")
        btn_student.setFixedHeight(40)
        btn_student.setCursor(Qt.PointingHandCursor)
        btn_student.clicked.connect(lambda: self.navigate_requested.emit("students_add"))

        btn_reports = QPushButton("📈  Financial Reports & Audit")
        btn_reports.setFixedHeight(40)
        btn_reports.setProperty("class", "SecondaryBtn")
        btn_reports.setCursor(Qt.PointingHandCursor)
        btn_reports.clicked.connect(lambda: self.navigate_requested.emit("reports"))

        btn_backup = QPushButton("⚙️  Database Backup & Restore")
        btn_backup.setFixedHeight(40)
        btn_backup.setProperty("class", "SecondaryBtn")
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.clicked.connect(lambda: self.navigate_requested.emit("settings"))

        actions_layout.addWidget(btn_collect, stretch=1)
        actions_layout.addWidget(btn_student, stretch=1)
        actions_layout.addWidget(btn_reports, stretch=1)
        actions_layout.addWidget(btn_backup, stretch=1)

        layout.addWidget(actions_group)

        # Lower Split: Recent Receipts Ledger (Left) + Student Analytics (Right)
        bottom_split = QHBoxLayout()
        bottom_split.setSpacing(15)

        # Recent Receipts Table Section
        recent_group = QGroupBox("Recent Fee Receipts Ledger")
        recent_layout = QVBoxLayout(recent_group)
        recent_layout.setContentsMargins(12, 12, 12, 12)

        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(6)
        self.table_recent.setHorizontalHeaderLabels([
            "Receipt No", "Date", "Student Name", "Class & Sec", "Paid (₹)", "Action"
        ])
        
        header = self.table_recent.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_recent.setColumnWidth(5, 160)

        self.table_recent.verticalHeader().setDefaultSectionSize(42)
        self.table_recent.setAlternatingRowColors(True)

        recent_layout.addWidget(self.table_recent)
        bottom_split.addWidget(recent_group, stretch=2)

        # Student Analytics by Class Section
        analytics_group = QGroupBox("Student Statistics by Class & Course")
        analytics_layout = QVBoxLayout(analytics_group)
        analytics_layout.setContentsMargins(12, 12, 12, 12)

        self.table_analytics = QTableWidget()
        self.table_analytics.setColumnCount(2)
        self.table_analytics.setHorizontalHeaderLabels(["Class / Stream", "Enrolled Students"])
        self.table_analytics.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_analytics.verticalHeader().setDefaultSectionSize(32)
        self.table_analytics.setAlternatingRowColors(True)

        analytics_layout.addWidget(self.table_analytics)
        bottom_split.addWidget(analytics_group, stretch=1)

        layout.addLayout(bottom_split, stretch=1)

        self.refresh_dashboard()

    def _create_kpi_card(self, title: str, initial_value: str, color: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "KPICard")

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(16, 14, 16, 14)

        lbl_t = QLabel(title)
        lbl_t.setProperty("class", "KPITitle")

        lbl_v = QLabel(initial_value)
        lbl_v.setProperty("class", "KPIValue")
        lbl_v.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")

        vbox.addWidget(lbl_t)
        vbox.addWidget(lbl_v)
        card.lbl_val = lbl_v
        return card

    def refresh_dashboard(self):
        # Recent Receipts
        recent_receipts = ReceiptController.get_all_receipts()[:10]
        self.table_recent.setRowCount(len(recent_receipts))

        for row_idx, r in enumerate(recent_receipts):
            self.table_recent.setItem(row_idx, 0, QTableWidgetItem(r.receipt_no))
            self.table_recent.setItem(row_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
            self.table_recent.setItem(row_idx, 2, QTableWidgetItem(r.student.name if r.student else "N/A"))
            self.table_recent.setItem(row_idx, 3, QTableWidgetItem(f"{r.student.class_name} ({r.student.section or 'A'})" if r.student else "N/A"))
            self.table_recent.setItem(row_idx, 4, QTableWidgetItem(format_currency(r.total_amount)))

            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(6, 4, 6, 4)
            act_layout.setAlignment(Qt.AlignCenter)

            btn_view = QPushButton("👁  View / Print")
            btn_view.setFixedHeight(30)
            btn_view.setMinimumWidth(130)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #1e3a8a;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 5px;
                    border: none;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.clicked.connect(lambda _, rec=r: self.view_receipt(rec))

            act_layout.addWidget(btn_view)
            self.table_recent.setCellWidget(row_idx, 5, action_widget)

        # Student Analytics by Class & Course
        from controllers.student_controller import StudentController
        class_stats = StudentController.get_student_counts_by_class()
        self.table_analytics.setRowCount(len(class_stats))

        for r_idx, stat in enumerate(class_stats):
            self.table_analytics.setItem(r_idx, 0, QTableWidgetItem(stat["class_name"]))
            self.table_analytics.setItem(r_idx, 1, QTableWidgetItem(f"{stat['student_count']} Students"))

    def view_receipt(self, receipt):
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()
