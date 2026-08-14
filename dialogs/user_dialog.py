"""
Add / Edit System User Account Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt
from controllers.auth_controller import AuthController

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data  # If present, edit mode
        self.is_edit = user_data is not None

        if self.is_edit:
            self.setWindowTitle(f"Edit System User: {user_data.username}")
        else:
            self.setWindowTitle("Add New System User Account")

        self.setMinimumSize(400, 320)
        self.setup_ui()

    def setup_ui(self):
        dialog_vbox = QVBoxLayout(self)
        dialog_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        group = QGroupBox("User Account Details")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username (e.g. operator2)")
        if self.is_edit:
            self.txt_username.setText(self.user_data.username)
            self.txt_username.setEnabled(False)  # Username cannot be changed
        form.addRow("Username *:", self.txt_username)

        if not self.is_edit:
            self.txt_password = QLineEdit()
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.txt_password.setPlaceholderText("Password")
            form.addRow("Password *:", self.txt_password)

        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("Full Name of Staff Member")
        if self.is_edit:
            self.txt_fullname.setText(self.user_data.full_name)
        form.addRow("Full Name *:", self.txt_fullname)

        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["Operator", "Administrator", "Viewer"])
        if self.is_edit:
            current_role = "Administrator" if self.user_data.role in ("Admin", "Administrator") else self.user_data.role
            idx = self.cmb_role.findText(current_role)
            if idx >= 0:
                self.cmb_role.setCurrentIndex(idx)
        form.addRow("Role *:", self.cmb_role)

        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Active", "Disabled"])
        if self.is_edit:
            idx = self.cmb_status.findText(self.user_data.status)
            if idx >= 0:
                self.cmb_status.setCurrentIndex(idx)
        form.addRow("Account Status *:", self.cmb_status)

        layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save User" if self.is_edit else "Create User")
        self.btn_save.clicked.connect(self.save_user)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def save_user(self):
        username = self.txt_username.text().strip()
        fullname = self.txt_fullname.text().strip()
        role = self.cmb_role.currentText()
        status = self.cmb_status.currentText()

        if not fullname or (not self.is_edit and not self.txt_password.text().strip()):
            QMessageBox.warning(self, "Validation Error", "All required fields must be filled.")
            return

        if self.is_edit:
            success, msg = AuthController.update_user(
                user_id=self.user_data.id,
                full_name=fullname,
                role=role,
                status=status
            )
            if success:
                QMessageBox.information(self, "Success", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", msg)
        else:
            password = self.txt_password.text().strip()
            success = AuthController.create_user(username, password, fullname, role)
            if success:
                QMessageBox.information(self, "Success", f"User '{username}' created successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to create user. Username '{username}' may already exist.")
