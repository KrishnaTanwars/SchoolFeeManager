"""
Add / Edit Specialization Branch Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QWidget
)
from PySide6.QtCore import Qt
from controllers.academic_controller import AcademicController

class BranchDialog(QDialog):
    def __init__(self, parent=None, branch_data=None):
        super().__init__(parent)
        self.branch_data = branch_data  # If present, edit mode
        self.is_edit = branch_data is not None

        if self.is_edit:
            self.setWindowTitle(f"Edit Branch: {branch_data.name}")
        else:
            self.setWindowTitle("Add New Specialization Branch")

        self.setMinimumSize(420, 260)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        group = QGroupBox("Branch Details")
        form = QFormLayout(group)
        form.setSpacing(10)

        # Branch Code
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g. PHARM, CSE, CEUTICS, GEN")
        if self.is_edit:
            self.txt_code.setText(self.branch_data.code)
        form.addRow("Branch Code *:", self.txt_code)

        # Branch Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Pharmacy, Computer Science, Pharmaceutics")
        if self.is_edit:
            self.txt_name.setText(self.branch_data.name)
        form.addRow("Branch Name *:", self.txt_name)

        # Linked Course
        self.cmb_course = QComboBox()
        courses_full = AcademicController.get_all_courses_full()
        self.cmb_course.addItem("All Courses (General)", "All")
        for c in courses_full:
            self.cmb_course.addItem(f"{c.name} ({c.code})", c.code)

        if self.is_edit and self.branch_data.course_code:
            idx = self.cmb_course.findData(self.branch_data.course_code)
            if idx >= 0:
                self.cmb_course.setCurrentIndex(idx)
        form.addRow("Linked Course:", self.cmb_course)

        main_layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Branch")
        self.btn_save.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_branch)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def save_branch(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        course_code = self.cmb_course.currentData()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Branch Code is required.")
            self.txt_code.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Error", "Branch Name is required.")
            self.txt_name.setFocus()
            return

        if self.is_edit:
            success, msg = AcademicController.update_branch(
                self.branch_data.id, code, name, course_code
            )
        else:
            success, msg = AcademicController.add_branch(
                code, name, course_code
            )

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
