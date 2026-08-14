"""
Add / Edit Student Dialog with Strict Validation, Enhanced Date Picker, Date of Birth, & Aadhaar Number support.
"""

from typing import Optional, Dict, Any
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout,
    QScrollArea, QFrame, QWidget
)
from PySide6.QtCore import Qt, QDate
from controllers.student_controller import StudentController
from controllers.settings_controller import SettingsController
from controllers.academic_controller import AcademicController
from utils.helpers import validate_indian_mobile, parse_date, format_date

class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle("Edit Student Details" if student else "Register New Student")
        self.setMinimumSize(520, 520)
        self.resize(620, 680)

        self.setup_ui()
        if self.student:
            self.load_student_data()

    def setup_ui(self):
        dialog_vbox = QVBoxLayout(self)
        dialog_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(15, 15, 15, 15)

        group = QGroupBox("Student Information & Academic Structure")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(10)

        # Admission Number
        self.txt_admission_no = QLineEdit()
        self.txt_admission_no.setPlaceholderText("e.g. ADM/2025/001")
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

        # Date of Birth (Placed immediately BELOW Mother's Name and ABOVE Course & Branch)
        self.dt_dob = QDateEdit()
        self.dt_dob.setFixedHeight(34)
        self.dt_dob.setCalendarPopup(True)
        self.dt_dob.setDisplayFormat("dd-MM-yyyy")
        self.dt_dob.setMinimumDate(QDate(1900, 1, 1))
        self.dt_dob.setMaximumDate(QDate.currentDate())
        self.dt_dob.setSpecialValueText("Select Date of Birth")
        self.dt_dob.setDate(QDate(1900, 1, 1))
        form_layout.addRow("Date of Birth *:", self.dt_dob)

        # Course & Branch Layout
        course_branch_layout = QHBoxLayout()
        self.cmb_course = QComboBox()
        self.cmb_course.setEditable(True)
        self.cmb_course.addItems(AcademicController.get_courses())
        self.cmb_branch = QComboBox()
        self.cmb_branch.setEditable(True)
        self.cmb_branch.addItems(AcademicController.get_branches())
        course_branch_layout.addWidget(self.cmb_course, stretch=1)
        course_branch_layout.addWidget(self.cmb_branch, stretch=1)
        form_layout.addRow("Course & Branch:", course_branch_layout)

        # Academic Year & Semester Layout
        yr_sem_layout = QHBoxLayout()
        self.cmb_year = QComboBox()
        self.cmb_year.setEditable(True)
        self.cmb_year.addItems(["None"] + AcademicController.get_years())
        self.cmb_semester = QComboBox()
        self.cmb_semester.setEditable(True)
        self.cmb_semester.addItems(["None"] + AcademicController.get_semesters())
        yr_sem_layout.addWidget(self.cmb_year, stretch=1)
        yr_sem_layout.addWidget(self.cmb_semester, stretch=1)
        form_layout.addRow("Year & Semester:", yr_sem_layout)

        # Mobile Number
        self.txt_mobile = QLineEdit()
        self.txt_mobile.setPlaceholderText("10-Digit Mobile Number (e.g. 9876543210)")
        form_layout.addRow("Mobile Number *:", self.txt_mobile)

        # Aadhaar Number (Placed immediately BELOW Mobile Number and ABOVE Date of Admission)
        self.txt_aadhaar = QLineEdit()
        self.txt_aadhaar.setPlaceholderText("12-digit Aadhaar Number")
        self.txt_aadhaar.setMaxLength(12)
        form_layout.addRow("Aadhaar Number:", self.txt_aadhaar)

        # Date of Admission
        self.dt_admission = QDateEdit()
        self.dt_admission.setFixedHeight(34)
        self.dt_admission.setCalendarPopup(True)
        self.dt_admission.setDisplayFormat("dd-MM-yyyy")
        self.dt_admission.setDate(QDate.currentDate())
        form_layout.addRow("Date of Admission:", self.dt_admission)

        # Academic Session
        self.cmb_session = QComboBox()
        from services.session_service import session_manager
        active_sess = session_manager.get_active_session()
        sessions = SettingsController.get_academic_sessions()
        session_list = [s.session_name for s in sessions] if sessions else ["2024-2025", "2025-2026", "2026-2027"]
        if active_sess not in session_list:
            session_list.insert(0, active_sess)
        self.cmb_session.addItems(session_list)
        if not self.student:
            self.cmb_session.setCurrentText(active_sess)
        form_layout.addRow("Academic Session *:", self.cmb_session)

        # Status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.cmb_status)

        # Address
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(50)
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

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def load_student_data(self):
        s = self.student
        self.txt_admission_no.setText(s.admission_no)
        self.txt_roll_no.setText(s.roll_no or "")
        self.txt_name.setText(s.name)
        self.txt_father_name.setText(s.father_name)
        self.txt_mother_name.setText(s.mother_name or "")
        if getattr(s, "date_of_birth", None):
            self.dt_dob.setDate(QDate(s.date_of_birth.year, s.date_of_birth.month, s.date_of_birth.day))
        else:
            self.dt_dob.setDate(QDate(1900, 1, 1))

        if s.course:
            self.cmb_course.setCurrentText(s.course)
        if s.branch:
            self.cmb_branch.setCurrentText(s.branch)
        if s.year:
            self.cmb_year.setCurrentText(s.year)
        if s.semester:
            self.cmb_semester.setCurrentText(s.semester)
        self.txt_mobile.setText(s.mobile)
        self.txt_aadhaar.setText(getattr(s, "aadhaar_number", None) or "")

        if s.admission_date:
            self.dt_admission.setDate(QDate(s.admission_date.year, s.admission_date.month, s.admission_date.day))
        self.cmb_session.setCurrentText(s.academic_session)
        self.cmb_status.setCurrentText(s.status)
        self.txt_address.setPlainText(s.address or "")

    def save_student(self):
        adm_no = self.txt_admission_no.text().strip()
        name = self.txt_name.text().strip()
        father_name = self.txt_father_name.text().strip()
        course_name = self.cmb_course.currentText().strip()
        mobile = self.txt_mobile.text().strip()
        aadhaar = self.txt_aadhaar.text().strip()

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

        # Date of Birth Validation
        qdob = self.dt_dob.date()
        if qdob == QDate(1900, 1, 1):
            QMessageBox.warning(self, "Validation Error", "Date of Birth is required.")
            self.dt_dob.setFocus()
            return

        if qdob > QDate.currentDate():
            QMessageBox.warning(self, "Validation Error", "Date of Birth cannot be in the future.")
            self.dt_dob.setFocus()
            return

        dob_date = date(qdob.year(), qdob.month(), qdob.day())
        today = date.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        if age > 100 or age < 1:
            QMessageBox.warning(self, "Validation Error", "Please enter a realistic Date of Birth (Age must be between 1 and 100 years).")
            self.dt_dob.setFocus()
            return

        if not course_name:
            QMessageBox.warning(self, "Validation Error", "Course is required.")
            self.cmb_course.setFocus()
            return

        if not validate_indian_mobile(mobile):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 10-digit Indian Mobile Number.")
            self.txt_mobile.setFocus()
            return

        # Aadhaar Validation
        if aadhaar:
            if not aadhaar.isdigit() or len(aadhaar) != 12:
                QMessageBox.warning(self, "Validation Error", "Aadhaar Number must be exactly 12 numeric digits.")
                self.txt_aadhaar.setFocus()
                return

        qdate = self.dt_admission.date()
        admission_date = date(qdate.year(), qdate.month(), qdate.day())

        yr = self.cmb_year.currentText().strip()
        sem = self.cmb_semester.currentText().strip()

        data = {
            "admission_no": adm_no,
            "roll_no": self.txt_roll_no.text().strip(),
            "name": name,
            "father_name": father_name,
            "mother_name": self.txt_mother_name.text().strip(),
            "date_of_birth": dob_date,
            "course": course_name,
            "branch": self.cmb_branch.currentText().strip(),
            "year": "" if yr == "None" else yr,
            "semester": "" if sem == "None" else sem,
            "class_name": course_name,
            "section": "",
            "mobile": mobile,
            "aadhaar_number": aadhaar or None,
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
