"""
Add / Edit Course & Degree Program Dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QSpinBox, QWidget
)
from PySide6.QtCore import Qt
from controllers.academic_controller import AcademicController

class CourseDialog(QDialog):
    def __init__(self, parent=None, course_data=None):
        super().__init__(parent)
        self.course_data = course_data  # If present, edit mode
        self.is_edit = course_data is not None

        if self.is_edit:
            self.setWindowTitle(f"Edit Course: {course_data.name}")
        else:
            self.setWindowTitle("Add New Academic Course / Degree Program")

        self.setMinimumSize(420, 320)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        group = QGroupBox("Course Details")
        form = QFormLayout(group)
        form.setSpacing(10)

        # Course Code
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("e.g. BPHARM, BTECH, MBA, DPHARM")
        if self.is_edit:
            self.txt_code.setText(self.course_data.code)
        form.addRow("Course Code *:", self.txt_code)

        # Course Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. B. Pharmacy, B.Tech CSE, MBA")
        if self.is_edit:
            self.txt_name.setText(self.course_data.name)
        form.addRow("Course Name *:", self.txt_name)

        # Course Type / Category
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["UG", "PG", "Diploma", "College", "School", "Institute"])
        if self.is_edit and self.course_data.course_type:
            idx = self.cmb_type.findText(self.course_data.course_type)
            if idx >= 0:
                self.cmb_type.setCurrentIndex(idx)
        form.addRow("Course Category / Type:", self.cmb_type)

        # Duration in Years
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(1, 6)
        self.spin_duration.setValue(3)
        if self.is_edit:
            self.spin_duration.setValue(self.course_data.duration_years or 3)
        form.addRow("Duration (Years):", self.spin_duration)

        # Total Semesters
        self.spin_semesters = QSpinBox()
        self.spin_semesters.setRange(0, 12)
        self.spin_semesters.setValue(6)
        if self.is_edit:
            self.spin_semesters.setValue(self.course_data.total_semesters or 6)
        form.addRow("Total Semesters:", self.spin_semesters)

        main_layout.addWidget(group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Course")
        self.btn_save.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.btn_save.clicked.connect(self.save_course)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def save_course(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        c_type = self.cmb_type.currentText()
        duration = self.spin_duration.value()
        semesters = self.spin_semesters.value()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Course Code is required.")
            self.txt_code.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Error", "Course Name is required.")
            self.txt_name.setFocus()
            return

        if self.is_edit:
            success, msg = AcademicController.update_course(
                self.course_data.id, code, name, c_type, duration, semesters
            )
        else:
            success, msg = AcademicController.add_course(
                code, name, c_type, duration, semesters
            )

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
