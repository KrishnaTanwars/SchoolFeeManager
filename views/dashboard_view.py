"""
Professional ERP Dashboard View with Responsive KPI Cards & Modern Analytics.
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
            "Receipt No", "Date", "Student Name", "Course / Branch", "Paid (₹)", "Action"
        ])
        
        header = self.table_recent.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_recent.setColumnWidth(5, 160)

        self.table_recent.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_recent)

        recent_layout.addWidget(self.table_recent)
        bottom_split.addWidget(recent_group, stretch=2)

        # Student Analytics by Course Section
        analytics_group = QGroupBox("Student Statistics by Course")
        analytics_layout = QVBoxLayout(analytics_group)
        analytics_layout.setContentsMargins(12, 12, 12, 12)

        self.table_analytics = QTableWidget()
        self.table_analytics.setColumnCount(2)
        self.table_analytics.setHorizontalHeaderLabels(["Course Name", "Enrolled Students"])
        self.table_analytics.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_analytics.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_analytics)

        analytics_layout.addWidget(self.table_analytics)
        bottom_split.addWidget(analytics_group, stretch=1)

        layout.addLayout(bottom_split)

        # Recent Activity & Recently Opened Split Section (Section 10 & 11)
        activity_split = QHBoxLayout()
        activity_split.setSpacing(15)

        # Recent Activity (Audit Log Widget)
        act_group = QGroupBox("📜  Recent System Activity (Last 20 Events)")
        v_act = QVBoxLayout(act_group)
        v_act.setContentsMargins(10, 10, 10, 10)

        self.table_recent_activity = QTableWidget()
        self.table_recent_activity.setColumnCount(4)
        self.table_recent_activity.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Description Details"])
        self.table_recent_activity.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_recent_activity.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_recent_activity.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_recent_activity)

        v_act.addWidget(self.table_recent_activity)
        activity_split.addWidget(act_group, stretch=2)

        # Recently Opened Quick Access
        rec_opened_group = QGroupBox("📌  Recently Opened Items")
        v_rec_opened = QVBoxLayout(rec_opened_group)
        v_rec_opened.setContentsMargins(10, 10, 10, 10)

        self.table_recently_opened = QTableWidget()
        self.table_recently_opened.setColumnCount(3)
        self.table_recently_opened.setHorizontalHeaderLabels(["Type", "Title / Item", "Time"])
        self.table_recently_opened.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recently_opened.setAlternatingRowColors(True)
        apply_responsive_table_formatting(self.table_recently_opened)

        v_rec_opened.addWidget(self.table_recently_opened)
        activity_split.addWidget(rec_opened_group, stretch=1)

        layout.addLayout(activity_split, stretch=1)

        scroll.setWidget(container)
        main_vbox.addWidget(scroll)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        try:
            # Recent Receipts
            recent_receipts = ReceiptController.get_all_receipts()[:10]
            self.table_recent.setRowCount(len(recent_receipts))

            for row_idx, r in enumerate(recent_receipts):
                self.table_recent.setItem(row_idx, 0, QTableWidgetItem(r.receipt_no))
                self.table_recent.setItem(row_idx, 1, QTableWidgetItem(format_date(r.receipt_date)))
                self.table_recent.setItem(row_idx, 2, QTableWidgetItem(r.student.name if r.student else "N/A"))
                crs_br = f"{r.student.course or 'General'}" + (f" ({r.student.branch})" if (r.student and getattr(r.student, "branch", None)) else "") if r.student else "N/A"
                self.table_recent.setItem(row_idx, 3, QTableWidgetItem(crs_br))
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

            # Student Analytics by Course
            from controllers.student_controller import StudentController
            course_stats = StudentController.get_student_counts_by_course()
            self.table_analytics.setRowCount(len(course_stats))

            for r_idx, stat in enumerate(course_stats):
                self.table_analytics.setItem(r_idx, 0, QTableWidgetItem(stat["course_name"]))
                self.table_analytics.setItem(r_idx, 1, QTableWidgetItem(f"{stat['student_count']} Students"))

            # Recent Activity Widget (Last 20 Audit Events)
            from controllers.settings_controller import SettingsController
            audit_logs = SettingsController.get_audit_logs(limit=20)
            self.table_recent_activity.setRowCount(len(audit_logs))

            for idx, l in enumerate(audit_logs):
                self.table_recent_activity.setItem(idx, 0, QTableWidgetItem(f"{l['date']} {l['time']}"))
                self.table_recent_activity.setItem(idx, 1, QTableWidgetItem(l["user"]))
                self.table_recent_activity.setItem(idx, 2, QTableWidgetItem(l["action"]))
                self.table_recent_activity.setItem(idx, 3, QTableWidgetItem(l["details"]))

            # Recently Opened Widget
            from services.recently_opened_service import RecentlyOpenedService
            recent_items = RecentlyOpenedService.get_recent_items(limit=10)
            self.table_recently_opened.setRowCount(len(recent_items))

            for idx, item in enumerate(recent_items):
                self.table_recently_opened.setItem(idx, 0, QTableWidgetItem(item["category"]))
                self.table_recently_opened.setItem(idx, 1, QTableWidgetItem(item["title"]))
                self.table_recently_opened.setItem(idx, 2, QTableWidgetItem(item["timestamp"]))
        except Exception:
            pass

    def view_receipt(self, receipt):
        from services.recently_opened_service import RecentlyOpenedService
        RecentlyOpenedService.add_recent_item("Receipt", f"Receipt {receipt.receipt_no}", receipt.id, f"Amount: {format_currency(receipt.total_amount)}")
        dlg = ReceiptPreviewDialog(self, receipt)
        dlg.exec()
