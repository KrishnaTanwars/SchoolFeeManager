"""
Add / Edit Student Dialog with Strict Validation & Enhanced Date Picker.
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

import os
import shutil
import uuid
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog
from config.app_config import STUDENT_PHOTOS_DIR

class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.photo_path_val = None
        self.setWindowTitle("Edit Student Details" if student else "Register New Student")
        self.setMinimumSize(540, 560)
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

        # Photo Header Layout
        photo_group = QGroupBox("Student Photo")
        photo_box_layout = QHBoxLayout(photo_group)

        self.lbl_photo_preview = QLabel()
        self.lbl_photo_preview.setFixedSize(80, 95)
        self.lbl_photo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_photo_preview.setStyleSheet("border: 1px dashed #94a3b8; border-radius: 4px; background: #f8fafc;")
        self.lbl_photo_preview.setText("No Photo")

        photo_btn_layout = QVBoxLayout()
        self.btn_choose_photo = QPushButton("📷 Choose Photo")
        self.btn_choose_photo.clicked.connect(self.choose_photo)
        self.btn_remove_photo = QPushButton("🗑️ Remove Photo")
        self.btn_remove_photo.clicked.connect(self.remove_photo)
        photo_btn_layout.addWidget(self.btn_choose_photo)
        photo_btn_layout.addWidget(self.btn_remove_photo)
        photo_btn_layout.addStretch()

        photo_box_layout.addWidget(self.lbl_photo_preview)
        photo_box_layout.addLayout(photo_btn_layout)
        photo_box_layout.addStretch()
        main_layout.addWidget(photo_group)

        group = QGroupBox("Student Information & Academic Structure")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(10)

        # Admission Number (Auto-Incremented)
        self.txt_admission_no = QLineEdit()
        self.txt_admission_no.setPlaceholderText("e.g. ADM/2026/0001")
        if not self.student:
            auto_adm = StudentController.get_next_admission_no()
            self.txt_admission_no.setText(auto_adm)
        form_layout.addRow("Admission Number *:", self.txt_admission_no)

        # Enrollment Number (Manual Entry)
        self.txt_enrollment_no = QLineEdit()
        self.txt_enrollment_no.setPlaceholderText("e.g. ENR2026889 (Optional / Manual)")
        form_layout.addRow("Enrollment Number:", self.txt_enrollment_no)

        # Student Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Full Name of Student")
        form_layout.addRow("Student Name *:", self.txt_name)

        # Date of Birth
        self.dt_dob = QDateEdit()
        self.dt_dob.setFixedHeight(34)
        self.dt_dob.setCalendarPopup(True)
        self.dt_dob.setDisplayFormat("dd-MM-yyyy")
        self.dt_dob.setDate(QDate(2005, 1, 1))
        self.dt_dob.setMaximumDate(QDate.currentDate())
        form_layout.addRow("Date of Birth:", self.dt_dob)

        # Aadhaar Number
        self.txt_aadhaar = QLineEdit()
        self.txt_aadhaar.setPlaceholderText("12-Digit Aadhaar Number (Optional)")
        self.txt_aadhaar.setMaxLength(12)
        form_layout.addRow("Aadhaar Number:", self.txt_aadhaar)

        # Father Name
        self.txt_father_name = QLineEdit()
        self.txt_father_name.setPlaceholderText("Father's Name")
        form_layout.addRow("Father's Name *:", self.txt_father_name)

        # Mother Name
        self.txt_mother_name = QLineEdit()
        self.txt_mother_name.setPlaceholderText("Mother's Name")
        form_layout.addRow("Mother's Name:", self.txt_mother_name)

        # Course & Branch Layout
        course_branch_layout = QHBoxLayout()
        self.cmb_course = QComboBox()
        self.cmb_course.setEditable(True)
        self.cmb_course.addItems(AcademicController.get_courses())
        self.cmb_course.currentTextChanged.connect(self.on_course_changed)
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
            self.cmb_session.addItems(["2024-2025", "2025-2026", "2026-2027"])
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

    def on_course_changed(self, course_name):
        curr_yr = self.cmb_year.currentText()
        curr_sem = self.cmb_semester.currentText()

        self.cmb_year.blockSignals(True)
        self.cmb_semester.blockSignals(True)

        self.cmb_year.clear()
        self.cmb_year.addItems(["None"] + AcademicController.get_years(course_name))
        self.cmb_semester.clear()
        self.cmb_semester.addItems(["None"] + AcademicController.get_semesters(course_name=course_name))

        if self.cmb_year.findText(curr_yr) >= 0:
            self.cmb_year.setCurrentText(curr_yr)
        if self.cmb_semester.findText(curr_sem) >= 0:
            self.cmb_semester.setCurrentText(curr_sem)

        self.cmb_year.blockSignals(False)
        self.cmb_semester.blockSignals(False)

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            ext = Path(file_path).suffix
            dest_name = f"photo_{uuid.uuid4().hex[:12]}{ext}"
            STUDENT_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
            dest_path = STUDENT_PHOTOS_DIR / dest_name
            shutil.copy2(file_path, dest_path)
            self.photo_path_val = dest_name
            self.update_photo_preview(dest_path)

    def remove_photo(self):
        self.photo_path_val = None
        self.lbl_photo_preview.setPixmap(QPixmap())
        self.lbl_photo_preview.setText("No Photo")

    def update_photo_preview(self, path_or_str):
        p = Path(path_or_str)
        if not p.exists():
            p = STUDENT_PHOTOS_DIR / str(path_or_str)
        if p.exists():
            pix = QPixmap(str(p))
            if not pix.isNull():
                scaled = pix.scaled(80, 95, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_photo_preview.setPixmap(scaled)
                self.lbl_photo_preview.setText("")
                return
        self.lbl_photo_preview.setPixmap(QPixmap())
        self.lbl_photo_preview.setText("No Photo")

    def load_student_data(self):
        s = self.student
        self.txt_admission_no.setText(s.admission_no)
        self.txt_enrollment_no.setText(getattr(s, "enrollment_no", "") or "")
        self.txt_name.setText(s.name)
        self.txt_father_name.setText(s.father_name)
        self.txt_mother_name.setText(s.mother_name or "")
        if getattr(s, "date_of_birth", None):
            self.dt_dob.setDate(QDate(s.date_of_birth.year, s.date_of_birth.month, s.date_of_birth.day))
        self.txt_aadhaar.setText(getattr(s, "aadhaar_number", "") or "")
        if getattr(s, "photo_path", None):
            self.photo_path_val = s.photo_path
            self.update_photo_preview(s.photo_path)
        if s.course:
            self.cmb_course.setCurrentText(s.course)
        if s.branch:
            self.cmb_branch.setCurrentText(s.branch)
        if s.year:
            self.cmb_year.setCurrentText(s.year)
        if s.semester:
            self.cmb_semester.setCurrentText(s.semester)
        self.txt_mobile.setText(s.mobile)
        if s.admission_date:
            self.dt_admission.setDate(QDate(s.admission_date.year, s.admission_date.month, s.admission_date.day))
        self.cmb_session.setCurrentText(s.academic_session)
        self.cmb_status.setCurrentText(s.status)
        self.txt_address.setPlainText(s.address or "")

    def save_student(self):
        adm_no = self.txt_admission_no.text().strip()
        enr_no = self.txt_enrollment_no.text().strip()
        name = self.txt_name.text().strip()
        father_name = self.txt_father_name.text().strip()
        course_name = self.cmb_course.currentText().strip()
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
        if not course_name:
            QMessageBox.warning(self, "Validation Error", "Course is required.")
            self.cmb_course.setFocus()
            return
        if not validate_indian_mobile(mobile):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 10-digit Indian Mobile Number.")
            self.txt_mobile.setFocus()
            return

        yr = self.cmb_year.currentText().strip()
        sem = self.cmb_semester.currentText().strip()

        # Validate course structure
        is_valid_struct, struct_msg = AcademicController.validate_course_structure(course_name, yr, sem)
        if not is_valid_struct:
            QMessageBox.warning(self, "Academic Structure Conflict", struct_msg)
            return

        qdate = self.dt_admission.date()
        admission_date = date(qdate.year(), qdate.month(), qdate.day())

        dob_qdate = self.dt_dob.date()
        dob_date = date(dob_qdate.year(), dob_qdate.month(), dob_qdate.day())

        aadhaar_val = self.txt_aadhaar.text().strip()

        data = {
            "admission_no": adm_no,
            "enrollment_no": enr_no,
            "roll_no": "",
            "name": name,
            "father_name": father_name,
            "mother_name": self.txt_mother_name.text().strip(),
            "course": course_name,
            "branch": self.cmb_branch.currentText().strip(),
            "year": "" if yr == "None" else yr,
            "semester": "" if sem == "None" else sem,
            "class_name": course_name,
            "section": "",
            "mobile": mobile,
            "date_of_birth": dob_date,
            "aadhaar_number": aadhaar_val,
            "photo_path": self.photo_path_val,
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
