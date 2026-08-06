"""
Login View Widget for Admin / Operator Authentication with Responsive Card Dimensions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from controllers.auth_controller import AuthController
from config.app_config import APP_VERSION

class LoginView(QWidget):
    login_success = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Center Card Frame with ample height to prevent bottom text clipping
        card = QFrame()
        card.setFixedSize(430, 480)
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 30, 35, 30)
        card_layout.setSpacing(12)

from config.app_config import APP_VERSION

        # App Logo / Icon Header
        title = QLabel("School Fee Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e3a8a; border: none;")

        subtitle = QLabel(f"Enterprise ERP System v{APP_VERSION}")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b; border: none;")

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(6)

        # Username Input
        lbl_user = QLabel("Username:")
        lbl_user.setStyleSheet("font-weight: 700; color: #334155; border: none;")
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(38)
        self.txt_username.setPlaceholderText("Enter username (default: admin)")
        self.txt_username.setText("admin")

        # Password Input
        lbl_pass = QLabel("Password:")
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
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("font-size: 11px; color: #64748b; border: none; padding-top: 8px; line-height: 1.4;")
        card_layout.addWidget(hint)

        main_layout.addWidget(card)

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
