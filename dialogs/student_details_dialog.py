"""
Student Details Dialog — Displays full student profile with photo, grouped details, and PDF Print support.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QFrame,
    QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from config.app_config import STUDENT_PHOTOS_DIR
from services.pdf_service import PDFService
from services.print_service import PrintService
from utils.helpers import format_date
from utils.logger import logger


class StudentDetailsDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle(f"Student Profile — {student.name if student else ''}")
        self.setMinimumSize(620, 520)
        self.resize(680, 580)
        self.setup_ui()

    def setup_ui(self):
        dialog_vbox = QVBoxLayout(self)
        dialog_vbox.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        if not self.student:
            main_layout.addWidget(QLabel("No student record loaded."))
            scroll.setWidget(container)
            dialog_vbox.addWidget(scroll)
            return

        s = self.student

        # Header Title Banner with Photo Display
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px;")
        hdr_layout = QHBoxLayout(hdr_frame)
        hdr_layout.setSpacing(15)

        title_v = QVBoxLayout()
        lbl_name = QLabel(s.name)
        lbl_name.setWordWrap(True)
        lbl_name.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e3a8a; border: none;")

        yr_sem_str = f"Year: {s.year or 'N/A'}  |  Semester: {s.semester or 'N/A'}"
        lbl_sub = QLabel(f"Adm. No: {s.admission_no}  |  Course: {s.course or 'General'}  |  {yr_sem_str}")
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b; border: none;")
        
        title_v.addWidget(lbl_name)
        title_v.addWidget(lbl_sub)

        status_lbl = QLabel(s.status.upper())
        status_bg = "#dcfce7" if s.status == "Active" else "#fee2e2"
        status_fg = "#166534" if s.status == "Active" else "#991b1b"
        status_lbl.setStyleSheet(f"background-color: {status_bg}; color: {status_fg}; font-weight: 800; font-size: 11px; padding: 4px 10px; border-radius: 4px; border: none;")
        title_v.addWidget(status_lbl, alignment=Qt.AlignLeft)

        hdr_layout.addLayout(title_v, stretch=1)

        # Photo Preview in Details Header
        lbl_photo = QLabel()
        lbl_photo.setFixedSize(80, 100)
        lbl_photo.setAlignment(Qt.AlignCenter)

        has_photo = False
        if getattr(s, "photo_path", None):
            photo_file = STUDENT_PHOTOS_DIR / s.photo_path
            if not photo_file.exists():
                photo_file = Path(s.photo_path)
            if photo_file.exists():
                pix = QPixmap(str(photo_file))
                if not pix.isNull():
                    scaled_pix = pix.scaled(80, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    lbl_photo.setPixmap(scaled_pix)
                    lbl_photo.setStyleSheet("border: 1px solid #1e3a8a; border-radius: 4px; background: #ffffff;")
                    has_photo = True

        if not has_photo:
            lbl_photo.setText("👨‍🎓")
            lbl_photo.setStyleSheet("font-size: 40px; background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 4px;")

        hdr_layout.addWidget(lbl_photo)
        main_layout.addWidget(hdr_frame)

        # Personal & Academic Details Group Box
        grp_academic = QGroupBox("Academic & Personal Information")
        grp_academic.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        f_academic = QFormLayout(grp_academic)
        f_academic.setSpacing(8)

        f_academic.addRow("Admission / Enrollment No.:", self._val_label(s.admission_no))
        f_academic.addRow("Student Name:", self._val_label(s.name))
        f_academic.addRow("Date of Birth:", self._val_label(format_date(getattr(s, "date_of_birth", None)) if getattr(s, "date_of_birth", None) else "N/A"))
        f_academic.addRow("Course / Program:", self._val_label(getattr(s, "course", None) or "General"))
        f_academic.addRow("Branch / Department:", self._val_label(getattr(s, "branch", None) or "General"))
        f_academic.addRow("Academic Year:", self._val_label(getattr(s, "year", None) or "N/A"))
        f_academic.addRow("Semester:", self._val_label(getattr(s, "semester", None) or "N/A"))
        f_academic.addRow("Academic Session:", self._val_label(s.academic_session))
        f_academic.addRow("Admission Date:", self._val_label(format_date(s.admission_date)))

        main_layout.addWidget(grp_academic)

        # Guardian & Contact Details Group Box
        grp_guardian = QGroupBox("Guardian & Contact Details")
        grp_guardian.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        f_guardian = QFormLayout(grp_guardian)
        f_guardian.setSpacing(8)

        f_guardian.addRow("Father's Name:", self._val_label(s.father_name))
        f_guardian.addRow("Mother's Name:", self._val_label(s.mother_name or "N/A"))
        f_guardian.addRow("Mobile Number:", self._val_label(s.mobile))
        f_guardian.addRow("Aadhaar Number:", self._val_label(getattr(s, "aadhaar_number", None) or "N/A"))
        f_guardian.addRow("Residential Address:", self._val_label(s.address or "N/A"))

        main_layout.addWidget(grp_guardian)

        # Action Buttons Toolbar (Print/PDF & Close Details)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_print_pdf = QPushButton("🖨️ Print / PDF Profile")
        self.btn_print_pdf.setFixedHeight(36)
        self.btn_print_pdf.setStyleSheet("""
            QPushButton {
                background-color: #1e3a8a;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.btn_print_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_print_pdf.clicked.connect(self.print_pdf_profile)

        btn_close = QPushButton("Close Details")
        btn_close.setFixedHeight(36)
        btn_close.setProperty("class", "SecondaryBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_print_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        main_layout.addLayout(btn_layout)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def print_pdf_profile(self):
        try:
            pdf_path = PDFService.generate_student_profile_pdf(self.student)
            PrintService.preview_pdf(pdf_path, self)
        except Exception as e:
            logger.error(f"Error generating/opening student profile PDF: {e}", exc_info=True)
            QMessageBox.critical(self, "PDF Error", f"Failed to generate student profile PDF:\n{str(e)}")

    def _val_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-weight: 600; color: #0f172a; border: none;")
        return lbl
