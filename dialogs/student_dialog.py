"""
Add / Edit Student Dialog with Strict Validation & Enhanced Date Picker.
"""

from typing import Optional, Dict, Any
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QDate
from controllers.student_controller import StudentController
from controllers.settings_controller import SettingsController
from utils.helpers import validate_indian_mobile, parse_date, format_date

class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle("Edit Student Details" if student else "Register New Student")
        self.resize(550, 520)

        self.setup_ui()
        if self.student:
            self.load_student_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        group = QGroupBox("Student Information Details")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(10)

        # Admission Number
        self.txt_admission_no = QLineEdit()
        self.txt_admission_no.setPlaceholderText("e.g. ADM/2024/001")
        form_layout.addRow("Admission Number *:", self.txt_admission_no)

        # Roll Number
        self.txt_roll_no = QLineEdit()
        self.txt_roll_no.setPlaceholderText("e.g. 101")
        form_layout.addRow("Roll Number:", self.txt_roll_no)

        # Student Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Full Name of Student")
        form_layout.addRow("Student Name *:", self.txt_name)

        # Father Name
        self.txt_father_name = QLineEdit()
        self.txt_father_name.setPlaceholderText("Father's Name")
        form_layout.addRow("Father's Name *:", self.txt_father_name)

        # Mother Name
        self.txt_mother_name = QLineEdit()
        self.txt_mother_name.setPlaceholderText("Mother's Name")
        form_layout.addRow("Mother's Name:", self.txt_mother_name)

        # Class & Section Layout
        class_sec_layout = QHBoxLayout()
        self.cmb_class = QComboBox()
        self.cmb_class.setEditable(True)
        self.cmb_class.addItems(["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12", "Nursery", "LKG", "UKG"])
        self.txt_section = QLineEdit()
        self.txt_section.setPlaceholderText("Section (A/B/C)")
        class_sec_layout.addWidget(self.cmb_class, stretch=2)
        class_sec_layout.addWidget(self.txt_section, stretch=1)
        form_layout.addRow("Class & Section *:", class_sec_layout)

        # Mobile Number
        self.txt_mobile = QLineEdit()
        self.txt_mobile.setPlaceholderText("10-Digit Mobile Number (e.g. 9876543210)")
        form_layout.addRow("Mobile Number *:", self.txt_mobile)

        # Date of Admission
        self.dt_admission = QDateEdit()
        self.dt_admission.setFixedHeight(34)
        self.dt_admission.setCalendarPopup(True)
        self.dt_admission.setDisplayFormat("dd-MM-yyyy")
        self.dt_admission.setDate(QDate.currentDate())
        form_layout.addRow("Date of Admission:", self.dt_admission)

        # Academic Session
        self.cmb_session = QComboBox()
        sessions = SettingsController.get_academic_sessions()
        if sessions:
            for s in sessions:
                self.cmb_session.addItem(s.session_name)
        else:
            self.cmb_session.addItems(["2024-2025", "2025-2026"])
        form_layout.addRow("Academic Session *:", self.cmb_session)

        # Status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.cmb_status)

        # Address
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(60)
        form_layout.addRow("Residential Address:", self.txt_address)

        main_layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Student")
        self.btn_save.clicked.connect(self.save_student)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def load_student_data(self):
        s = self.student
        self.txt_admission_no.setText(s.admission_no)
        self.txt_roll_no.setText(s.roll_no or "")
        self.txt_name.setText(s.name)
        self.txt_father_name.setText(s.father_name)
        self.txt_mother_name.setText(s.mother_name or "")
        self.cmb_class.setCurrentText(s.class_name)
        self.txt_section.setText(s.section or "")
        self.txt_mobile.setText(s.mobile)
        if s.admission_date:
            self.dt_admission.setDate(QDate(s.admission_date.year, s.admission_date.month, s.admission_date.day))
        self.cmb_session.setCurrentText(s.academic_session)
        self.cmb_status.setCurrentText(s.status)
        self.txt_address.setPlainText(s.address or "")

    def save_student(self):
        adm_no = self.txt_admission_no.text().strip()
        name = self.txt_name.text().strip()
        father_name = self.txt_father_name.text().strip()
        class_name = self.cmb_class.currentText().strip()
        mobile = self.txt_mobile.text().strip()

        if not adm_no:
            QMessageBox.warning(self, "Validation Error", "Admission Number is required.")
            self.txt_admission_no.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Error", "Student Name is required.")
            self.txt_name.setFocus()
            return
        if not father_name:
            QMessageBox.warning(self, "Validation Error", "Father's Name is required.")
            self.txt_father_name.setFocus()
            return
        if not class_name:
            QMessageBox.warning(self, "Validation Error", "Class is required.")
            return
        if not validate_indian_mobile(mobile):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 10-digit Indian Mobile Number.")
            self.txt_mobile.setFocus()
            return

        qdate = self.dt_admission.date()
        admission_date = date(qdate.year(), qdate.month(), qdate.day())

        data = {
            "admission_no": adm_no,
            "roll_no": self.txt_roll_no.text().strip(),
            "name": name,
            "father_name": father_name,
            "mother_name": self.txt_mother_name.text().strip(),
            "class_name": class_name,
            "section": self.txt_section.text().strip(),
            "mobile": mobile,
            "address": self.txt_address.toPlainText().strip(),
            "admission_date": admission_date,
            "academic_session": self.cmb_session.currentText(),
            "status": self.cmb_status.currentText()
        }

        if self.student:
            success, msg = StudentController.update_student(self.student.id, data)
        else:
            success, msg = StudentController.create_student(data)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
