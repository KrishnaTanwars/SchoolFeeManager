"""
Add System User Account Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from controllers.auth_controller import AuthController

class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New System User Account")
        self.resize(400, 250)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("User Credentials & Role")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username (e.g. operator2)")
        form.addRow("Username *:", self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Password")
        form.addRow("Password *:", self.txt_password)

        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("Full Name of Staff Member")
        form.addRow("Full Name *:", self.txt_fullname)

        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["Operator", "Admin"])
        form.addRow("Role:", self.cmb_role)

        layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Create User")
        self.btn_save.clicked.connect(self.save_user)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def save_user(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        fullname = self.txt_fullname.text().strip()
        role = self.cmb_role.currentText()

        if not username or not password or not fullname:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        success = AuthController.create_user(username, password, fullname, role)
        if success:
            QMessageBox.information(self, "Success", f"User '{username}' created successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"Username '{username}' already exists.")
