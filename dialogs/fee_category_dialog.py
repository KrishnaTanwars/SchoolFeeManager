"""
Add / Edit Fee Category Dialog.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QCheckBox, QTextEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from controllers.fee_controller import FeeController

class FeeCategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Edit Fee Category" if category else "Add New Fee Category / Head")
        self.resize(450, 350)

        self.setup_ui()
        if self.category:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("Fee Category Configuration")
        form = QFormLayout(group)
        form.setSpacing(10)

        # Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Tuition Fee, Hostel Fee")
        form.addRow("Category Name *:", self.txt_name)

        # Code
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g. TF, HF")
        form.addRow("Short Code:", self.txt_code)

        # Default Amount
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0.0, 1000000.0)
        self.spn_amount.setDecimals(2)
        self.spn_amount.setSingleStep(100.0)
        self.spn_amount.setPrefix("₹ ")
        form.addRow("Default Amount:", self.spn_amount)

        # Active Checkbox
        self.chk_active = QCheckBox("Active for Fee Collection")
        self.chk_active.setChecked(True)
        form.addRow("Status:", self.chk_active)

        # Description
        self.txt_desc = QTextEdit()
        self.txt_desc.setMaximumHeight(60)
        form.addRow("Description:", self.txt_desc)

        layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Category")
        self.btn_save.clicked.connect(self.save_category)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_data(self):
        c = self.category
        self.txt_name.setText(c.name)
        self.txt_code.setText(c.code or "")
        self.spn_amount.setValue(c.default_amount)
        self.chk_active.setChecked(c.is_active)
        self.txt_desc.setPlainText(c.description or "")

    def save_category(self):
        name = self.txt_name.text().strip()
        code = self.txt_code.text().strip()
        amount = self.spn_amount.value()
        is_active = self.chk_active.isChecked()
        desc = self.txt_desc.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Category Name is required.")
            self.txt_name.setFocus()
            return

        if self.category:
            success, msg = FeeController.update_category(self.category.id, name, code, amount, is_active, desc)
        else:
            success, msg = FeeController.create_category(name, code, amount, desc)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
