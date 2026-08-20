"""
Professional Settings & Central Administration View for EduLedger ERP v1.7.0.
Features interactive Category Cards Dashboard and specialized administrative pages.
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QGroupBox, QFormLayout, QMessageBox, QFileDialog, QComboBox,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QCursor

import PySide6
from config.app_config import APP_NAME, APP_VERSION, COMPANY_NAME, DB_PATH, BACKUP_DIR, EXPORTS_DIR
from controllers.settings_controller import SettingsController
from controllers.auth_controller import AuthController
from controllers.academic_controller import AcademicController
from services.backup_service import BackupService
from services.export_service import ExportService
from dialogs.user_dialog import UserDialog
from dialogs.change_password_dialog import ChangePasswordDialog
from dialogs.course_dialog import CourseDialog
from dialogs.branch_dialog import BranchDialog
from dialogs.course_details_dialog import CourseDetailsDialog
from utils.logger import logger
from utils.table_delegate import apply_responsive_table_formatting


class CategoryCard(QFrame):
    """Clickable, visual Category Card for Settings Dashboard."""

    def __init__(self, icon: str, title: str, description: str, category_key: str, on_click_callback):
        super().__init__()
        self.category_key = category_key
        self.on_click_callback = on_click_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 14px;
            }
            QFrame:hover {
                border: 2px solid #2563eb;
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        hdr_layout = QHBoxLayout()
        hdr_layout.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 26px; background: transparent;")

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1e293b; background: transparent;")

        hdr_layout.addWidget(lbl_icon)
        hdr_layout.addWidget(lbl_title, stretch=1)

        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")

        btn_open = QPushButton("Open Category →")
        btn_open.setFixedHeight(30)
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
        btn_open.clicked.connect(lambda: self.on_click_callback(self.category_key))

        layout.addLayout(hdr_layout)
        layout.addWidget(lbl_desc, stretch=1)
        layout.addWidget(btn_open)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click_callback(self.category_key)
        super().mousePressEvent(event)


class SettingsView(QWidget):
    preferences_updated = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path_selected = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header Bar
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background-color: #1e3a8a; border-radius: 8px; padding: 12px 16px;")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)

        self.btn_back_dashboard = QPushButton("⬅ Back to Dashboard")
        self.btn_back_dashboard.setCursor(Qt.PointingHandCursor)
        self.btn_back_dashboard.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1e3a8a;
                font-weight: bold;
                border-radius: 5px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_back_dashboard.clicked.connect(self.show_dashboard)
        self.btn_back_dashboard.hide()

        self.lbl_header_title = QLabel("System Settings & Administration Panel")
        self.lbl_header_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800;")

        self.lbl_header_subtitle = QLabel("Central control panel for EduLedger ERP")
        self.lbl_header_subtitle.setStyleSheet("color: #93c5fd; font-size: 12px; font-weight: 600;")

        v_head = QVBoxLayout()
        v_head.setSpacing(2)
        v_head.addWidget(self.lbl_header_title)
        v_head.addWidget(self.lbl_header_subtitle)

        header_layout.addWidget(self.btn_back_dashboard)
        header_layout.addLayout(v_head, stretch=1)

        main_layout.addWidget(self.header_frame)

        # Stacked Widget for Router (Index 0 = Dashboard, 1 = School, 2 = Users, 3 = Academic, 4 = DB, 5 = Backup, 6 = Audit, 7 = Preferences, 8 = About)
        self.stack = QStackedWidget()

        # Page 0: Category Dashboard
        self.page_dashboard = QWidget()
        self.setup_dashboard_page()
        self.stack.addWidget(self.page_dashboard)

        # Page 1: School Information
        self.page_school = QWidget()
        self.setup_school_page()
        self.stack.addWidget(self.page_school)

        # Page 2: User Management
        self.page_users = QWidget()
        self.setup_users_page()
        self.stack.addWidget(self.page_users)

        # Page 3: Academic Settings
        self.page_academic = QWidget()
        self.setup_academic_page()
        self.stack.addWidget(self.page_academic)

        # Page 4: Database Management
        self.page_db = QWidget()
        self.setup_db_page()
        self.stack.addWidget(self.page_db)

        # Page 5: Backup & Restore
        self.page_backup = QWidget()
        self.setup_backup_page()
        self.stack.addWidget(self.page_backup)

        # Page 6: Audit Log Viewer
        self.page_audit = QWidget()
        self.setup_audit_page()
        self.stack.addWidget(self.page_audit)

        # Page 7: Application Preferences
        self.page_prefs = QWidget()
        self.setup_prefs_page()
        self.stack.addWidget(self.page_prefs)

        # Page 8: About Software
        self.page_about = QWidget()
        self.setup_about_page()
        self.stack.addWidget(self.page_about)

        main_layout.addWidget(self.stack)

        # Initial view
        self.show_dashboard()

    # ---------------- PAGE NAVIGATION ----------------
    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.lbl_header_title.setText("System Settings & Administration Panel")
        self.lbl_header_subtitle.setText("Central control panel for EduLedger ERP")
        self.btn_back_dashboard.hide()

    def open_category(self, key: str):
        page_map = {
            "school": (1, "School Information & Branding", "Manage school profile, contact, address, logo, and receipt text", self.load_school_info),
            "users": (2, "User Management & Accounts", "Manage system users, roles, password resets, and login tracking", self.load_users),
            "academic": (3, "Academic Session Settings", "Manage academic sessions and current active session", self.load_sessions),
            "db": (4, "Database Management & Integrity", "Database optimization, integrity checks, and statistics", self.load_db_stats),
            "backup": (5, "Database Backup & Disaster Recovery", "Immediate backups, restore, history, and scheduling", self.load_backup_history),
            "audit": (6, "Audit Logs & Security Viewer", "Filter, search, and export system audit events", self.load_audit_logs),
            "prefs": (7, "Application Preferences", "Window sizes, themes, printers, formats, and folders", self.load_preferences),
            "about": (8, "About EduLedger ERP", "Software versions, environment diagnostics, and license", self.load_about_info)
        }

        if key in page_map:
            idx, title, subtitle, refresh_fn = page_map[key]
            self.stack.setCurrentIndex(idx)
            self.lbl_header_title.setText(title)
            self.lbl_header_subtitle.setText(subtitle)
            self.btn_back_dashboard.show()
            if refresh_fn:
                refresh_fn()

    # ---------------- DASHBOARD PAGE ----------------
    def setup_dashboard_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        lbl_desc = QLabel("Select an administrative category below to configure system parameters, user permissions, database tools, and security options:")
        lbl_desc.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")
        layout.addWidget(lbl_desc)

        # 4x2 Grid of Cards
        grid = QGridLayout()
        grid.setSpacing(14)

        categories = [
            ("🏢", "School Information", "Configure school name, address, city, state, pin, contact numbers, logo, and receipt footer.", "school"),
            ("👥", "User Management", "Manage user accounts, assign Administrator/Operator/Viewer roles, reset passwords, and track logins.", "users"),
            ("🎓", "Academic Settings", "Configure academic sessions (e.g. 2024-2025), switch active sessions, and add new years.", "academic"),
            ("💾", "Database Management", "View database size, record counts, execute VACUUM optimization, and check SQLite integrity.", "db"),
            ("📦", "Backup & Restore", "Create instant database backups, restore safety snapshots, configure schedule, and review logs.", "backup"),
            ("📜", "Audit Log Viewer", "Inspect security logs, filter by user/module/date, search audit events, export CSV/Excel, and print.", "audit"),
            ("⚙️", "Application Preferences", "Configure window sizes, default folders, themes, currency symbols, printers, and date formats.", "prefs"),
            ("ℹ️", "About Software", "View system version, PySide6 runtime, Python version, SQLite engine, build metadata, and license.", "about")
        ]

        row, col = 0, 0
        for icon, title, desc, key in categories:
            card = CategoryCard(icon, title, desc, key, self.open_category)
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

    # ---------------- PAGE 1: SCHOOL INFORMATION ----------------
    def setup_school_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        group = QGroupBox("School Information & Receipt Branding Parameters")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.txt_school_name = QLineEdit()
        form.addRow("School / Institute Name *:", self.txt_school_name)

        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(50)
        form.addRow("Address Line *:", self.txt_address)

        self.txt_city = QLineEdit()
        form.addRow("City *:", self.txt_city)

        self.txt_state = QLineEdit()
        form.addRow("State / Region *:", self.txt_state)

        self.txt_pin = QLineEdit()
        form.addRow("PIN Code *:", self.txt_pin)

        self.txt_phone = QLineEdit()
        form.addRow("Contact Phone(s) *:", self.txt_phone)

        self.txt_email = QLineEdit()
        form.addRow("Email Address:", self.txt_email)

        self.txt_website = QLineEdit()
        form.addRow("Website URL:", self.txt_website)

        self.txt_principal = QLineEdit()
        form.addRow("Principal / Director Name:", self.txt_principal)

        # Logo Selector
        logo_layout = QHBoxLayout()
        self.lbl_logo_path = QLabel("No Logo Selected")
        self.lbl_logo_path.setStyleSheet("color: #64748b; font-style: italic;")
        self.btn_select_logo = QPushButton("Browse Logo...")
        self.btn_select_logo.setProperty("class", "SecondaryBtn")
        self.btn_select_logo.clicked.connect(self.select_logo)
        logo_layout.addWidget(self.lbl_logo_path, stretch=2)
        logo_layout.addWidget(self.btn_select_logo, stretch=1)
        form.addRow("School Logo Image:", logo_layout)

        self.txt_receipt_prefix = QLineEdit()
        form.addRow("Receipt Number Prefix:", self.txt_receipt_prefix)

        self.txt_receipt_footer = QTextEdit()
        self.txt_receipt_footer.setMaximumHeight(50)
        form.addRow("Receipt Footer Note:", self.txt_receipt_footer)

        layout.addWidget(group)

        # Save Button
        btn_save = QPushButton("💾   Save School Information & Profile")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: bold; font-size: 14px; border-radius: 6px;")
        btn_save.clicked.connect(self.save_school_info)
        layout.addWidget(btn_save)
        layout.addStretch()

        scroll.setWidget(container)
        p_layout = QVBoxLayout(self.page_school)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(scroll)

    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select School Logo Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            try:
                import shutil
                assets_dir = Path(__file__).resolve().parent.parent / "assets"
                assets_dir.mkdir(parents=True, exist_ok=True)
                ext = Path(path).suffix
                target_logo = assets_dir / f"school_logo{ext}"
                shutil.copy2(path, target_logo)
                rel_path = f"assets/school_logo{ext}"
                self.logo_path_selected = rel_path
                self.lbl_logo_path.setText(target_logo.name)
            except Exception as e:
                self.logo_path_selected = path
                self.lbl_logo_path.setText(Path(path).name)

    def load_school_info(self):
        info = SettingsController.get_school_info()
        if info:
            self.txt_school_name.setText(info.school_name)
            self.txt_address.setPlainText(info.address)
            self.txt_city.setText(getattr(info, 'city', '') or '')
            self.txt_state.setText(getattr(info, 'state', '') or '')
            self.txt_pin.setText(getattr(info, 'pin_code', '') or '')
            self.txt_phone.setText(info.phone)
            self.txt_email.setText(info.email)
            self.txt_website.setText(info.website or "")
            self.txt_principal.setText(getattr(info, 'principal_name', '') or '')
            self.txt_receipt_prefix.setText(info.receipt_prefix)
            self.txt_receipt_footer.setPlainText(info.receipt_footer)
            if info.logo_path:
                self.logo_path_selected = info.logo_path
                self.lbl_logo_path.setText(Path(info.logo_path).name)

    def save_school_info(self):
        name = self.txt_school_name.text().strip()
        address = self.txt_address.toPlainText().strip()
        phone = self.txt_phone.text().strip()

        if not name or not address or not phone:
            QMessageBox.warning(self, "Validation Error", "School Name, Address, and Phone are required.")
            return

        data = {
            "school_name": name,
            "address": address,
            "city": self.txt_city.text().strip(),
            "state": self.txt_state.text().strip(),
            "pin_code": self.txt_pin.text().strip(),
            "phone": phone,
            "email": self.txt_email.text().strip(),
            "website": self.txt_website.text().strip(),
            "principal_name": self.txt_principal.text().strip(),
            "logo_path": self.logo_path_selected,
            "receipt_prefix": self.txt_receipt_prefix.text().strip(),
            "receipt_footer": self.txt_receipt_footer.toPlainText().strip()
        }

        success, msg = SettingsController.update_school_info(data)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    # ---------------- PAGE 2: USER MANAGEMENT ----------------
    def setup_users_page(self):
        layout = QVBoxLayout(self.page_users)
        layout.setContentsMargins(4, 4, 4, 4)

        hdr = QHBoxLayout()
        lbl_info = QLabel("Registered System Accounts & Permission Roles")
        lbl_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e3a8a;")
        hdr.addWidget(lbl_info)
        hdr.addStretch()

        self.btn_add_user = QPushButton("+ Add System User")
        self.btn_add_user.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 5px;")
        self.btn_add_user.clicked.connect(self.add_user)

        self.btn_edit_user = QPushButton("✏ Edit User")
        self.btn_edit_user.setProperty("class", "SecondaryBtn")
        self.btn_edit_user.clicked.connect(self.edit_user)

        self.btn_toggle_status = QPushButton("🔄 Disable/Enable")
        self.btn_toggle_status.setProperty("class", "SecondaryBtn")
        self.btn_toggle_status.clicked.connect(self.toggle_user_status)

        self.btn_reset_pwd = QPushButton("🔑 Reset Password")
        self.btn_reset_pwd.setProperty("class", "SecondaryBtn")
        self.btn_reset_pwd.clicked.connect(self.reset_user_password)

        self.btn_delete_user = QPushButton("🗑 Delete User")
        self.btn_delete_user.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 6px 12px; border-radius: 5px;")
        self.btn_delete_user.clicked.connect(self.delete_user)

        hdr.addWidget(self.btn_add_user)
        hdr.addWidget(self.btn_edit_user)
        hdr.addWidget(self.btn_toggle_status)
        hdr.addWidget(self.btn_reset_pwd)
        hdr.addWidget(self.btn_delete_user)

        layout.addLayout(hdr)

        self.table_users = QTableWidget()
        self.table_users.setColumnCount(6)
        self.table_users.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Status", "Last Login"])
        self.table_users.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_users.setSelectionMode(QTableWidget.SingleSelection)
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        apply_responsive_table_formatting(self.table_users)
        layout.addWidget(self.table_users)

    def load_users(self):
        users = AuthController.get_all_users()
        self.table_users.setRowCount(len(users))

        for idx, u in enumerate(users):
            item_id = QTableWidgetItem(str(u.id))
            item_user = QTableWidgetItem(u.username)
            item_name = QTableWidgetItem(u.full_name)
            item_role = QTableWidgetItem("Administrator" if u.role in ("Admin", "Administrator") else u.role)
            item_status = QTableWidgetItem(u.status)
            
            last_login_str = u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never"
            item_login = QTableWidgetItem(last_login_str)

            if u.status != "Active":
                item_status.setForeground(Qt.red)

            self.table_users.setItem(idx, 0, item_id)
            self.table_users.setItem(idx, 1, item_user)
            self.table_users.setItem(idx, 2, item_name)
            self.table_users.setItem(idx, 3, item_role)
            self.table_users.setItem(idx, 4, item_status)
            self.table_users.setItem(idx, 5, item_login)

    def get_selected_user(self):
        row = self.table_users.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a user row first.")
            return None
        user_id = int(self.table_users.item(row, 0).text())
        users = AuthController.get_all_users()
        for u in users:
            if u.id == user_id:
                return u
        return None

    def add_user(self):
        dlg = UserDialog(self)
        if dlg.exec():
            self.load_users()

    def edit_user(self):
        user = self.get_selected_user()
        if not user:
            return
        dlg = UserDialog(self, user_data=user)
        if dlg.exec():
            self.load_users()

    def toggle_user_status(self):
        user = self.get_selected_user()
        if not user:
            return
        new_status = "Disabled" if user.status == "Active" else "Active"
        success, msg = AuthController.update_user(user.id, user.full_name, user.role, new_status)
        if success:
            QMessageBox.information(self, "Success", f"User '{user.username}' status set to {new_status}.")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", msg)

    def reset_user_password(self):
        user = self.get_selected_user()
        if not user:
            return
        dlg = ChangePasswordDialog(self, user_id=user.id, username=user.username, is_admin_reset=True)
        dlg.exec()

    def delete_user(self):
        user = self.get_selected_user()
        if not user:
            return
        if not AuthController.is_admin():
            QMessageBox.warning(self, "Access Denied", "Only Administrators can delete user accounts.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to permanently delete user '{user.username}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = AuthController.delete_user(user.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_users()
            else:
                QMessageBox.critical(self, "Error", msg)

    # ---------------- PAGE 3: ACADEMIC SETTINGS ----------------
    def setup_academic_page(self):
        main_layout = QVBoxLayout(self.page_academic)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # Tabbed Container for Academic Master Modules
        self.academic_tabs = QTabWidget()
        self.academic_tabs.setStyleSheet("""
            QTabBar::tab {
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
            }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)

        # --- TAB 1: COURSES & PROGRAM MASTER ---
        tab_crs = QWidget()
        vbox_tab1 = QVBoxLayout(tab_crs)
        vbox_tab1.setContentsMargins(6, 6, 6, 6)
        vbox_tab1.setSpacing(8)

        # Course Action Toolbar
        hdr_crs = QHBoxLayout()
        hdr_crs.setSpacing(8)

        self.chk_course_select_all = QCheckBox("Select All")
        self.chk_course_select_all.setStyleSheet("font-weight: bold; font-size: 12px; color: #1e3a8a;")
        self.chk_course_select_all.toggled.connect(self.toggle_select_all_courses)

        self.lbl_course_selected_count = QLabel("Selected: 0")
        self.lbl_course_selected_count.setStyleSheet("font-weight: bold; color: #475569; font-size: 12px;")

        self.btn_course_bulk_active = QPushButton("⚡ Mark Selected Active")
        self.btn_course_bulk_active.setStyleSheet("background-color: #059669; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_course_bulk_active.setCursor(Qt.PointingHandCursor)
        self.btn_course_bulk_active.clicked.connect(lambda: self.bulk_set_course_status(True))

        self.btn_course_bulk_inactive = QPushButton("⏸ Mark Selected Inactive")
        self.btn_course_bulk_inactive.setStyleSheet("background-color: #d97706; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_course_bulk_inactive.setCursor(Qt.PointingHandCursor)
        self.btn_course_bulk_inactive.clicked.connect(lambda: self.bulk_set_course_status(False))

        self.btn_course_bulk_delete = QPushButton("🗑 Delete Selected")
        self.btn_course_bulk_delete.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_course_bulk_delete.setCursor(Qt.PointingHandCursor)
        self.btn_course_bulk_delete.clicked.connect(self.bulk_delete_courses)

        self.btn_add_course = QPushButton("+ Add New Course Program")
        self.btn_add_course.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 5px;")
        self.btn_add_course.setCursor(Qt.PointingHandCursor)
        self.btn_add_course.clicked.connect(self.add_course)

        hdr_crs.addWidget(self.chk_course_select_all)
        hdr_crs.addWidget(self.lbl_course_selected_count)
        hdr_crs.addWidget(self.btn_course_bulk_active)
        hdr_crs.addWidget(self.btn_course_bulk_inactive)
        hdr_crs.addWidget(self.btn_course_bulk_delete)
        hdr_crs.addStretch()
        hdr_crs.addWidget(self.btn_add_course)
        vbox_tab1.addLayout(hdr_crs)

        # Course Table (11 Columns: Checkbox, ID, Code, Name, Type, Department, Duration, Semesters, Baseline Fee, Status, Actions)
        self.table_courses = QTableWidget()
        self.table_courses.setColumnCount(11)
        self.table_courses.setHorizontalHeaderLabels([
            "☐", "ID", "Code", "Course Name", "Type", "Department", "Duration", "Semesters", "Baseline Fee", "Status", "Actions"
        ])
        
        header_crs = self.table_courses.horizontalHeader()
        header_crs.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Checkbox
        header_crs.setSectionResizeMode(1, QHeaderView.ResizeToContents) # ID
        header_crs.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Code
        header_crs.setSectionResizeMode(3, QHeaderView.Stretch)          # Name
        header_crs.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Type
        header_crs.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Dept
        header_crs.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Duration
        header_crs.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Semesters
        header_crs.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Fee
        header_crs.setSectionResizeMode(9, QHeaderView.ResizeToContents) # Status
        header_crs.setSectionResizeMode(10, QHeaderView.ResizeToContents) # Actions
        self.table_courses.itemChanged.connect(self.update_course_selection_count)
        apply_responsive_table_formatting(self.table_courses)
        vbox_tab1.addWidget(self.table_courses)

        self.academic_tabs.addTab(tab_crs, "🎓 Course Programs Master")

        # --- TAB 2: SPECIALIZATION BRANCHES ---
        tab_br = QWidget()
        vbox_tab2 = QVBoxLayout(tab_br)
        vbox_tab2.setContentsMargins(6, 6, 6, 6)
        vbox_tab2.setSpacing(8)

        # Branch Action Toolbar
        hdr_br = QHBoxLayout()
        hdr_br.setSpacing(8)

        self.chk_branch_select_all = QCheckBox("Select All")
        self.chk_branch_select_all.setStyleSheet("font-weight: bold; font-size: 12px; color: #1e3a8a;")
        self.chk_branch_select_all.toggled.connect(self.toggle_select_all_branches)

        self.lbl_branch_selected_count = QLabel("Selected: 0")
        self.lbl_branch_selected_count.setStyleSheet("font-weight: bold; color: #475569; font-size: 12px;")

        self.btn_branch_bulk_active = QPushButton("⚡ Mark Selected Active")
        self.btn_branch_bulk_active.setStyleSheet("background-color: #059669; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_branch_bulk_active.setCursor(Qt.PointingHandCursor)
        self.btn_branch_bulk_active.clicked.connect(lambda: self.bulk_set_branch_status(True))

        self.btn_branch_bulk_inactive = QPushButton("⏸ Mark Selected Inactive")
        self.btn_branch_bulk_inactive.setStyleSheet("background-color: #d97706; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_branch_bulk_inactive.setCursor(Qt.PointingHandCursor)
        self.btn_branch_bulk_inactive.clicked.connect(lambda: self.bulk_set_branch_status(False))

        self.btn_branch_bulk_delete = QPushButton("🗑 Delete Selected")
        self.btn_branch_bulk_delete.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold; font-size: 11px; padding: 5px 10px; border-radius: 4px;")
        self.btn_branch_bulk_delete.setCursor(Qt.PointingHandCursor)
        self.btn_branch_bulk_delete.clicked.connect(self.bulk_delete_branches)

        self.btn_add_branch = QPushButton("+ Add New Branch")
        self.btn_add_branch.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 5px;")
        self.btn_add_branch.setCursor(Qt.PointingHandCursor)
        self.btn_add_branch.clicked.connect(self.add_branch)

        hdr_br.addWidget(self.chk_branch_select_all)
        hdr_br.addWidget(self.lbl_branch_selected_count)
        hdr_br.addWidget(self.btn_branch_bulk_active)
        hdr_br.addWidget(self.btn_branch_bulk_inactive)
        hdr_br.addWidget(self.btn_branch_bulk_delete)
        hdr_br.addStretch()
        hdr_br.addWidget(self.btn_add_branch)
        vbox_tab2.addLayout(hdr_br)

        # Branch Table (7 Columns: Checkbox, ID, Code, Branch Name, Linked Course, Status, Actions)
        self.table_branches = QTableWidget()
        self.table_branches.setColumnCount(7)
        self.table_branches.setHorizontalHeaderLabels([
            "☐", "ID", "Code", "Branch Name", "Linked Course", "Status", "Actions"
        ])

        header_br = self.table_branches.horizontalHeader()
        header_br.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Checkbox
        header_br.setSectionResizeMode(1, QHeaderView.ResizeToContents) # ID
        header_br.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Code
        header_br.setSectionResizeMode(3, QHeaderView.Stretch)          # Branch Name
        header_br.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Course
        header_br.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Status
        header_br.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Actions
        self.table_branches.itemChanged.connect(self.update_branch_selection_count)
        apply_responsive_table_formatting(self.table_branches)
        vbox_tab2.addWidget(self.table_branches)

        self.academic_tabs.addTab(tab_br, "🌿 Specialization Branches")

        # --- TAB 3: ACADEMIC SESSIONS ---
        tab_sess = QWidget()
        vbox_tab3 = QVBoxLayout(tab_sess)
        vbox_tab3.setContentsMargins(6, 6, 6, 6)

        hdr_sess = QHBoxLayout()
        hdr_sess.addWidget(QLabel("Configure active operational academic session year for student registration & billing:"))
        hdr_sess.addStretch()

        self.btn_add_session = QPushButton("+ Add New Academic Session")
        self.btn_add_session.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 5px;")
        self.btn_add_session.setCursor(Qt.PointingHandCursor)
        self.btn_add_session.clicked.connect(self.add_session)
        hdr_sess.addWidget(self.btn_add_session)
        vbox_tab3.addLayout(hdr_sess)

        self.table_sessions = QTableWidget()
        self.table_sessions.setColumnCount(3)
        self.table_sessions.setHorizontalHeaderLabels(["Session Name", "Is Active Current Session", "Action"])
        self.table_sessions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        apply_responsive_table_formatting(self.table_sessions)
        vbox_tab3.addWidget(self.table_sessions)

        self.academic_tabs.addTab(tab_sess, "📅 Academic Sessions")

        main_layout.addWidget(self.academic_tabs)

    def load_sessions(self):
        sessions = SettingsController.get_academic_sessions()
        self.table_sessions.setRowCount(len(sessions))

        for idx, s in enumerate(sessions):
            self.table_sessions.setItem(idx, 0, QTableWidgetItem(s.session_name))
            self.table_sessions.setItem(idx, 1, QTableWidgetItem("Yes (Active Current)" if s.is_current else "No"))

            if not s.is_current:
                btn_set = QPushButton("Make Current Session")
                btn_set.setProperty("class", "SecondaryBtn")
                btn_set.setCursor(Qt.PointingHandCursor)
                btn_set.clicked.connect(lambda _, sname=s.session_name: self.set_current_session(sname))
                self.table_sessions.setCellWidget(idx, 2, btn_set)
            else:
                lbl_active = QLabel("✓ Currently Active")
                lbl_active.setStyleSheet("font-weight: bold; color: #10b981; padding-left: 10px;")
                self.table_sessions.setCellWidget(idx, 2, lbl_active)

        self.load_courses()
        self.load_branches()

    def add_session(self):
        from PySide6.QtWidgets import QInputDialog
        session_name, ok = QInputDialog.getText(self, "New Academic Session", "Enter Academic Session Name (e.g. 2025-2026):")
        if ok and session_name.strip():
            SettingsController.set_current_session(session_name.strip())
            self.load_sessions()

    def set_current_session(self, sname: str):
        success, msg = SettingsController.set_current_session(sname)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_sessions()
        else:
            QMessageBox.critical(self, "Error", msg)

    def load_courses(self):
        self.table_courses.blockSignals(True)
        courses = AcademicController.get_all_courses_full()
        self.table_courses.setRowCount(len(courses))

        for idx, c in enumerate(courses):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, c.id)
            self.table_courses.setItem(idx, 0, chk_item)

            self.table_courses.setItem(idx, 1, QTableWidgetItem(str(c.id)))
            self.table_courses.setItem(idx, 2, QTableWidgetItem(c.code))
            self.table_courses.setItem(idx, 3, QTableWidgetItem(c.name))
            self.table_courses.setItem(idx, 4, QTableWidgetItem(c.course_type or "UG"))
            self.table_courses.setItem(idx, 5, QTableWidgetItem(getattr(c, "department", "General") or "General"))
            self.table_courses.setItem(idx, 6, QTableWidgetItem(f"{c.duration_years} Years"))
            self.table_courses.setItem(idx, 7, QTableWidgetItem(f"{c.total_semesters} Semesters"))
            
            fee_val = getattr(c, "baseline_annual_fee", 0.0) or 0.0
            fee_str = f"₹ {fee_val:,.0f}" if fee_val > 0 else "-"
            self.table_courses.setItem(idx, 8, QTableWidgetItem(fee_str))

            status_item = QTableWidgetItem("Active" if c.is_active else "Inactive")
            if not c.is_active:
                status_item.setForeground(Qt.red)
            self.table_courses.setItem(idx, 9, status_item)

            btn_box = QWidget()
            btn_layout = QHBoxLayout(btn_box)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(6)

            btn_details = QPushButton("👁 Details")
            btn_details.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; font-size: 11px; padding: 4px 10px; border-radius: 4px;")
            btn_details.setCursor(Qt.PointingHandCursor)
            btn_details.clicked.connect(lambda _, crs=c: self.view_course_details(crs))

            btn_edit = QPushButton("✏ Edit")
            btn_edit.setProperty("class", "SecondaryBtn")
            btn_edit.setStyleSheet("font-weight: bold; font-size: 11px; padding: 4px 10px; border-radius: 4px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, crs=c: self.edit_course(crs))

            btn_delete = QPushButton("🗑 Delete")
            btn_delete.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold; font-size: 11px; padding: 4px 10px; border-radius: 4px;")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda _, crs=c: self.delete_single_course(crs))

            btn_layout.addWidget(btn_details)
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            self.table_courses.setCellWidget(idx, 10, btn_box)

        self.table_courses.blockSignals(False)
        self.update_course_selection_count()

    def toggle_select_all_courses(self, checked: bool):
        self.table_courses.blockSignals(True)
        state = Qt.Checked if checked else Qt.Unchecked
        for r in range(self.table_courses.rowCount()):
            chk = self.table_courses.item(r, 0)
            if chk:
                chk.setCheckState(state)
        self.table_courses.blockSignals(False)
        self.update_course_selection_count()

    def get_selected_course_ids(self) -> List[int]:
        selected_ids = []
        for r in range(self.table_courses.rowCount()):
            chk = self.table_courses.item(r, 0)
            if chk and chk.checkState() == Qt.Checked:
                cid = chk.data(Qt.UserRole)
                if cid:
                    selected_ids.append(int(cid))
        return selected_ids

    def update_course_selection_count(self):
        count = len(self.get_selected_course_ids())
        self.lbl_course_selected_count.setText(f"Selected: {count}")

    def bulk_set_course_status(self, is_active: bool):
        cids = self.get_selected_course_ids()
        if not cids:
            QMessageBox.warning(self, "Selection Required", "Please select at least one course using checkboxes.")
            return
        
        action_name = "Active" if is_active else "Inactive"
        updated_count = 0
        for cid in cids:
            ok, _ = AcademicController.set_course_status(cid, is_active)
            if ok:
                updated_count += 1

        QMessageBox.information(self, "Success", f"Marked {updated_count} course program(s) as {action_name}.")
        self.chk_course_select_all.setChecked(False)
        self.load_courses()

    def bulk_delete_courses(self):
        cids = self.get_selected_course_ids()
        if not cids:
            QMessageBox.warning(self, "Selection Required", "Please select at least one course using checkboxes.")
            return

        reply = QMessageBox.question(
            self, "Confirm Bulk Delete",
            f"Are you sure you want to permanently delete {len(cids)} selected course program(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            deleted_count = 0
            err_msgs = []
            for cid in cids:
                ok, msg = AcademicController.delete_course(cid)
                if ok:
                    deleted_count += 1
                else:
                    err_msgs.append(msg)
            
            if deleted_count > 0:
                QMessageBox.information(self, "Bulk Delete Result", f"Successfully deleted {deleted_count} course program(s).")
            if err_msgs:
                QMessageBox.warning(self, "Errors Encountered", "\n".join(err_msgs[:5]))
            
            self.chk_course_select_all.setChecked(False)
            self.load_courses()

    def view_course_details(self, course_data):
        dlg = CourseDetailsDialog(self, course_data=course_data)
        if dlg.exec():
            self.load_courses()

    def add_course(self):
        dlg = CourseDialog(self)
        if dlg.exec():
            self.load_courses()

    def edit_course(self, course_data):
        dlg = CourseDialog(self, course_data=course_data)
        if dlg.exec():
            self.load_courses()

    def delete_single_course(self, course_data):
        reply = QMessageBox.question(
            self, "Confirm Delete Course",
            f"Are you sure you want to permanently delete course program '{course_data.name}' ({course_data.code})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = AcademicController.delete_course(course_data.id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses()
            else:
                QMessageBox.critical(self, "Error", msg)

    def load_branches(self):
        self.table_branches.blockSignals(True)
        branches = AcademicController.get_all_branches_full()
        self.table_branches.setRowCount(len(branches))

        for idx, b in enumerate(branches):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Unchecked)
            chk_item.setData(Qt.UserRole, b.id)
            self.table_branches.setItem(idx, 0, chk_item)

            self.table_branches.setItem(idx, 1, QTableWidgetItem(str(b.id)))
            self.table_branches.setItem(idx, 2, QTableWidgetItem(b.code))
            self.table_branches.setItem(idx, 3, QTableWidgetItem(b.name))
            self.table_branches.setItem(idx, 4, QTableWidgetItem(b.course_code or "All Courses"))
            
            status_item = QTableWidgetItem("Active" if b.is_active else "Inactive")
            if not b.is_active:
                status_item.setForeground(Qt.red)
            self.table_branches.setItem(idx, 5, status_item)

            btn_box = QWidget()
            btn_layout = QHBoxLayout(btn_box)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(6)

            btn_edit = QPushButton("✏ Edit")
            btn_edit.setProperty("class", "SecondaryBtn")
            btn_edit.setStyleSheet("font-weight: bold; font-size: 11px; padding: 4px 10px; border-radius: 4px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, br=b: self.edit_branch(br))

            btn_delete = QPushButton("🗑 Delete")
            btn_delete.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold; font-size: 11px; padding: 4px 10px; border-radius: 4px;")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda _, br=b: self.delete_branch(br.id, br.name))

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            self.table_branches.setCellWidget(idx, 6, btn_box)

        self.table_branches.blockSignals(False)
        self.update_branch_selection_count()

    def toggle_select_all_branches(self, checked: bool):
        self.table_branches.blockSignals(True)
        state = Qt.Checked if checked else Qt.Unchecked
        for r in range(self.table_branches.rowCount()):
            chk = self.table_branches.item(r, 0)
            if chk:
                chk.setCheckState(state)
        self.table_branches.blockSignals(False)
        self.update_branch_selection_count()

    def get_selected_branch_ids(self) -> List[int]:
        selected_ids = []
        for r in range(self.table_branches.rowCount()):
            chk = self.table_branches.item(r, 0)
            if chk and chk.checkState() == Qt.Checked:
                bid = chk.data(Qt.UserRole)
                if bid:
                    selected_ids.append(int(bid))
        return selected_ids

    def update_branch_selection_count(self):
        count = len(self.get_selected_branch_ids())
        self.lbl_branch_selected_count.setText(f"Selected: {count}")

    def bulk_set_branch_status(self, is_active: bool):
        bids = self.get_selected_branch_ids()
        if not bids:
            QMessageBox.warning(self, "Selection Required", "Please select at least one branch using checkboxes.")
            return
        
        action_name = "Active" if is_active else "Inactive"
        updated_count = 0
        for bid in bids:
            ok, _ = AcademicController.set_branch_status(bid, is_active)
            if ok:
                updated_count += 1

        QMessageBox.information(self, "Success", f"Marked {updated_count} branch(es) as {action_name}.")
        self.chk_branch_select_all.setChecked(False)
        self.load_branches()

    def bulk_delete_branches(self):
        bids = self.get_selected_branch_ids()
        if not bids:
            QMessageBox.warning(self, "Selection Required", "Please select at least one branch using checkboxes.")
            return

        reply = QMessageBox.question(
            self, "Confirm Bulk Delete",
            f"Are you sure you want to permanently delete {len(bids)} selected branch(es)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            deleted_count = 0
            err_msgs = []
            for bid in bids:
                ok, msg = AcademicController.delete_branch(bid)
                if ok:
                    deleted_count += 1
                else:
                    err_msgs.append(msg)
            
            if deleted_count > 0:
                QMessageBox.information(self, "Bulk Delete Result", f"Successfully deleted {deleted_count} branch(es).")
            if err_msgs:
                QMessageBox.warning(self, "Errors Encountered", "\n".join(err_msgs[:5]))
            
            self.chk_branch_select_all.setChecked(False)
            self.load_branches()

    def add_branch(self):
        dlg = BranchDialog(self)
        if dlg.exec():
            self.load_branches()

    def edit_branch(self, branch_data):
        dlg = BranchDialog(self, branch_data=branch_data)
        if dlg.exec():
            self.load_branches()

    def toggle_branch_status(self, branch_id: int):
        success, msg = AcademicController.toggle_branch_status(branch_id)
        if success:
            self.load_branches()
        else:
            QMessageBox.critical(self, "Error", msg)

    def delete_branch(self, branch_id: int, branch_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete branch '{branch_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = AcademicController.delete_branch(branch_id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_branches()
            else:
                QMessageBox.critical(self, "Error", msg)

    # ---------------- PAGE 4: DATABASE MANAGEMENT ----------------
    def setup_db_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(14)

        # Database Statistics Box
        box_stats = QGroupBox("Database Health & Summary Statistics")
        form_stats = QFormLayout(box_stats)
        form_stats.setSpacing(10)

        self.lbl_db_path = QLabel("-")
        self.lbl_db_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form_stats.addRow("Database Storage Path:", self.lbl_db_path)

        self.lbl_db_size = QLabel("-")
        form_stats.addRow("File Size on Disk:", self.lbl_db_size)

        self.lbl_stat_students = QLabel("-")
        form_stats.addRow("Total Enrolled Students:", self.lbl_stat_students)

        self.lbl_stat_receipts = QLabel("-")
        form_stats.addRow("Total Fee Receipts Recorded:", self.lbl_stat_receipts)

        self.lbl_stat_feeheads = QLabel("-")
        form_stats.addRow("Configured Fee Heads:", self.lbl_stat_feeheads)

        self.lbl_stat_users = QLabel("-")
        form_stats.addRow("Registered System Users:", self.lbl_stat_users)

        self.lbl_stat_audit = QLabel("-")
        form_stats.addRow("Recorded Audit Logs:", self.lbl_stat_audit)

        layout.addWidget(box_stats)

        # Action Tools
        box_tools = QGroupBox("Database Maintenance & Maintenance Tools")
        layout_tools = QHBoxLayout(box_tools)

        self.btn_optimize_db = QPushButton("⚡  Optimize Database (VACUUM)")
        self.btn_optimize_db.setFixedHeight(38)
        self.btn_optimize_db.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_optimize_db.clicked.connect(self.run_optimize_db)

        self.btn_repair_db = QPushButton("🔧  Repair Database (REINDEX)")
        self.btn_repair_db.setFixedHeight(38)
        self.btn_repair_db.setProperty("class", "SecondaryBtn")
        self.btn_repair_db.clicked.connect(self.run_repair_db)

        self.btn_verify_db = QPushButton("🔍  Verify Database Integrity")
        self.btn_verify_db.setFixedHeight(38)
        self.btn_verify_db.setProperty("class", "SecondaryBtn")
        self.btn_verify_db.clicked.connect(self.run_verify_db)

        layout_tools.addWidget(self.btn_optimize_db)
        layout_tools.addWidget(self.btn_repair_db)
        layout_tools.addWidget(self.btn_verify_db)

        layout.addWidget(box_tools)
        layout.addStretch()

        scroll.setWidget(container)
        p_layout = QVBoxLayout(self.page_db)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(scroll)

    def load_db_stats(self):
        stats = SettingsController.get_database_stats()
        self.lbl_db_path.setText(stats["db_path"])
        self.lbl_db_size.setText(stats["db_size"])
        self.lbl_stat_students.setText(str(stats["student_count"]))
        self.lbl_stat_receipts.setText(str(stats["receipt_count"]))
        self.lbl_stat_feeheads.setText(str(stats["fee_head_count"]))
        self.lbl_stat_users.setText(str(stats["user_count"]))
        self.lbl_stat_audit.setText(str(stats["audit_count"]))

    def run_optimize_db(self):
        success, msg = SettingsController.optimize_database()
        if success:
            QMessageBox.information(self, "Database Optimization Complete", msg)
            self.load_db_stats()
        else:
            QMessageBox.critical(self, "Optimization Error", msg)

    def run_repair_db(self):
        success, msg = BackupService.repair_database()
        if success:
            QMessageBox.information(self, "Database Repair Complete", msg)
            self.load_db_stats()
        else:
            QMessageBox.critical(self, "Repair Error", msg)

    def run_verify_db(self):
        success, msg = SettingsController.verify_database_integrity()
        if success:
            QMessageBox.information(self, "Integrity Verification Passed", msg)
        else:
            QMessageBox.critical(self, "Integrity Verification Issue", msg)

    # ---------------- PAGE 5: BACKUP & RESTORE ----------------
    def setup_backup_page(self):
        layout = QVBoxLayout(self.page_backup)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        box_actions = QGroupBox("Instant Backup & Restore Actions")
        h_act = QHBoxLayout(box_actions)

        self.btn_backup_now = QPushButton("📦  Create Immediate Backup ZIP")
        self.btn_backup_now.setFixedHeight(40)
        self.btn_backup_now.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_backup_now.clicked.connect(self.run_backup)

        self.btn_restore_now = QPushButton("🚨  Restore Database from ZIP")
        self.btn_restore_now.setFixedHeight(40)
        self.btn_restore_now.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_restore_now.clicked.connect(self.run_restore)

        h_act.addWidget(self.btn_backup_now)
        h_act.addWidget(self.btn_restore_now)
        layout.addWidget(box_actions)

        # Auto Backup Preferences Panel
        box_auto = QGroupBox("Automatic Backup & Retention Schedule")
        h_auto = QHBoxLayout(box_auto)
        h_auto.setSpacing(12)

        self.chk_auto_backup = QCheckBox("Enable Automatic Scheduled Backups")
        self.chk_auto_backup.setChecked(True)

        self.cmb_auto_freq = QComboBox()
        self.cmb_auto_freq.addItems(["Daily", "Weekly", "Monthly"])

        self.cmb_auto_retention = QComboBox()
        self.cmb_auto_retention.addItems(["5", "10", "20", "Unlimited"])

        self.btn_save_auto = QPushButton("💾 Save Schedule")
        self.btn_save_auto.setFixedHeight(32)
        self.btn_save_auto.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 5px; padding: 0 12px;")
        self.btn_save_auto.clicked.connect(self.save_auto_backup_prefs)

        h_auto.addWidget(self.chk_auto_backup)
        h_auto.addWidget(QLabel("Frequency:"))
        h_auto.addWidget(self.cmb_auto_freq)
        h_auto.addWidget(QLabel("Retention (Backups to Keep):"))
        h_auto.addWidget(self.cmb_auto_retention)
        h_auto.addWidget(self.btn_save_auto)

        layout.addWidget(box_auto)

        # Backup History Table
        box_hist = QGroupBox("Database Backup Archive History")
        v_hist = QVBoxLayout(box_hist)

        self.table_backup_history = QTableWidget()
        self.table_backup_history.setColumnCount(5)
        self.table_backup_history.setHorizontalHeaderLabels(["Filename", "Size", "Type", "Created By", "Timestamp"])
        self.table_backup_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        apply_responsive_table_formatting(self.table_backup_history)
        v_hist.addWidget(self.table_backup_history)

        layout.addWidget(box_hist)

        self.load_auto_backup_prefs()

    def load_auto_backup_prefs(self):
        prefs = SettingsController.get_app_preferences()
        self.chk_auto_backup.setChecked(prefs.get("auto_backup_enabled", True))
        self.cmb_auto_freq.setCurrentText(prefs.get("auto_backup_frequency", "Daily"))
        self.cmb_auto_retention.setCurrentText(str(prefs.get("backup_retention", "10")))

    def save_auto_backup_prefs(self):
        prefs = SettingsController.get_app_preferences()
        prefs["auto_backup_enabled"] = self.chk_auto_backup.isChecked()
        prefs["auto_backup_frequency"] = self.cmb_auto_freq.currentText()
        prefs["backup_retention"] = self.cmb_auto_retention.currentText()

        success, msg = SettingsController.save_app_preferences(prefs)
        if success:
            QMessageBox.information(self, "Success", "Auto-backup schedule and retention preferences saved successfully.")
        else:
            QMessageBox.critical(self, "Error", msg)

    def load_backup_history(self):
        db = SettingsController.get_db() if hasattr(SettingsController, "get_db") else None
        if not db:
            from config.database import get_db
            db = get_db()
        try:
            from models.audit import BackupHistory
            backups = db.query(BackupHistory).order_by(BackupHistory.created_at.desc()).all()
            self.table_backup_history.setRowCount(len(backups))

            for idx, b in enumerate(backups):
                self.table_backup_history.setItem(idx, 0, QTableWidgetItem(b.filename))
                self.table_backup_history.setItem(idx, 1, QTableWidgetItem(b.file_size))
                self.table_backup_history.setItem(idx, 2, QTableWidgetItem(b.backup_type))
                self.table_backup_history.setItem(idx, 3, QTableWidgetItem(getattr(b, 'created_by', 'Administrator') or 'Administrator'))
                self.table_backup_history.setItem(idx, 4, QTableWidgetItem(b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else ""))
        finally:
            db.close()

    def run_backup(self):
        success, msg, path = BackupService.create_backup()
        if success:
            QMessageBox.information(self, "Backup Successful", f"{msg}\nSaved at: {path}")
            self.load_backup_history()
        else:
            QMessageBox.critical(self, "Backup Failed", msg)

    def run_restore(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup Zip File to Restore", "", "Zip Files (*.zip)")
        if not file_path:
            return

        # Preview Backup Archive details before restoring
        preview = BackupService.get_backup_preview(file_path)
        if not preview.get("valid"):
            QMessageBox.critical(self, "Corrupted Backup File", preview.get("message", "Invalid backup archive."))
            return

        prompt_msg = (
            f"<b>=== BACKUP ARCHIVE PREVIEW ===</b><br><br>"
            f"• <b>Filename</b>: {preview['filename']}<br>"
            f"• <b>Archive Date</b>: {preview['date']}<br>"
            f"• <b>Archive Size</b>: {preview['size']}<br>"
            f"• <b>Database Included</b>: {'Yes ✓' if preview['has_db'] else 'No ❌'}<br>"
            f"• <b>Settings Included</b>: {'Yes ✓' if preview['has_settings'] else 'No ❌'}<br><br>"
            f"<span style='color: #dc2626;'><b>CRITICAL WARNING:</b> Restoring will replace active database records.<br>"
            f"A safety snapshot of your current database will be created automatically.</span><br><br>"
            f"Do you want to proceed with restore?"
        )

        reply = QMessageBox.warning(
            self, "Confirm Database Restore", prompt_msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success, msg = BackupService.restore_backup(file_path)
        if success:
            QMessageBox.information(self, "Restore Successful", msg)
            self.load_backup_history()
        else:
            QMessageBox.critical(self, "Restore Failed", msg)

    # ---------------- PAGE 6: AUDIT LOG VIEWER ----------------
    def setup_audit_page(self):
        layout = QVBoxLayout(self.page_audit)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # Filters Bar
        filter_box = QGroupBox("Filter Audit Records")
        f_layout = QHBoxLayout(filter_box)
        f_layout.setSpacing(10)

        f_layout.addWidget(QLabel("Module:"))
        self.cmb_audit_module = QComboBox()
        self.cmb_audit_module.addItems(["All", "Settings", "Auth", "UserManagement", "AuditLogs", "Students", "Receipts", "Security"])
        f_layout.addWidget(self.cmb_audit_module)

        f_layout.addWidget(QLabel("Search:"))
        self.txt_audit_search = QLineEdit()
        self.txt_audit_search.setPlaceholderText("Search action, details, user...")
        f_layout.addWidget(self.txt_audit_search, stretch=1)

        self.btn_filter_audit = QPushButton("🔍 Filter")
        self.btn_filter_audit.setProperty("class", "SecondaryBtn")
        self.btn_filter_audit.clicked.connect(self.load_audit_logs)
        f_layout.addWidget(self.btn_filter_audit)

        layout.addWidget(filter_box)

        # Actions Bar
        act_layout = QHBoxLayout()
        self.btn_export_audit_csv = QPushButton("📄 Export CSV")
        self.btn_export_audit_csv.setProperty("class", "SecondaryBtn")
        self.btn_export_audit_csv.clicked.connect(self.export_audit_csv)

        self.btn_export_audit_excel = QPushButton("📊 Export Excel")
        self.btn_export_audit_excel.setProperty("class", "SecondaryBtn")
        self.btn_export_audit_excel.clicked.connect(self.export_audit_excel)

        self.btn_print_audit = QPushButton("🖨 Print / PDF")
        self.btn_print_audit.setProperty("class", "SecondaryBtn")
        self.btn_print_audit.clicked.connect(self.export_audit_pdf)

        self.btn_clear_audit = QPushButton("🧹 Clear Logs (Admin)")
        self.btn_clear_audit.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; border-radius: 5px; padding: 4px 10px;")
        self.btn_clear_audit.clicked.connect(self.clear_audit_logs)

        act_layout.addWidget(self.btn_export_audit_csv)
        act_layout.addWidget(self.btn_export_audit_excel)
        act_layout.addWidget(self.btn_print_audit)
        act_layout.addStretch()
        act_layout.addWidget(self.btn_clear_audit)

        layout.addLayout(act_layout)

        # Audit Table
        self.table_audit = QTableWidget()
        self.table_audit.setColumnCount(6)
        self.table_audit.setHorizontalHeaderLabels(["Date", "Time", "Username", "Action", "Module", "Description Details"])
        self.table_audit.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_audit.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        apply_responsive_table_formatting(self.table_audit)
        layout.addWidget(self.table_audit)

    def load_audit_logs(self):
        mod = self.cmb_audit_module.currentText()
        srch = self.txt_audit_search.text().strip()

        logs = SettingsController.get_audit_logs(module=mod, search=srch)
        self.table_audit.setRowCount(len(logs))

        for idx, l in enumerate(logs):
            self.table_audit.setItem(idx, 0, QTableWidgetItem(l["date"]))
            self.table_audit.setItem(idx, 1, QTableWidgetItem(l["time"]))
            self.table_audit.setItem(idx, 2, QTableWidgetItem(l["user"]))
            self.table_audit.setItem(idx, 3, QTableWidgetItem(l["action"]))
            self.table_audit.setItem(idx, 4, QTableWidgetItem(l["module"]))
            self.table_audit.setItem(idx, 5, QTableWidgetItem(l["details"]))

    def export_audit_csv(self):
        headers = ["Date", "Time", "Username", "Action", "Module", "Description"]
        rows = []
        for r in range(self.table_audit.rowCount()):
            row = [self.table_audit.item(r, c).text() if self.table_audit.item(r, c) else "" for c in range(6)]
            rows.append(row)
        success, path = ExportService.export_to_csv(headers, rows, filename_prefix="Audit_Logs")
        if success:
            QMessageBox.information(self, "Export Successful", f"Audit logs exported to CSV:\n{path}")
        else:
            QMessageBox.critical(self, "Export Failed", path)

    def export_audit_excel(self):
        headers = ["Date", "Time", "Username", "Action", "Module", "Description"]
        rows = []
        for r in range(self.table_audit.rowCount()):
            row = [self.table_audit.item(r, c).text() if self.table_audit.item(r, c) else "" for c in range(6)]
            rows.append(row)
        success, path = ExportService.export_to_excel(headers, rows, filename_prefix="Audit_Logs")
        if success:
            QMessageBox.information(self, "Export Successful", f"Audit logs exported to Excel:\n{path}")
        else:
            QMessageBox.critical(self, "Export Failed", path)

    def export_audit_pdf(self):
        headers = ["Date", "Time", "Username", "Action", "Module", "Description"]
        rows = []
        for r in range(self.table_audit.rowCount()):
            row = [self.table_audit.item(r, c).text() if self.table_audit.item(r, c) else "" for c in range(6)]
            rows.append(row)
        success, path = ExportService.export_to_pdf_ledger("Audit Logs Trail Report", headers, rows)
        if success:
            QMessageBox.information(self, "Export Successful", f"Audit logs exported to PDF:\n{path}")
        else:
            QMessageBox.critical(self, "Export Failed", path)

    def clear_audit_logs(self):
        reply = QMessageBox.question(
            self, "Confirm Clear Audit Logs",
            "Are you sure you want to clear all audit logs? This action is permanent.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = SettingsController.clear_audit_logs()
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_audit_logs()
            else:
                QMessageBox.critical(self, "Error", msg)

    # ---------------- PAGE 7: PREFERENCES ----------------
    def setup_prefs_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        group = QGroupBox("Application Preferences & System Customization")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.cmb_win_size = QComboBox()
        self.cmb_win_size.addItems(["1280x750", "1280x800", "1600x900", "1920x1080", "Maximize"])
        form.addRow("Default Window Size:", self.cmb_win_size)

        self.cmb_sidebar_state = QComboBox()
        self.cmb_sidebar_state.addItems(["Collapsed (Compact)", "Expanded (Full)"])
        form.addRow("Default Sidebar State:", self.cmb_sidebar_state)

        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["Professional Navy", "Dark Slate", "Light Classic"])
        form.addRow("Visual Theme:", self.cmb_theme)

        self.chk_auto_backup = QCheckBox("Enable Automatic Background Backup")
        form.addRow("Auto Backup:", self.chk_auto_backup)

        self.cmb_printer = QComboBox()
        self.cmb_printer.addItems(["Default PDF Printer", "System Default Printer"])
        form.addRow("Receipt Printer:", self.cmb_printer)

        self.txt_export_folder = QLineEdit()
        form.addRow("Default Export Folder:", self.txt_export_folder)

        self.txt_backup_folder = QLineEdit()
        form.addRow("Default Backup Folder:", self.txt_backup_folder)

        self.cmb_currency = QComboBox()
        self.cmb_currency.addItems(["₹", "$", "€", "£"])
        form.addRow("Currency Symbol:", self.cmb_currency)

        self.cmb_date_format = QComboBox()
        self.cmb_date_format.addItems(["DD/MM/YYYY", "YYYY-MM-DD", "MM/DD/YYYY"])
        form.addRow("Date Format:", self.cmb_date_format)

        self.cmb_time_format = QComboBox()
        self.cmb_time_format.addItems(["12-Hour (AM/PM)", "24-Hour"])
        form.addRow("Time Format:", self.cmb_time_format)

        self.cmb_auto_logout = QComboBox()
        self.cmb_auto_logout.addItems(["15 Minutes", "30 Minutes", "60 Minutes", "Disabled"])
        form.addRow("Auto Session Timeout:", self.cmb_auto_logout)

        layout.addWidget(group)

        btn_save = QPushButton("💾   Save Preferences")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 6px;")
        btn_save.clicked.connect(self.save_preferences)
        layout.addWidget(btn_save)
        layout.addStretch()

        scroll.setWidget(container)
        p_layout = QVBoxLayout(self.page_prefs)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(scroll)

    def load_preferences(self):
        prefs = SettingsController.get_preferences()
        idx_size = self.cmb_win_size.findText(prefs.get("window_size", "1280x750"))
        if idx_size >= 0: self.cmb_win_size.setCurrentIndex(idx_size)

        self.cmb_sidebar_state.setCurrentIndex(1 if prefs.get("sidebar_expanded", False) else 0)

        idx_theme = self.cmb_theme.findText(prefs.get("theme", "Professional Navy"))
        if idx_theme >= 0: self.cmb_theme.setCurrentIndex(idx_theme)

        self.chk_auto_backup.setChecked(prefs.get("auto_backup", True))
        self.txt_export_folder.setText(prefs.get("export_folder", ""))
        self.txt_backup_folder.setText(prefs.get("backup_folder", ""))

        idx_curr = self.cmb_currency.findText(prefs.get("currency_symbol", "₹"))
        if idx_curr >= 0: self.cmb_currency.setCurrentIndex(idx_curr)

        idx_df = self.cmb_date_format.findText(prefs.get("date_format", "DD/MM/YYYY"))
        if idx_df >= 0: self.cmb_date_format.setCurrentIndex(idx_df)

        idx_tf = self.cmb_time_format.findText(prefs.get("time_format", "12-Hour (AM/PM)"))
        if idx_tf >= 0: self.cmb_time_format.setCurrentIndex(idx_tf)

    def save_preferences(self):
        prefs = {
            "window_size": self.cmb_win_size.currentText(),
            "sidebar_expanded": self.cmb_sidebar_state.currentIndex() == 1,
            "theme": self.cmb_theme.currentText(),
            "auto_backup": self.chk_auto_backup.isChecked(),
            "export_folder": self.txt_export_folder.text().strip(),
            "backup_folder": self.txt_backup_folder.text().strip(),
            "currency_symbol": self.cmb_currency.currentText(),
            "date_format": self.cmb_date_format.currentText(),
            "time_format": self.cmb_time_format.currentText(),
        }
        success, msg = SettingsController.save_preferences(prefs)
        if success:
            self.preferences_updated.emit(prefs)
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    # ---------------- PAGE 8: ABOUT SOFTWARE ----------------
    def setup_about_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(14)

        box_brand = QGroupBox("About EduLedger ERP Software")
        form_brand = QFormLayout(box_brand)
        form_brand.setSpacing(10)

        self.lbl_ab_name = QLabel(f"<b>{APP_NAME}</b>")
        form_brand.addRow("Software Product:", self.lbl_ab_name)

        self.lbl_ab_version = QLabel(f"v{APP_VERSION} (Enterprise Edition)")
        form_brand.addRow("Version:", self.lbl_ab_version)

        self.lbl_ab_build = QLabel("2026.08.20.1800")
        form_brand.addRow("Build Number:", self.lbl_ab_build)

        self.lbl_ab_python = QLabel(f"{sys.version.split()[0]}")
        form_brand.addRow("Python Version:", self.lbl_ab_python)

        self.lbl_ab_qt = QLabel(f"PySide6 {PySide6.__version__}")
        form_brand.addRow("Qt GUI Toolkit:", self.lbl_ab_qt)

        self.lbl_ab_sqlite = QLabel(f"SQLite {sqlite3.sqlite_version}")
        form_brand.addRow("Database Engine:", self.lbl_ab_sqlite)

        self.lbl_ab_dev = QLabel("EduLedger ERP Development Team / Krishna Tanwar")
        form_brand.addRow("Developer:", self.lbl_ab_dev)

        self.lbl_ab_license = QLabel("Commercial Enterprise License")
        form_brand.addRow("License Terms:", self.lbl_ab_license)

        self.lbl_ab_date = QLabel("August 2026")
        form_brand.addRow("Release Date:", self.lbl_ab_date)

        # Dynamic Git Commit Hash
        git_hash = "v3.6.0-release"
        try:
            res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                git_hash = res.stdout.strip()
        except Exception:
            pass

        self.lbl_ab_git = QLabel(git_hash)
        form_brand.addRow("Git Commit Hash:", self.lbl_ab_git)

        layout.addWidget(box_brand)
        layout.addStretch()

        scroll.setWidget(container)
        p_layout = QVBoxLayout(self.page_about)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(scroll)

    def load_about_info(self):
        pass
