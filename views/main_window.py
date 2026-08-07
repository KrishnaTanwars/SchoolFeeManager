"""
Main Application Shell Window with Commercial Auto-Collapsible Sidebar Navigation & View Router.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QStatusBar, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSettings
from PySide6.QtGui import QKeySequence, QShortcut

from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.receipt_view import ReceiptView
from views.receipt_history_view import ReceiptHistoryView
from views.student_view import StudentView
from views.fee_category_view import FeeCategoryView
from views.report_view import ReportView
from views.settings_view import SettingsView

from controllers.auth_controller import AuthController
from controllers.settings_controller import SettingsController
from config.app_config import APP_NAME, APP_VERSION
from utils.helpers import format_date

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - Enterprise Edition")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 680)

        # Local User Preference Storage for Sidebar State
        self.settings = QSettings("SmartSchool", "SchoolFeeManager")
        # Default to COLLAPSED (False) on fresh launch
        self.sidebar_expanded = self.settings.value("sidebar_expanded", False, type=bool)

        self.setup_ui()
        self.setup_shortcuts()
        self.trigger_auto_backup()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------- SIDEBAR FRAME ----------------
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("SidebarFrame")
        
        initial_width = 220 if self.sidebar_expanded else 60
        self.sidebar_frame.setFixedWidth(initial_width)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(6, 12, 6, 12)
        sidebar_layout.setSpacing(6)

        # App Brand & Toggle Header
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(6)

        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(36, 36)
        self.btn_toggle.setToolTip("Toggle Navigation Sidebar (Ctrl+B)")
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #1e293b;
                color: #ffffff;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)

        self.title_container = QWidget()
        title_v = QVBoxLayout(self.title_container)
        title_v.setContentsMargins(4, 0, 0, 0)
        title_v.setSpacing(2)

        self.lbl_title = QLabel("EDULEDGER")
        self.lbl_title.setObjectName("SidebarTitle")
        self.lbl_title.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;")

        self.lbl_subtitle = QLabel(f"ERP v{APP_VERSION}")
        self.lbl_subtitle.setObjectName("SidebarSubtitle")
        self.lbl_subtitle.setStyleSheet("color: #38bdf8; font-size: 10px; font-weight: 600;")

        title_v.addWidget(self.lbl_title)
        title_v.addWidget(self.lbl_subtitle)

        brand_layout.addWidget(self.btn_toggle)
        brand_layout.addWidget(self.title_container)
        brand_layout.addStretch()

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(10)

        # Navigation Items Data: (key, full_text, compact_text, tooltip)
        self.nav_items_data = [
            ("dashboard", "🏠   Dashboard", "🏠", "Dashboard (Alt+1)"),
            ("receipt", "💰   Fee Collection", "💰", "Fee Collection (Alt+2)"),
            ("history", "📜   Receipt History", "📜", "Receipt History (Alt+3)"),
            ("students", "👨‍🎓   Student Master", "👨‍🎓", "Student Master (Alt+4)"),
            ("fees", "🏷️   Fee Heads Master", "🏷️", "Fee Heads Master (Alt+5)"),
            ("reports", "📊   Financial Reports", "📊", "Financial Reports (Alt+6)"),
            ("settings", "⚙️   Settings & Backup", "⚙️", "Settings & Backup (Alt+7)"),
        ]

        # Navigation Buttons
        self.nav_buttons = {}
        for key, full_text, compact_text, tooltip in self.nav_items_data:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setProperty("class", "NavBtn")
            btn.setFixedHeight(38)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.navigate_to(k))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sidebar_layout.addStretch()

        # Logout Button
        self.btn_logout = QPushButton()
        self.btn_logout.setProperty("class", "NavBtn")
        self.btn_logout.setFixedHeight(38)
        self.btn_logout.setToolTip("Log Out System")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(self.sidebar_frame)

        # Apply initial collapsed/expanded UI state
        self.update_sidebar_visuals(animated=False)

        # ---------------- RIGHT CONTAINER ----------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(12)

        self.lbl_school_header = QLabel("DPS International School")
        self.lbl_school_header.setObjectName("HeaderTitle")

        # Global Search Header Button
        self.btn_global_search = QPushButton("🔍  Search everywhere... (Ctrl+K)")
        self.btn_global_search.setFixedHeight(30)
        self.btn_global_search.setMinimumWidth(220)
        self.btn_global_search.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #1e3a8a;
                border-color: #2563eb;
            }
        """)
        self.btn_global_search.setCursor(Qt.PointingHandCursor)
        self.btn_global_search.clicked.connect(self.open_global_search)

        # Global Search Keyboard Shortcut (Ctrl+K)
        shortcut_search = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut_search.activated.connect(self.open_global_search)

        self.lbl_user_info = QLabel("User: System Administrator")
        self.lbl_user_info.setObjectName("HeaderUser")

        header_layout.addWidget(self.lbl_school_header)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_global_search)
        header_layout.addWidget(self.lbl_user_info)

        right_layout.addWidget(header_frame)

        # QStackedWidget Content Views
        self.stacked_widget = QStackedWidget()

        # Initialize Views
        self.views = {
            "login": LoginView(),
            "dashboard": DashboardView(),
            "receipt": ReceiptView(),
            "history": ReceiptHistoryView(),
            "students": StudentView(),
            "fees": FeeCategoryView(),
            "reports": ReportView(),
            "settings": SettingsView()
        }

        # Signals connection
        self.views["login"].login_success.connect(self.on_login_success)
        self.views["dashboard"].navigate_requested.connect(self.navigate_to)

        for key, view_widget in self.views.items():
            self.stacked_widget.addWidget(view_widget)

        right_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(right_container)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("School Fee ERP System | Status: Connected (Offline DB)")

        # Start at Login
        self.show_login()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        QShortcut(QKeySequence("Ctrl+P"), self, lambda: self.navigate_to("receipt"))
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.navigate_to("students_add"))
        QShortcut(QKeySequence("F5"), self, self.refresh_active_view)

    def show_login(self):
        self.sidebar_frame.hide()
        self.lbl_school_header.hide()
        self.lbl_user_info.hide()
        self.stacked_widget.setCurrentWidget(self.views["login"])

    def on_login_success(self):
        user = AuthController.get_current_user()
        if user:
            self.lbl_user_info.setText(f"Logged in as: <b>{user.full_name}</b> ({user.role})")
        
        info = SettingsController.get_school_info()
        if info:
            self.lbl_school_header.setText(f"<b>{info.school_name}</b> &nbsp;|&nbsp; Academic Session: <b>{info.current_session}</b>")

        self.sidebar_frame.show()
        self.lbl_school_header.show()
        self.lbl_user_info.show()
        self.navigate_to("dashboard")

    def toggle_sidebar(self):
        """Toggle sidebar between expanded (220px) and collapsed (60px) state with smooth QPropertyAnimation."""
        self.sidebar_expanded = not self.sidebar_expanded
        self.settings.setValue("sidebar_expanded", self.sidebar_expanded)
        self.update_sidebar_visuals(animated=True)

    def update_sidebar_visuals(self, animated: bool = True):
        start_w = self.sidebar_frame.width()
        end_w = 220 if self.sidebar_expanded else 60

        if animated:
            # Smooth QPropertyAnimation over 200 ms
            self.anim_min = QPropertyAnimation(self.sidebar_frame, b"minimumWidth")
            self.anim_min.setDuration(200)
            self.anim_min.setStartValue(start_w)
            self.anim_min.setEndValue(end_w)
            self.anim_min.setEasingCurve(QEasingCurve.InOutQuad)

            self.anim_max = QPropertyAnimation(self.sidebar_frame, b"maximumWidth")
            self.anim_max.setDuration(200)
            self.anim_max.setStartValue(start_w)
            self.anim_max.setEndValue(end_w)
            self.anim_max.setEasingCurve(QEasingCurve.InOutQuad)

            self.anim_group = QParallelAnimationGroup()
            self.anim_group.addAnimation(self.anim_min)
            self.anim_group.addAnimation(self.anim_max)
            self.anim_group.start()
        else:
            self.sidebar_frame.setFixedWidth(end_w)

        # Toggle Brand Title Container
        if self.sidebar_expanded:
            self.title_container.show()
        else:
            self.title_container.hide()

        # Update Navigation Button Text & Alignment
        for key, full_text, compact_text, tooltip in self.nav_items_data:
            btn = self.nav_buttons[key]
            if self.sidebar_expanded:
                btn.setText(full_text)
                btn.setStyleSheet("text-align: left; padding-left: 12px; font-size: 12px;")
            else:
                btn.setText(compact_text)
                btn.setStyleSheet("text-align: center; padding-left: 0px; font-size: 16px;")

        # Logout Button
        if self.sidebar_expanded:
            self.btn_logout.setText("🔒   Log Out System")
            self.btn_logout.setStyleSheet("text-align: left; padding-left: 12px; font-size: 12px;")
        else:
            self.btn_logout.setText("🔒")
            self.btn_logout.setStyleSheet("text-align: center; padding-left: 0px; font-size: 16px;")

    def navigate_to(self, key: str):
        auto_add_student = False
        if key in ("student", "students_add"):
            if key == "students_add":
                auto_add_student = True
            key = "students"

        if key not in self.views:
            return

        # Settings Protection Hook
        if key == "settings":
            from dialogs.admin_auth_dialog import AdminAuthDialog
            from services.security_service import SecurityService

            auth_dlg = AdminAuthDialog(
                self,
                action_title="Settings Authorization Required",
                action_context="Access System Settings & Administration",
                module="Settings"
            )
            if not auth_dlg.exec():
                SecurityService.log_audit(
                    action="Settings Access Denied",
                    module="Settings",
                    details="Attempted to access Settings without valid administrator authorization",
                    status="Denied"
                )
                # Keep navigation button state synchronized with currently visible view
                curr_view = self.stacked_widget.currentWidget()
                for k, v in self.views.items():
                    if v == curr_view and k in self.nav_buttons:
                        self.nav_buttons[k].setChecked(True)
                return

            SecurityService.log_audit(
                action="Settings Opened",
                module="Settings",
                details="Administrator authorized access to Settings",
                status="Success"
            )

        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)

        view = self.views[key]
        self.stacked_widget.setCurrentWidget(view)

        if hasattr(view, "refresh_dashboard"):
            view.refresh_dashboard()
        elif hasattr(view, "refresh_view"):
            view.refresh_view()
        elif hasattr(view, "load_students"):
            view.load_students()
            if auto_add_student and hasattr(view, "add_student"):
                view.add_student()
        elif hasattr(view, "load_categories"):
            view.load_categories()
        elif hasattr(view, "load_receipts"):
            view.load_receipts()

        self.status_bar.showMessage(f"Active Screen: {key.capitalize()}")

    def open_global_search(self):
        from dialogs.global_search_dialog import GlobalSearchDialog
        dlg = GlobalSearchDialog(self, on_navigate_callback=self.on_global_search_navigate)
        dlg.exec()

    def on_global_search_navigate(self, target_data: dict):
        t_view = target_data.get("target_view", "dashboard")
        self.navigate_to(t_view)

        if t_view == "reports" and "report_key" in target_data:
            report_view = self.views.get("reports")
            if hasattr(report_view, "open_report"):
                report_view.open_report(target_data["report_key"])

        elif t_view == "students" and target_data.get("title"):
            student_view = self.views.get("students")
            if hasattr(student_view, "txt_search"):
                student_view.txt_search.setText(target_data["title"])

        elif t_view == "receipt_history" and target_data.get("receipt_no"):
            history_view = self.views.get("history")
            if hasattr(history_view, "txt_search"):
                history_view.txt_search.setText(target_data["receipt_no"])

    def trigger_auto_backup(self):
        try:
            from services.backup_service import BackupService
            BackupService.check_and_run_auto_backup()
        except Exception as e:
            logger.warning(f"Startup auto-backup notice: {e}")

    def refresh_active_view(self):
        curr = self.stacked_widget.currentWidget()
        if hasattr(curr, "refresh_dashboard"):
            curr.refresh_dashboard()
        elif hasattr(curr, "load_students"):
            curr.load_students()

    def logout(self):
        reply = QMessageBox.question(
            self, "Log Out", "Are you sure you want to log out of the Fee ERP System?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            AuthController.logout()
            self.show_login()
