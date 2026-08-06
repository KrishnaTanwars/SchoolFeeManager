"""
Universal Administrator Authorization Modal Dialog for EduLedger ERP.
Used across all modules to protect critical delete and settings operations.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from services.security_service import SecurityService

class AdminAuthDialog(QDialog):
    def __init__(self, parent=None, action_title: str = "Administrator Authorization Required", action_context: str = "", module: str = "General"):
        super().__init__(parent)
        self.action_title = action_title
        self.action_context = action_context
        self.module = module
        
        self.setWindowTitle("Administrator Authorization Required")
        self.setModal(True)
        self.setFixedSize(450, 290)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Title Frame
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #1e3a8a; border-radius: 6px; padding: 10px;")
        v_hdr = QVBoxLayout(hdr_frame)
        v_hdr.setContentsMargins(10, 8, 10, 8)
        v_hdr.setSpacing(4)

        lbl_hdr_title = QLabel(self.action_title)
        lbl_hdr_title.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 800;")
        
        lbl_hdr_sub = QLabel("ADMINISTRATOR PASSWORD REQUIRED")
        lbl_hdr_sub.setStyleSheet("color: #93c5fd; font-size: 11px; font-weight: 700; letter-spacing: 1px;")

        v_hdr.addWidget(lbl_hdr_title)
        v_hdr.addWidget(lbl_hdr_sub)
        layout.addWidget(hdr_frame)

        # Context description if provided
        if self.action_context:
            lbl_desc = QLabel(f"Operation: <b>{self.action_context}</b>")
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #334155; font-size: 12px; margin-bottom: 2px;")
            layout.addWidget(lbl_desc)

        # Error Banner (Hidden by default)
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: bold; background-color: #fef2f2; border: 1px solid #fca5a5; border-radius: 4px; padding: 6px;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)

        # Password Input Field
        lbl_pwd_label = QLabel("Administrator Password:")
        lbl_pwd_label.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 13px;")
        layout.addWidget(lbl_pwd_label)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Enter administrator password to authorize...")
        self.txt_password.setFixedHeight(36)
        self.txt_password.setStyleSheet("font-size: 13px; padding: 0 10px;")
        self.txt_password.returnPressed.connect(self.authorize)
        layout.addWidget(self.txt_password)

        # Show / Hide Password Toggle Checkbox
        self.chk_show_pwd = QCheckBox("Show Password")
        self.chk_show_pwd.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")
        self.chk_show_pwd.toggled.connect(self._toggle_password_visibility)
        layout.addWidget(self.chk_show_pwd)

        layout.addStretch()

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedHeight(36)
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_authorize = QPushButton("🔒  Authorize Action")
        self.btn_authorize.setFixedHeight(36)
        self.btn_authorize.setCursor(Qt.PointingHandCursor)
        self.btn_authorize.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: bold; border-radius: 5px; font-size: 13px; padding: 0 16px;")
        self.btn_authorize.clicked.connect(self.authorize)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_authorize)

        layout.addLayout(btn_layout)

        # Set initial focus
        self.txt_password.setFocus()

    def _toggle_password_visibility(self, checked: bool):
        if checked:
            self.txt_password.setEchoMode(QLineEdit.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)

    def authorize(self):
        password = self.txt_password.text().strip()
        if not password:
            self.lbl_error.setText("❌ Please enter administrator password.")
            self.lbl_error.show()
            self.txt_password.setFocus()
            return

        self.btn_authorize.setEnabled(False)
        try:
            if SecurityService.verify_admin_password(password, module=self.module):
                self.lbl_error.hide()
                self.accept()
            else:
                self.lbl_error.setText("❌ Incorrect administrator password. Access denied.")
                self.lbl_error.show()
                self.txt_password.clear()
                self.txt_password.setFocus()
        finally:
            self.btn_authorize.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
