"""
Settings, School Profile, User Management, and Backup & Restore View.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QGroupBox, QFormLayout, QMessageBox, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt
from controllers.settings_controller import SettingsController
from controllers.auth_controller import AuthController
from services.backup_service import BackupService
from dialogs.user_dialog import UserDialog
from utils.workers import GenericWorker
from utils.logger import logger

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path_selected = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header
        title_lbl = QLabel("System Settings & Administration")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(title_lbl)

        # Tab Container
        self.tabs = QTabWidget()

        # Tab 1: School Profile & Receipt Settings
        self.tab_profile = QWidget()
        self.setup_profile_tab()
        self.tabs.addTab(self.tab_profile, "School Profile & Receipt Settings")

        # Tab 2: Academic Sessions
        self.tab_sessions = QWidget()
        self.setup_sessions_tab()
        self.tabs.addTab(self.tab_sessions, "Academic Sessions")

        # Tab 3: User Management
        self.tab_users = QWidget()
        self.setup_users_tab()
        self.tabs.addTab(self.tab_users, "User Management")

        # Tab 4: Database Backup & Restore
        self.tab_backup = QWidget()
        self.setup_backup_tab()
        self.tabs.addTab(self.tab_backup, "Backup & Restore")

        layout.addWidget(self.tabs)
        self.load_school_info()

    # ---------------- TAB 1: PROFILE ----------------
    def setup_profile_tab(self):
        layout = QVBoxLayout(self.tab_profile)

        group = QGroupBox("School Information & Receipt Branding")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.txt_school_name = QLineEdit()
        form.addRow("School / Institute Name *:", self.txt_school_name)

        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(60)
        form.addRow("Address *:", self.txt_address)

        self.txt_phone = QLineEdit()
        form.addRow("Contact Phone(s) *:", self.txt_phone)

        self.txt_email = QLineEdit()
        form.addRow("Email Address:", self.txt_email)

        self.txt_website = QLineEdit()
        form.addRow("Website URL:", self.txt_website)

        # Logo Selector
        logo_layout = QHBoxLayout()
        self.lbl_logo_path = QLabel("No Logo Selected")
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
        btn_save = QPushButton("Save Settings & School Profile")
        btn_save.setFixedHeight(40)
        btn_save.clicked.connect(self.save_school_info)
        layout.addWidget(btn_save)
        layout.addStretch()

    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select School Logo Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.logo_path_selected = path
            self.lbl_logo_path.setText(Path(path).name)

    def load_school_info(self):
        info = SettingsController.get_school_info()
        if info:
            self.txt_school_name.setText(info.school_name)
            self.txt_address.setPlainText(info.address)
            self.txt_phone.setText(info.phone)
            self.txt_email.setText(info.email)
            self.txt_website.setText(info.website or "")
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
            "phone": phone,
            "email": self.txt_email.text().strip(),
            "website": self.txt_website.text().strip(),
            "logo_path": self.logo_path_selected,
            "receipt_prefix": self.txt_receipt_prefix.text().strip(),
            "receipt_footer": self.txt_receipt_footer.toPlainText().strip()
        }

        success, msg = SettingsController.update_school_info(data)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    # ---------------- TAB 2: SESSIONS ----------------
    def setup_sessions_tab(self):
        layout = QVBoxLayout(self.tab_sessions)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Manage Academic Sessions"))
        hdr.addStretch()

        self.btn_add_session = QPushButton("+ Add New Session")
        self.btn_add_session.clicked.connect(self.add_session)
        hdr.addWidget(self.btn_add_session)

        layout.addLayout(hdr)

        self.table_sessions = QTableWidget()
        self.table_sessions.setColumnCount(3)
        self.table_sessions.setHorizontalHeaderLabels(["Session Name", "Is Active Current Session", "Action"])
        self.table_sessions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_sessions)

        self.load_sessions()

    def load_sessions(self):
        sessions = SettingsController.get_academic_sessions()
        self.table_sessions.setRowCount(len(sessions))

        for idx, s in enumerate(sessions):
            self.table_sessions.setItem(idx, 0, QTableWidgetItem(s.session_name))
            self.table_sessions.setItem(idx, 1, QTableWidgetItem("Yes (Current)" if s.is_current else "No"))

            if not s.is_current:
                btn_set = QPushButton("Make Current Session")
                btn_set.setProperty("class", "SecondaryBtn")
                btn_set.clicked.connect(lambda _, sname=s.session_name: self.set_current_session(sname))
                self.table_sessions.setCellWidget(idx, 2, btn_set)
            else:
                lbl_active = QLabel("Active")
                lbl_active.setStyleSheet("font-weight: bold; color: #10b981; padding-left: 10px;")
                self.table_sessions.setCellWidget(idx, 2, lbl_active)

    def add_session(self):
        name, ok = QFileDialog.getSaveFileName(self, "New Academic Session", "", "Session")
        # Custom prompt via QMessageBox input
        from PySide6.QtWidgets import QInputDialog
        session_name, ok = QInputDialog.getText(self, "New Academic Session", "Enter Session Name (e.g. 2025-2026):")
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

    # ---------------- TAB 3: USERS ----------------
    def setup_users_tab(self):
        layout = QVBoxLayout(self.tab_users)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("System User Accounts"))
        hdr.addStretch()

        self.btn_add_user = QPushButton("+ Add System User")
        self.btn_add_user.clicked.connect(self.add_user)
        hdr.addWidget(self.btn_add_user)

        layout.addLayout(hdr)

        self.table_users = QTableWidget()
        self.table_users.setColumnCount(4)
        self.table_users.setHorizontalHeaderLabels(["Username", "Full Name", "Role", "Status"])
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_users)

        self.load_users()

    def load_users(self):
        users = AuthController.get_all_users()
        self.table_users.setRowCount(len(users))

        for idx, u in enumerate(users):
            self.table_users.setItem(idx, 0, QTableWidgetItem(u.username))
            self.table_users.setItem(idx, 1, QTableWidgetItem(u.full_name))
            self.table_users.setItem(idx, 2, QTableWidgetItem(u.role))
            self.table_users.setItem(idx, 3, QTableWidgetItem(u.status))

    def add_user(self):
        dlg = UserDialog(self)
        if dlg.exec():
            self.load_users()

    # ---------------- TAB 4: BACKUP & RESTORE ----------------
    def setup_backup_tab(self):
        layout = QVBoxLayout(self.tab_backup)

        # Action Buttons
        box = QGroupBox("Database Backup & Disaster Recovery Actions")
        box_layout = QHBoxLayout(box)

        self.btn_backup_now = QPushButton("Create Immediate Backup ZIP")
        self.btn_backup_now.setFixedHeight(40)
        self.btn_backup_now.clicked.connect(self.run_backup)

        self.btn_restore_now = QPushButton("Restore Database from ZIP")
        self.btn_restore_now.setFixedHeight(40)
        self.btn_restore_now.setProperty("class", "DangerBtn")
        self.btn_restore_now.clicked.connect(self.run_restore)

        box_layout.addWidget(self.btn_backup_now)
        box_layout.addWidget(self.btn_restore_now)

        layout.addWidget(box)

        # Backup Instructions
        info = QLabel(
            "<b>Note on Backup & Restore:</b><br/>"
            "• Manual backups create a timestamped <code>.zip</code> file containing <code>school_fee.db</code>.<br/>"
            "• Before performing any database restore, the system automatically creates a safety backup of your current database.<br/>"
            "• Restoring overwrites existing data with the selected backup snapshot."
        )
        info.setStyleSheet("background-color: #eff6ff; border: 1px solid #93c5fd; border-radius: 6px; padding: 10px; color: #1e3a8a;")
        layout.addWidget(info)
        layout.addStretch()

    def run_backup(self):
        success, msg, path = BackupService.create_backup()
        if success:
            QMessageBox.information(self, "Backup Successful", f"{msg}\nSaved at: {path}")
        else:
            QMessageBox.critical(self, "Backup Failed", msg)

    def run_restore(self):
        reply = QMessageBox.warning(
            self, "Confirm Database Restore",
            "CRITICAL WARNING:\nRestoring a database will replace your current database records with the selected backup snapshot.\n"
            "A safety backup of your current database will be created automatically before restoring.\n\n"
            "Do you want to proceed with restore?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup Zip File", "", "Zip Files (*.zip)")
        if not file_path:
            return

        success, msg = BackupService.restore_backup(file_path)
        if success:
            QMessageBox.information(self, "Restore Successful", msg)
        else:
            QMessageBox.critical(self, "Restore Failed", msg)
