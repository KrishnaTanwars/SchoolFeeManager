"""
Login View Widget for Admin / Operator Authentication with Responsive Card Dimensions.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from controllers.auth_controller import AuthController
from controllers.settings_controller import SettingsController
from config.app_config import APP_VERSION, ASSETS_DIR

class LoginView(QWidget):
    login_success = Signal()

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
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignCenter)

        # Center Card Frame with flexible dimensions to prevent clipping
        card = QFrame()
        card.setMinimumSize(360, 460)
        card.setMaximumWidth(450)
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 25, 35, 25)
        card_layout.setSpacing(10)

        # App Logo Image & Header
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("border: none;")

        logo_path = SettingsController.get_active_logo_path()
        if not logo_path or not Path(logo_path).exists():
            logo_path = str(ASSETS_DIR / "edu_ledger_logo.png")

        if Path(logo_path).exists():
            pix = QPixmap(logo_path)
            if not pix.isNull():
                lbl_logo.setPixmap(pix.scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                card_layout.addWidget(lbl_logo)

        title = QLabel("College Management System")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a; border: none;")

        subtitle = QLabel(f"Enterprise ERP System v{APP_VERSION}")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b; border: none;")

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(6)

        # Username Input
        lbl_user = QLabel("Username:")
        lbl_user.setWordWrap(True)
        lbl_user.setStyleSheet("font-weight: 700; color: #334155; border: none;")
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(38)
        self.txt_username.setPlaceholderText("Enter username (default: admin)")
        self.txt_username.setText("admin")

        # Password Input
        lbl_pass = QLabel("Password:")
        lbl_pass.setWordWrap(True)
        lbl_pass.setStyleSheet("font-weight: 700; color: #334155; border: none;")
        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(38)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Enter password (default: admin123)")
        self.txt_password.setText("admin123")
        self.txt_password.returnPressed.connect(self.handle_login)

        card_layout.addWidget(lbl_user)
        card_layout.addWidget(self.txt_username)
        card_layout.addWidget(lbl_pass)
        card_layout.addWidget(self.txt_password)
        card_layout.addSpacing(10)

        # Login Button
        self.btn_login = QPushButton("LOG IN TO ERP")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.handle_login)

        card_layout.addWidget(self.btn_login)

        # Credentials Hint
        hint = QLabel("Default Credentials:<br/>Admin: <b>admin / admin123</b><br/>Operator: <b>operator / operator123</b>")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("font-size: 11px; color: #64748b; border: none; padding-top: 8px; line-height: 1.4;")
        card_layout.addWidget(hint)

        main_layout.addWidget(card)

        scroll.setWidget(container)
        main_vbox.addWidget(scroll)

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return

        if AuthController.login(username, password):
            self.login_success.emit()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
            self.txt_password.clear()
            self.txt_password.setFocus()
