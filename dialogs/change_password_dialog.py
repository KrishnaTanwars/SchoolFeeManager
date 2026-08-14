"""
Change Password and Admin Password Reset Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from controllers.auth_controller import AuthController

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None, user_id=None, username=None, is_admin_reset=False):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.is_admin_reset = is_admin_reset

        if is_admin_reset:
            self.setWindowTitle(f"Reset Password: {username}")
        else:
            self.setWindowTitle("Change My Password")

        self.setMinimumSize(360, 240)
        self.resize(400, 260 if is_admin_reset else 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = f"Reset Password for '{self.username}'" if self.is_admin_reset else "Change Security Password"
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setSpacing(10)

        if not self.is_admin_reset:
            self.txt_old_pwd = QLineEdit()
            self.txt_old_pwd.setEchoMode(QLineEdit.Password)
            self.txt_old_pwd.setPlaceholderText("Enter current password")
            form.addRow("Current Password *:", self.txt_old_pwd)

        self.txt_new_pwd = QLineEdit()
        self.txt_new_pwd.setEchoMode(QLineEdit.Password)
        self.txt_new_pwd.setPlaceholderText("Enter new password")
        form.addRow("New Password *:", self.txt_new_pwd)

        self.txt_confirm_pwd = QLineEdit()
        self.txt_confirm_pwd.setEchoMode(QLineEdit.Password)
        self.txt_confirm_pwd.setPlaceholderText("Confirm new password")
        form.addRow("Confirm Password *:", self.txt_confirm_pwd)

        layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Reset Password" if self.is_admin_reset else "Update Password")
        self.btn_save.clicked.connect(self.save_password)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def save_password(self):
        new_pwd = self.txt_new_pwd.text().strip()
        confirm_pwd = self.txt_confirm_pwd.text().strip()

        if not new_pwd or not confirm_pwd:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Validation Error", "New password and confirmation do not match.")
            return

        if len(new_pwd) < 4:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 4 characters long.")
            return

        if self.is_admin_reset:
            success, msg = AuthController.reset_password(self.user_id, new_pwd)
        else:
            old_pwd = self.txt_old_pwd.text().strip()
            if not old_pwd:
                QMessageBox.warning(self, "Validation Error", "Current password is required.")
                return
            success, msg = AuthController.change_password(self.user_id, old_pwd, new_pwd)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
