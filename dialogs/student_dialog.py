"""
Add / Edit Student Dialog with Compact Two-Column Layout, Photo Upload, Date of Birth, & Strict Validation.
"""

from typing import Optional, Dict, Any
from datetime import date
from pathlib import Path
import uuid
import shutil

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QPushButton, QMessageBox, QGroupBox, QFormLayout,
    QScrollArea, QFrame, QWidget, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QImage

from controllers.student_controller import StudentController
from controllers.settings_controller import SettingsController
from controllers.academic_controller import AcademicController
from config.app_config import STUDENT_PHOTOS_DIR
from utils.helpers import validate_indian_mobile, parse_date, format_date
from utils.logger import logger


class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.current_photo_path: Optional[str] = student.photo_path if (student and getattr(student, "photo_path", None)) else None
        self.setWindowTitle("Edit Student Details" if student else "Register New Student")
        self.setMinimumSize(780, 580)
        self.resize(860, 680)

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
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        group = QGroupBox("Student Information & Academic Details")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        group_vbox = QVBoxLayout(group)
        group_vbox.setContentsMargins(14, 14, 14, 14)
        group_vbox.setSpacing(12)

        # ---------------- TOP TWO-COLUMN SECTION (Info Left, Photo Right) ----------------
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(15)

        # Left Column: Primary Student Identity
        left_form = QFormLayout()
        left_form.setSpacing(10)

        self.txt_admission_no = QLineEdit()
        self.txt_admission_no.setFixedHeight(32)
        self.txt_admission_no.setPlaceholderText("e.g. ADM/2025/001")
        left_form.addRow("Admission / Enrollment No. *:", self.txt_admission_no)

        self.txt_name = QLineEdit()
        self.txt_name.setFixedHeight(32)
        self.txt_name.setPlaceholderText("Full Name of Student")
        left_form.addRow("Student Name *:", self.txt_name)

        self.txt_father_name = QLineEdit()
        self.txt_father_name.setFixedHeight(32)
        self.txt_father_name.setPlaceholderText("Father's Name")
        left_form.addRow("Father's Name *:", self.txt_father_name)

        self.txt_mother_name = QLineEdit()
        self.txt_mother_name.setFixedHeight(32)
        self.txt_mother_name.setPlaceholderText("Mother's Name")
        left_form.addRow("Mother's Name:", self.txt_mother_name)

        top_row_layout.addLayout(left_form, stretch=3)

        # Right Column: Student Photo Section
        photo_box = QGroupBox("Student Photo (Optional)")
        photo_box.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                margin-top: 0px;
                padding-top: 4px;
                background-color: #f8fafc;
            }
        """)
        photo_vbox = QVBoxLayout(photo_box)
        photo_vbox.setContentsMargins(8, 8, 8, 8)
        photo_vbox.setAlignment(Qt.AlignCenter)

        self.lbl_photo_frame = QLabel()
        self.lbl_photo_frame.setFixedSize(110, 135)
        self.lbl_photo_frame.setAlignment(Qt.AlignCenter)
        self.lbl_photo_frame.setStyleSheet("""
            QLabel {
                border: 2px dashed #94a3b8;
                border-radius: 6px;
                background-color: #ffffff;
                color: #64748b;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        photo_btn_layout = QHBoxLayout()
        photo_btn_layout.setSpacing(6)

        self.btn_upload_photo = QPushButton("Upload Photo")
        self.btn_upload_photo.setFixedHeight(28)
        self.btn_upload_photo.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.btn_upload_photo.setCursor(Qt.PointingHandCursor)
        self.btn_upload_photo.clicked.connect(self.choose_photo)

        self.btn_remove_photo = QPushButton("Remove")
        self.btn_remove_photo.setFixedHeight(28)
        self.btn_remove_photo.setStyleSheet("font-size: 11px; font-weight: bold; background-color: #fef2f2; color: #dc2626; border: 1px solid #fca5a5;")
        self.btn_remove_photo.setCursor(Qt.PointingHandCursor)
        self.btn_remove_photo.clicked.connect(self.remove_photo)

        self.update_photo_preview()

        photo_btn_layout.addWidget(self.btn_upload_photo)
        photo_btn_layout.addWidget(self.btn_remove_photo)

        photo_vbox.addWidget(self.lbl_photo_frame, alignment=Qt.AlignCenter)
        photo_vbox.addLayout(photo_btn_layout)

        top_row_layout.addWidget(photo_box, stretch=1)
        group_vbox.addLayout(top_row_layout)

        # ---------------- MAIN FORM FIELDS (Full Width Compact Layout) ----------------
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Date of Birth
        self.dt_dob = QDateEdit()
        self.dt_dob.setFixedHeight(32)
        self.dt_dob.setCalendarPopup(True)
        self.dt_dob.setDisplayFormat("dd-MM-yyyy")
        self.dt_dob.setMinimumDate(QDate(1900, 1, 1))
        self.dt_dob.setMaximumDate(QDate.currentDate())
        self.dt_dob.setSpecialValueText("Select Date of Birth")
        self.dt_dob.setDate(QDate(1900, 1, 1))
        form_layout.addRow("Date of Birth *:", self.dt_dob)

        # Course Category, Course & Branch Section
        cat_crs_layout = QHBoxLayout()
        cat_crs_layout.setSpacing(10)

        self.cmb_category = QComboBox()
        self.cmb_category.setFixedHeight(32)
        self.cmb_category.addItems(["UG", "PG"])
        self.cmb_category.currentTextChanged.connect(self.on_category_changed)

        self.cmb_course = QComboBox()
        self.cmb_course.setFixedHeight(32)
        self.cmb_course.addItems(AcademicController.get_courses_by_category("UG"))
        self.cmb_course.currentTextChanged.connect(self.on_course_changed)

        self.cmb_branch = QComboBox()
        self.cmb_branch.setFixedHeight(32)
        self.cmb_branch.addItems(AcademicController.get_branches())

        cat_crs_layout.addWidget(self.cmb_category, stretch=1)
        cat_crs_layout.addWidget(self.cmb_course, stretch=2)
        cat_crs_layout.addWidget(self.cmb_branch, stretch=1)
        form_layout.addRow("Category, Course & Branch *:", cat_crs_layout)

        # Year & Semester Row (Ordinal Format: 1st, 2nd, 1st Sem, etc.)
        yr_sem_layout = QHBoxLayout()
        yr_sem_layout.setSpacing(10)
        self.cmb_year = QComboBox()
        self.cmb_year.setFixedHeight(32)

        self.cmb_semester = QComboBox()
        self.cmb_semester.setFixedHeight(32)

        self.update_year_and_semester_options()

        yr_sem_layout.addWidget(self.cmb_year, stretch=1)
        yr_sem_layout.addWidget(self.cmb_semester, stretch=1)
        form_layout.addRow("Year & Semester:", yr_sem_layout)

        # Mobile Number & Aadhaar Number Row
        contact_layout = QHBoxLayout()
        contact_layout.setSpacing(10)
        self.txt_mobile = QLineEdit()
        self.txt_mobile.setFixedHeight(32)
        self.txt_mobile.setPlaceholderText("10-Digit Mobile Number *")

        self.txt_aadhaar = QLineEdit()
        self.txt_aadhaar.setFixedHeight(32)
        self.txt_aadhaar.setPlaceholderText("12-Digit Aadhaar (Optional)")
        self.txt_aadhaar.setMaxLength(12)

        contact_layout.addWidget(self.txt_mobile, stretch=1)
        contact_layout.addWidget(self.txt_aadhaar, stretch=1)
        form_layout.addRow("Mobile & Aadhaar:", contact_layout)

        # Date of Admission
        self.dt_admission = QDateEdit()
        self.dt_admission.setFixedHeight(32)
        self.dt_admission.setCalendarPopup(True)
        self.dt_admission.setDisplayFormat("dd-MM-yyyy")
        self.dt_admission.setDate(QDate.currentDate())
        form_layout.addRow("Date of Admission:", self.dt_admission)

        # Academic Session & Status Row
        sess_status_layout = QHBoxLayout()
        sess_status_layout.setSpacing(10)
        self.cmb_session = QComboBox()
        self.cmb_session.setFixedHeight(32)
        from services.session_service import session_manager
        active_sess = session_manager.get_active_session()
        sessions = SettingsController.get_academic_sessions()
        session_list = [s.session_name for s in sessions] if sessions else ["2024-2025", "2025-2026", "2026-2027"]
        if active_sess not in session_list:
            session_list.insert(0, active_sess)
        self.cmb_session.addItems(session_list)
        if not self.student:
            self.cmb_session.setCurrentText(active_sess)

        self.cmb_status = QComboBox()
        self.cmb_status.setFixedHeight(32)
        self.cmb_status.addItems(["Active", "Inactive"])
        self.cmb_status.setCurrentText("Active")

        sess_status_layout.addWidget(self.cmb_session, stretch=2)
        sess_status_layout.addWidget(self.cmb_status, stretch=1)
        form_layout.addRow("Session & Status *:", sess_status_layout)

        # Residential Address
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(55)
        form_layout.addRow("Residential Address:", self.txt_address)

        group_vbox.addLayout(form_layout)
        main_layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedHeight(36)
        self.btn_cancel.setProperty("class", "SecondaryBtn")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Student")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.save_student)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def update_photo_preview(self):
        if self.current_photo_path:
            full_path = STUDENT_PHOTOS_DIR / self.current_photo_path
            if not full_path.exists():
                full_path = Path(self.current_photo_path)

            if full_path.exists():
                pixmap = QPixmap(str(full_path))
                if not pixmap.isNull():
                    scaled_pix = pixmap.scaled(110, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.lbl_photo_frame.setPixmap(scaled_pix)
                    self.lbl_photo_frame.setStyleSheet("border: 1px solid #1e3a8a; border-radius: 6px; background-color: #ffffff;")
                    self.btn_upload_photo.setText("Change Photo")
                    self.btn_remove_photo.show()
                    return

        # Default placeholder
        self.lbl_photo_frame.clear()
        self.lbl_photo_frame.setText("STUDENT\nPHOTO\n(3:4 / ID)")
        self.lbl_photo_frame.setStyleSheet("""
            QLabel {
                border: 2px dashed #94a3b8;
                border-radius: 6px;
                background-color: #ffffff;
                color: #64748b;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        self.btn_upload_photo.setText("Upload Photo")
        self.btn_remove_photo.hide()

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Student Photo",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return

        try:
            src_path = Path(file_path)
            pix = QPixmap(str(src_path))
            if pix.isNull():
                QMessageBox.warning(self, "Invalid Image", "The selected file is not a valid image format.")
                return

            ext = src_path.suffix.lower() if src_path.suffix.lower() in [".jpg", ".jpeg", ".png"] else ".jpg"
            filename = f"photo_{uuid.uuid4().hex[:12]}{ext}"
            dest_path = STUDENT_PHOTOS_DIR / filename

            # Save scaled copy (max 600x800 for optimal storage & print quality)
            scaled = pix.scaled(600, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            scaled.save(str(dest_path))

            self.current_photo_path = filename
            self.update_photo_preview()
        except Exception as e:
            logger.error(f"Error processing student photo: {e}", exc_info=True)
            QMessageBox.critical(self, "Photo Error", f"Failed to save student photo: {str(e)}")

    def on_category_changed(self, cat_text: str):
        self.cmb_course.blockSignals(True)
        self.cmb_course.clear()
        courses = AcademicController.get_courses_by_category(cat_text)
        self.cmb_course.addItems(courses)
        self.cmb_course.blockSignals(False)
        self.on_course_changed(self.cmb_course.currentText())

    def on_course_changed(self, course_text: str):
        self.update_year_and_semester_options()

    def update_year_and_semester_options(self):
        course_text = self.cmb_course.currentText() if hasattr(self, "cmb_course") else ""
        years = AcademicController.get_years(course_name=course_text)
        semesters = AcademicController.get_semesters(course_name=course_text)

        self.cmb_year.blockSignals(True)
        curr_yr = self.cmb_year.currentText()
        self.cmb_year.clear()
        self.cmb_year.addItems(["None"] + years)
        if curr_yr in years:
            self.cmb_year.setCurrentText(curr_yr)
        self.cmb_year.blockSignals(False)

        self.cmb_semester.blockSignals(True)
        curr_sem = self.cmb_semester.currentText()
        self.cmb_semester.clear()
        self.cmb_semester.addItems(["None"] + semesters)
        if curr_sem in semesters:
            self.cmb_semester.setCurrentText(curr_sem)
        self.cmb_semester.blockSignals(False)

    def remove_photo(self):
        self.current_photo_path = None
        self.update_photo_preview()

    def load_student_data(self):
        s = self.student
        self.txt_admission_no.setText(s.admission_no)
        self.txt_name.setText(s.name)
        self.txt_father_name.setText(s.father_name)
        self.txt_mother_name.setText(s.mother_name or "")
        self.current_photo_path = getattr(s, "photo_path", None)
        self.update_photo_preview()

        cat = getattr(s, "course_category", None)
        if not cat and s.course:
            cat = "PG" if ("master" in s.course.lower() or "mpharm" in s.course.lower() or "pg" in s.course.lower()) else "UG"
        if cat:
            self.cmb_category.setCurrentText(cat)

        if getattr(s, "date_of_birth", None):
            self.dt_dob.setDate(QDate(s.date_of_birth.year, s.date_of_birth.month, s.date_of_birth.day))
        else:
            self.dt_dob.setDate(QDate(1900, 1, 1))

        if s.course:
            self.cmb_course.setCurrentText(s.course)
        if s.branch:
            self.cmb_branch.setCurrentText(s.branch)

        # Match Year / Semester with new ordinal format or fallback
        if s.year:
            idx = self.cmb_year.findText(s.year, Qt.MatchContains)
            if idx >= 0:
                self.cmb_year.setCurrentIndex(idx)
            else:
                self.cmb_year.setCurrentText(s.year)

        if s.semester:
            idx = self.cmb_semester.findText(s.semester, Qt.MatchContains)
            if idx >= 0:
                self.cmb_semester.setCurrentIndex(idx)
            else:
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
        category_name = self.cmb_category.currentText().strip()
        course_name = self.cmb_course.currentText().strip()
        mobile = self.txt_mobile.text().strip()
        aadhaar = self.txt_aadhaar.text().strip()

        if not adm_no:
            QMessageBox.warning(self, "Validation Error", "Admission / Enrollment No. is required.")
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
            "roll_no": "",
            "name": name,
            "father_name": father_name,
            "mother_name": self.txt_mother_name.text().strip(),
            "date_of_birth": dob_date,
            "course_category": category_name,
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
            "status": self.cmb_status.currentText(),
            "photo_path": self.current_photo_path
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
