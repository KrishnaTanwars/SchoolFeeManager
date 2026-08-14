"""
Main Application Shell Window with Commercial Auto-Collapsible Sidebar Navigation & View Router.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QStatusBar, QMessageBox, QApplication,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, QRect, QSettings
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QCursor

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

class OverlaySidebarFrame(QFrame):
    """
    Enterprise Floating Overlay Sidebar Panel.
    Hovers on top of central views without triggering layout reflows or resizing main content.
    """
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.main_window and hasattr(self.main_window, "on_sidebar_mouse_enter"):
            self.main_window.on_sidebar_mouse_enter()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.main_window and hasattr(self.main_window, "on_sidebar_mouse_leave"):
            self.main_window.on_sidebar_mouse_leave()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"EduLedger ERP v{APP_VERSION} - Enterprise Production Edition")
        self.setMinimumSize(800, 600)
        self.resize(1280, 800)

        # Restore window geometry and state from QSettings if available
        settings = QSettings("EduLedger", "SchoolFeeManager")
        geom = settings.value("geometry")
        state = settings.value("windowState")
        if geom:
            self.restoreGeometry(geom)
        else:
            self.showMaximized()
        if state:
            self.restoreState(state)

        # Always start sidebar COLLAPSED (False) and UNPINNED (False) on startup
        self.sidebar_expanded = False
        self.is_pinned = False
        self._ignore_initial_hover = True

        # Mouse leave delay timer (200ms)
        self.leave_timer = QTimer(self)
        self.leave_timer.setSingleShot(True)
        self.leave_timer.timeout.connect(self.on_leave_timer_timeout)

        self.setup_ui()
        self.setup_shortcuts()
        self.trigger_auto_backup()

    def closeEvent(self, event):
        settings = QSettings("EduLedger", "SchoolFeeManager")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------- SIDEBAR BASE SPACER ----------------
        # Fixed 60px base spacer in main layout to reserve exact space for collapsed sidebar.
        # Right container starts at x=60 and NEVER resizes or shifts during sidebar hover.
        self.sidebar_base = QWidget()
        self.sidebar_base.setFixedWidth(60)
        self.sidebar_base.setStyleSheet("background-color: #0f172a;")
        self.main_layout.addWidget(self.sidebar_base)

        # ---------------- OVERLAY SIDEBAR FRAME ----------------
        # Floating Layer 2 widget parented directly to central_widget
        self.sidebar_frame = OverlaySidebarFrame(parent=central_widget, main_window=self)
        self.sidebar_frame.setObjectName("SidebarFrame")

        # Elevation Drop Shadow for Windows 11 style floating panel
        self.shadow_effect = QGraphicsDropShadowEffect(self.sidebar_frame)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setOffset(4, 0)
        self.shadow_effect.setColor(QColor(0, 0, 0, 90))
        self.sidebar_frame.setGraphicsEffect(self.shadow_effect)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(6)

        # App Brand & Controls Header
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

        self.btn_pin = QPushButton("📍")
        self.btn_pin.setFixedSize(36, 36)
        self.btn_pin.setToolTip("Pin Sidebar (Stay Expanded)")
        self.btn_pin.setCursor(Qt.PointingHandCursor)
        self.btn_pin.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #1e293b;
                color: #94a3b8;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #38bdf8;
            }
            QPushButton:checked {
                background-color: #1e3a8a;
                color: #ffffff;
                border: 1px solid #38bdf8;
            }
        """)
        self.btn_pin.setCheckable(True)
        self.btn_pin.clicked.connect(self.toggle_pin_mode)

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
        brand_layout.addWidget(self.btn_pin)

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
            btn.clicked.connect(lambda _, k=key: self.on_nav_button_clicked(k))
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

        # Apply initial collapsed/expanded UI state
        self.update_sidebar_visuals(animated=False)

        # ---------------- RIGHT CONTAINER ----------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header Bar
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(self.header_frame)
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

        header_layout.addWidget(self.lbl_school_header)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_global_search)

        right_layout.addWidget(self.header_frame)

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

        # Logged-in User Status Bar Label (Permanent Right-Aligned Widget)
        self.lbl_status_user = QLabel("")
        self.lbl_status_user.setObjectName("StatusUserLabel")
        self.lbl_status_user.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 500;
                color: #475569;
                padding-right: 12px;
            }
        """)
        self.status_bar.addPermanentWidget(self.lbl_status_user)

        # Connect Session Manager Signal for Real-Time Academic Session Header Sync
        from services.session_service import session_manager
        session_manager.session_changed.connect(self.on_active_session_changed)

        # Start at Login
        self.show_login()

    def update_header_label(self, active_session: str = None):
        if not active_session:
            from services.session_service import session_manager
            active_session = session_manager.get_active_session()
        info = SettingsController.get_school_info()
        school_name = info.school_name if info else "DPS International School"
        self.lbl_school_header.setText(f"<b>{school_name}</b> &nbsp;|&nbsp; Academic Session: <b>{active_session}</b>")

    def on_active_session_changed(self, new_session: str):
        self.update_header_label(new_session)
        # Synchronize and refresh all stacked views dynamically
        for key, view in self.views.items():
            try:
                if hasattr(view, "refresh_dashboard"):
                    view.refresh_dashboard()
                elif hasattr(view, "refresh_view"):
                    view.refresh_view()
                elif hasattr(view, "load_students"):
                    view.load_students()
                elif hasattr(view, "load_categories"):
                    view.load_categories()
                elif hasattr(view, "load_receipts"):
                    view.load_receipts()
                elif hasattr(view, "load_sessions"):
                    view.load_sessions()
                if hasattr(view, "load_filter_options"):
                    view.load_filter_options()
            except Exception as e:
                pass
        self.status_bar.showMessage(f"Active Academic Session updated to {new_session}")

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        QShortcut(QKeySequence("Ctrl+P"), self, lambda: self.navigate_to("receipt"))
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.navigate_to("students_add"))
        QShortcut(QKeySequence("F5"), self, self.refresh_active_view)

    def show_login(self):
        self.sidebar_base.hide()
        self.sidebar_frame.hide()
        self.header_frame.hide()
        self.lbl_school_header.hide()
        self.btn_global_search.hide()
        self.lbl_status_user.setText("")
        self.lbl_status_user.hide()
        self.stacked_widget.setCurrentWidget(self.views["login"])

    def on_login_success(self):
        user = AuthController.get_current_user()
        if user:
            role_display = user.role.capitalize() if user.role else "User"
            self.lbl_status_user.setText(f"Logged in as: <b>{user.full_name}</b> ({role_display})")
            self.lbl_status_user.show()
        
        self.update_header_label()

        self.sidebar_base.show()
        self.sidebar_frame.show()
        self.header_frame.show()
        self.lbl_school_header.show()
        self.btn_global_search.show()
        self.sidebar_frame.raise_()
        self.navigate_to("dashboard")

        # Ensure collapsed state on startup and enable interactive hover
        self.collapse_sidebar(animated=False)
        self._hover_enabled = True

    # ---------------- HOVER & OVERLAY MOUSE EVENTS ----------------
    def on_sidebar_mouse_enter(self):
        if not getattr(self, "_hover_enabled", False):
            return
        if QApplication.platformName() == "offscreen" and not getattr(self, "_force_hover_expand", False):
            return
        if hasattr(self, "leave_timer") and self.leave_timer.isActive():
            self.leave_timer.stop()

        if not self.is_pinned and not self.sidebar_expanded:
            self.expand_sidebar(animated=True)

    def on_sidebar_mouse_leave(self):
        if not self.is_pinned and self.sidebar_expanded:
            self.leave_timer.start(200)

    def on_leave_timer_timeout(self):
        if self.is_pinned:
            return
        global_pos = QCursor.pos()
        local_pos = self.sidebar_frame.mapFromGlobal(global_pos)
        if not self.sidebar_frame.rect().contains(local_pos):
            self.collapse_sidebar(animated=True)

    def toggle_pin_mode(self):
        self.is_pinned = not self.is_pinned
        self.btn_pin.setChecked(self.is_pinned)
        if self.is_pinned:
            self.btn_pin.setText("📌")
            self.btn_pin.setToolTip("Unpin Sidebar (Hover Mode)")
            if not self.sidebar_expanded:
                self.expand_sidebar(animated=True)
        else:
            self.btn_pin.setText("📍")
            self.btn_pin.setToolTip("Pin Sidebar (Stay Expanded)")
            global_pos = QCursor.pos()
            local_pos = self.sidebar_frame.mapFromGlobal(global_pos)
            if not self.sidebar_frame.rect().contains(local_pos):
                self.collapse_sidebar(animated=True)

    def toggle_sidebar(self):
        """Toggle sidebar expansion state directly."""
        if self.sidebar_expanded:
            self.collapse_sidebar(animated=True)
        else:
            self.expand_sidebar(animated=True)

    def expand_sidebar(self, animated: bool = True):
        self.sidebar_expanded = True
        self.update_sidebar_visuals(animated=animated)

    def collapse_sidebar(self, animated: bool = True):
        self.sidebar_expanded = False
        self.update_sidebar_visuals(animated=animated)

    def update_sidebar_visuals(self, animated: bool = True):
        target_w = 250 if self.sidebar_expanded else 60
        parent_h = self.centralWidget().height() if self.centralWidget() else self.height()

        # Toggle Title Container & Pin Button Visibility
        if self.sidebar_expanded:
            self.title_container.show()
            self.btn_pin.show()
        else:
            self.title_container.hide()
            self.btn_pin.hide()

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

        start_geom = self.sidebar_frame.geometry()
        end_geom = QRect(0, 0, target_w, parent_h)

        if animated:
            if hasattr(self, "sidebar_anim") and self.sidebar_anim is not None:
                if self.sidebar_anim.state() == QPropertyAnimation.Running:
                    self.sidebar_anim.stop()

            self.sidebar_anim = QPropertyAnimation(self.sidebar_frame, b"geometry", self)
            self.sidebar_anim.setDuration(180)
            self.sidebar_anim.setStartValue(start_geom)
            self.sidebar_anim.setEndValue(end_geom)
            self.sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)

            def on_anim_finished():
                self.sidebar_frame.setGeometry(end_geom)
                self.sidebar_frame.raise_()

            self.sidebar_anim.finished.connect(on_anim_finished)
            self.sidebar_anim.start()
        else:
            self.sidebar_frame.setGeometry(end_geom)
            self.sidebar_frame.raise_()

    def on_nav_button_clicked(self, key: str):
        self.navigate_to(key)
        if not self.is_pinned and self.sidebar_expanded:
            self.collapse_sidebar(animated=True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.sidebar_expanded and not self.is_pinned:
                self.collapse_sidebar(animated=True)
                event.accept()
                return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "sidebar_frame") and self.sidebar_frame:
            curr_w = 250 if self.sidebar_expanded else 60
            parent_h = self.centralWidget().height() if self.centralWidget() else self.height()
            self.sidebar_frame.setGeometry(0, 0, curr_w, parent_h)
            self.sidebar_frame.raise_()

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
        if not AuthController.is_authenticated() or self.stacked_widget.currentWidget() == self.views.get("login"):
            return
        from dialogs.global_search_dialog import GlobalSearchDialog
        dlg = GlobalSearchDialog(self, on_navigate_callback=self.on_global_search_navigate)
        dlg.exec()

    def on_global_search_navigate(self, target_data: dict):
        t_view = target_data.get("target_view", "dashboard")

        # Map target view aliases to actual view keys in self.views
        if t_view in ("receipt_history", "history"):
            t_view = "history"
        elif t_view in ("fee_heads", "fees"):
            t_view = "fees"
        elif t_view in ("students", "student"):
            t_view = "students"

        self.navigate_to(t_view)

        if t_view == "reports" and "report_key" in target_data:
            report_view = self.views.get("reports")
            if hasattr(report_view, "open_report"):
                report_view.open_report(target_data["report_key"])

        elif t_view == "students" and target_data.get("title"):
            student_view = self.views.get("students")
            if hasattr(student_view, "txt_search"):
                student_view.txt_search.setText(target_data["title"])

        elif t_view == "history" and target_data.get("receipt_no"):
            history_view = self.views.get("history")
            if hasattr(history_view, "txt_search"):
                history_view.txt_search.setText(target_data["receipt_no"])

        elif t_view == "fees" and target_data.get("title"):
            fees_view = self.views.get("fees")
            if hasattr(fees_view, "txt_search"):
                fees_view.txt_search.setText(target_data["title"])

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
