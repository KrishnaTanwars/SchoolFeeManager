"""
Add / Edit Fee Category Dialog.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QCheckBox, QComboBox, QTextEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout,
    QScrollArea, QWidget, QFrame
)
from controllers.fee_controller import FeeController

class FeeCategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Edit Fee Head" if category else "Add New Fee Head")
        self.setMinimumSize(420, 360)
        self.resize(480, 380)

        self.setup_ui()
        if self.category:
            self.load_data()

    def setup_ui(self):
        dialog_vbox = QVBoxLayout(self)
        dialog_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)

        group = QGroupBox("Fee Head Details")
        form = QFormLayout(group)
        form.setSpacing(12)

        # Description / Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. UG Tuition Fee, Admission Form Fee")
        form.addRow("Description / Name *:", self.txt_name)

        # Course Dropdown (UG / PG)
        self.cmb_course = QComboBox()
        self.cmb_course.addItems(["UG", "PG"])
        form.addRow("Course Level *:", self.cmb_course)

        # Default Amount
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0.0, 1000000.0)
        self.spn_amount.setDecimals(2)
        self.spn_amount.setSingleStep(100.0)
        self.spn_amount.setPrefix("₹ ")
        form.addRow("Default Amount:", self.spn_amount)

        # Status Checkbox
        self.chk_active = QCheckBox("Active for Fee Collection")
        self.chk_active.setChecked(True)
        form.addRow("Status:", self.chk_active)

        # Description / Remarks
        self.txt_desc = QTextEdit()
        self.txt_desc.setMaximumHeight(60)
        self.txt_desc.setPlaceholderText("Optional notes or fee breakdown details")
        form.addRow("Remarks:", self.txt_desc)

        layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Fee Head")
        self.btn_save.clicked.connect(self.save_category)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def load_data(self):
        c = self.category
        self.txt_name.setText(c.name)
        self.cmb_course.setCurrentText(c.course if getattr(c, "course", None) in ("UG", "PG") else "UG")
        self.spn_amount.setValue(c.default_amount)
        self.chk_active.setChecked(c.is_active)
        self.txt_desc.setPlainText(c.description or "")

    def save_category(self):
        name = self.txt_name.text().strip()
        course = self.cmb_course.currentText().strip()
        amount = self.spn_amount.value()
        is_active = self.chk_active.isChecked()
        desc = self.txt_desc.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Description / Fee Head Name is required.")
            self.txt_name.setFocus()
            return

        data = {
            "name": name,
            "course": course,
            "default_amount": amount,
            "is_active": is_active,
            "description": desc
        }

        if self.category:
            success, msg = FeeController.update_category(self.category.id, data)
        else:
            success, msg = FeeController.create_category(data)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
