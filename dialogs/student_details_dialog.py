"""
Student Details Dialog — Displays full student profile in a clean, grouped card layout.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from utils.helpers import format_date

class StudentDetailsDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle(f"Student Details — {student.name if student else ''}")
        self.setMinimumSize(580, 520)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        if not self.student:
            main_layout.addWidget(QLabel("No student record loaded."))
            return

        s = self.student

        # Header Title Banner
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px;")
        hdr_layout = QHBoxLayout(hdr_frame)

        lbl_avatar = QLabel("👨‍🎓")
        lbl_avatar.setStyleSheet("font-size: 32px; border: none;")
        hdr_layout.addWidget(lbl_avatar)

        title_v = QVBoxLayout()
        lbl_name = QLabel(s.name)
        lbl_name.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e3a8a; border: none;")
        lbl_sub = QLabel(f"Adm. No: {s.admission_no}  |  Class: {s.class_name} ({s.section or 'A'})  |  Session: {s.academic_session}")
        lbl_sub.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b; border: none;")
        title_v.addWidget(lbl_name)
        title_v.addWidget(lbl_sub)

        hdr_layout.addLayout(title_v)
        hdr_layout.addStretch()

        status_lbl = QLabel(s.status.upper())
        status_bg = "#dcfce7" if s.status == "Active" else "#fee2e2"
        status_fg = "#166534" if s.status == "Active" else "#991b1b"
        status_lbl.setStyleSheet(f"background-color: {status_bg}; color: {status_fg}; font-weight: 800; font-size: 11px; padding: 4px 10px; border-radius: 4px; border: none;")
        hdr_layout.addWidget(status_lbl)

        main_layout.addWidget(hdr_frame)

        # Personal & Academic Details Group Box
        grp_academic = QGroupBox("Academic & Personal Information")
        grp_academic.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        f_academic = QFormLayout(grp_academic)
        f_academic.setSpacing(8)

        f_academic.addRow("Admission Number:", self._val_label(s.admission_no))
        f_academic.addRow("Roll Number:", self._val_label(s.roll_no or "N/A"))
        f_academic.addRow("Student Name:", self._val_label(s.name))
        f_academic.addRow("Class & Section:", self._val_label(f"{s.class_name} - Sec {s.section or 'A'}"))
        f_academic.addRow("Course / Stream:", self._val_label(getattr(s, "course", None) or "General"))
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
        f_guardian.addRow("Residential Address:", self._val_label(s.address or "N/A"))

        main_layout.addWidget(grp_guardian)

        # Action / Close Bar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_close = QPushButton("Close Details")
        btn_close.setFixedWidth(120)
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(btn_close)
        main_layout.addLayout(btn_layout)

    def _val_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: 600; color: #0f172a; border: none;")
        return lbl
