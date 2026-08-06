"""
Main Application Shell Window with Commercial Sidebar Navigation & View Router.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QStatusBar, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSize
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

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------- SIDEBAR FRAME ----------------
        self.sidebar_expanded = True
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("SidebarFrame")
        self.sidebar_frame.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(6)

        # App Brand & Toggle Header
        brand_layout = QHBoxLayout()
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(36, 36)
        self.btn_toggle.setToolTip("Expand / Collapse Sidebar")
        self.btn_toggle.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #1e293b; color: #ffffff; border: none; border-radius: 4px;")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)

        title_v = QVBoxLayout()
        self.lbl_title = QLabel("SCHOOL FEE ERP")
        self.lbl_title.setObjectName("SidebarTitle")

        self.lbl_subtitle = QLabel(f"ERP v{APP_VERSION}")
        self.lbl_subtitle.setObjectName("SidebarSubtitle")

        title_v.addWidget(self.lbl_title)
        title_v.addWidget(self.lbl_subtitle)

        brand_layout.addWidget(self.btn_toggle)
        brand_layout.addLayout(title_v)
        brand_layout.addStretch()

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(10)

        # Navigation Items Data: (key, full_text, compact_text, tooltip)
        self.nav_items_data = [
            ("dashboard", "📊  Dashboard", "📊", "Dashboard"),
            ("receipt", "💳  Collect Fee", "💳", "Collect Fee"),
            ("history", "📜  Receipt History", "📜", "Receipt History"),
            ("students", "👨‍🎓  Student Master", "👨‍🎓", "Student Master"),
            ("fees", "🏷️  Fee Heads Master", "🏷️", "Fee Heads Master"),
            ("reports", "📈  Financial Reports", "📈", "Financial Reports"),
            ("settings", "⚙️  Settings & Backup", "⚙️", "Settings & Backup"),
        ]

        # Navigation Buttons
        self.nav_buttons = {}
        for key, full_text, compact_text, tooltip in self.nav_items_data:
            btn = QPushButton(full_text)
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
        self.btn_logout = QPushButton("🔒  Log Out System")
        self.btn_logout.setProperty("class", "NavBtn")
        self.btn_logout.setFixedHeight(38)
        self.btn_logout.setToolTip("Log Out System")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(self.sidebar_frame)

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

        self.lbl_school_header = QLabel("DPS International School")
        self.lbl_school_header.setObjectName("HeaderTitle")

        self.lbl_user_info = QLabel("User: System Administrator")
        self.lbl_user_info.setObjectName("HeaderUser")

        header_layout.addWidget(self.lbl_school_header)
        header_layout.addStretch()
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
        self.sidebar_expanded = not self.sidebar_expanded

        if self.sidebar_expanded:
            self.sidebar_frame.setFixedWidth(220)
            self.lbl_title.show()
            self.lbl_subtitle.show()
            for key, full_text, compact_text, tooltip in self.nav_items_data:
                self.nav_buttons[key].setText(full_text)
            self.btn_logout.setText("🔒  Log Out System")
        else:
            self.sidebar_frame.setFixedWidth(65)
            self.lbl_title.hide()
            self.lbl_subtitle.hide()
            for key, full_text, compact_text, tooltip in self.nav_items_data:
                self.nav_buttons[key].setText(compact_text)
            self.btn_logout.setText("🔒")

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
