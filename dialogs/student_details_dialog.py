"""
Student Details Dialog — Displays full student profile in a clean, grouped card layout.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QFrame,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from utils.helpers import format_date

from pathlib import Path
from PySide6.QtGui import QPixmap
from config.app_config import STUDENT_PHOTOS_DIR

class StudentDetailsDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle(f"Student Profile — {student.name if student else ''}")
        self.setMinimumSize(520, 480)
        self.resize(600, 560)
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

        # Header Title Banner
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px;")
        hdr_layout = QHBoxLayout(hdr_frame)

        lbl_photo = QLabel()
        lbl_photo.setFixedSize(70, 85)
        lbl_photo.setAlignment(Qt.AlignCenter)
        has_photo = False
        if getattr(s, "photo_path", None):
            photo_file = STUDENT_PHOTOS_DIR / s.photo_path
            if not photo_file.exists():
                photo_file = Path(s.photo_path)
            if photo_file.exists():
                pix = QPixmap(str(photo_file))
                if not pix.isNull():
                    scaled_pix = pix.scaled(70, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    lbl_photo.setPixmap(scaled_pix)
                    lbl_photo.setStyleSheet("border: 1px solid #1e3a8a; border-radius: 4px; background: #ffffff;")
                    has_photo = True
        if not has_photo:
            lbl_photo.setText("👨‍🎓")
            lbl_photo.setStyleSheet("font-size: 32px; border: 1px dashed #cbd5e1; border-radius: 4px; background: #ffffff;")

        hdr_layout.addWidget(lbl_photo)

        title_v = QVBoxLayout()
        lbl_name = QLabel(s.name)
        lbl_name.setWordWrap(True)
        lbl_name.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e3a8a; border: none;")
        lbl_sub = QLabel(f"Adm No: {s.admission_no}  |  Enroll No: {getattr(s, 'enrollment_no', None) or 'N/A'}  |  Course: {s.course or 'General'}  |  Semester: {getattr(s, 'semester', None) or 'N/A'}")
        lbl_sub.setWordWrap(True)
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
        f_academic.addRow("Enrollment Number:", self._val_label(getattr(s, "enrollment_no", None) or "N/A"))
        f_academic.addRow("Student Name:", self._val_label(s.name))
        f_academic.addRow("Date of Birth:", self._val_label(format_date(getattr(s, "date_of_birth", None)) if getattr(s, "date_of_birth", None) else "N/A"))
        f_academic.addRow("Aadhaar Number:", self._val_label(getattr(s, "aadhaar_number", None) or "N/A"))
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
        f_guardian.addRow("Residential Address:", self._val_label(s.address or "N/A"))

        main_layout.addWidget(grp_guardian)

        # Fee Status Summary & Payment History Group Box
        grp_fee = QGroupBox("Fee & Payment History Summary")
        grp_fee.setStyleSheet("QGroupBox { font-weight: bold; color: #1e3a8a; }")
        v_fee = QVBoxLayout(grp_fee)
        v_fee.setSpacing(10)

        # Calculate student fee metrics
        from config.database import get_db
        from models.receipt import Receipt
        db = get_db()
        receipts = []
        tot_paid = 0.0
        tot_billed = 0.0
        curr_due = 0.0
        try:
            receipts = db.query(Receipt).filter(Receipt.student_id == s.id).order_by(Receipt.id.desc()).all()
            for r in receipts:
                tot_paid += (r.paid_amount or 0.0)
                tot_billed += (r.total_amount or 0.0)
            if receipts:
                curr_due = receipts[0].due_amount or 0.0
        except Exception:
            pass
        finally:
            db.close()

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        # Card 1: Total Paid
        c1 = QFrame()
        c1.setStyleSheet("background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 8px;")
        v1 = QVBoxLayout(c1)
        v1.setContentsMargins(6,6,6,6)
        lbl_c1_t = QLabel("TOTAL PAID")
        lbl_c1_t.setStyleSheet("font-size: 10px; font-weight: 700; color: #166534; border: none;")
        lbl_c1_v = QLabel(f"₹ {tot_paid:,.2f}")
        lbl_c1_v.setStyleSheet("font-size: 15px; font-weight: 800; color: #15803d; border: none;")
        v1.addWidget(lbl_c1_t)
        v1.addWidget(lbl_c1_v)

        # Card 2: Total Billed
        c2 = QFrame()
        c2.setStyleSheet("background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 8px;")
        v2 = QVBoxLayout(c2)
        v2.setContentsMargins(6,6,6,6)
        lbl_c2_t = QLabel("TOTAL BILLED")
        lbl_c2_t.setStyleSheet("font-size: 10px; font-weight: 700; color: #1e40af; border: none;")
        lbl_c2_v = QLabel(f"₹ {tot_billed:,.2f}")
        lbl_c2_v.setStyleSheet("font-size: 15px; font-weight: 800; color: #1d4ed8; border: none;")
        v2.addWidget(lbl_c2_t)
        v2.addWidget(lbl_c2_v)

        # Card 3: Outstanding Due
        c3 = QFrame()
        due_bg = "#fef2f2" if curr_due > 0 else "#f8fafc"
        due_border = "#fecaca" if curr_due > 0 else "#cbd5e1"
        due_fg = "#b91c1c" if curr_due > 0 else "#047857"
        c3.setStyleSheet(f"background-color: {due_bg}; border: 1px solid {due_border}; border-radius: 6px; padding: 8px;")
        v3 = QVBoxLayout(c3)
        v3.setContentsMargins(6,6,6,6)
        lbl_c3_t = QLabel("OUTSTANDING DUE")
        lbl_c3_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {due_fg}; border: none;")
        lbl_c3_v = QLabel(f"₹ {curr_due:,.2f}" if curr_due > 0 else "₹ 0.00 (PAID)")
        lbl_c3_v.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {due_fg}; border: none;")
        v3.addWidget(lbl_c3_t)
        v3.addWidget(lbl_c3_v)

        cards_layout.addWidget(c1)
        cards_layout.addWidget(c2)
        cards_layout.addWidget(c3)
        v_fee.addLayout(cards_layout)

        # Payment Receipts Mini Table
        if receipts:
            from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
            tbl_receipts = QTableWidget()
            tbl_receipts.setColumnCount(5)
            tbl_receipts.setHorizontalHeaderLabels(["Receipt No", "Date", "Session", "Mode", "Paid (₹)"])
            tbl_receipts.setRowCount(len(receipts))
            tbl_receipts.setFixedHeight(120)
            tbl_receipts.verticalHeader().setVisible(False)
            tbl_receipts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tbl_receipts.setStyleSheet("QTableWidget { background-color: #ffffff; border: 1px solid #e2e8f0; font-size: 11px; } QHeaderView::section { font-weight: bold; background-color: #f1f5f9; }")

            for row, r in enumerate(receipts):
                tbl_receipts.setItem(row, 0, QTableWidgetItem(r.receipt_no))
                tbl_receipts.setItem(row, 1, QTableWidgetItem(format_date(r.receipt_date)))
                tbl_receipts.setItem(row, 2, QTableWidgetItem(r.academic_session or "N/A"))
                tbl_receipts.setItem(row, 3, QTableWidgetItem(r.payment_mode or "Cash"))
                tbl_receipts.setItem(row, 4, QTableWidgetItem(f"₹ {(r.paid_amount or 0.0):,.2f}"))

            v_fee.addWidget(tbl_receipts)
        else:
            lbl_no_rec = QLabel("No past fee payment receipts recorded for this student.")
            lbl_no_rec.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
            v_fee.addWidget(lbl_no_rec)

        main_layout.addWidget(grp_fee)

        # Action / Close Bar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        from PySide6.QtWidgets import QMessageBox
        self.btn_print = QPushButton("🖨️  Print Single-Page Profile (PDF)")
        self.btn_print.setFixedHeight(36)
        self.btn_print.setStyleSheet("background-color: #1e3a8a; color: #ffffff; font-weight: bold; padding: 0 14px; border-radius: 4px;")
        self.btn_print.setCursor(Qt.PointingHandCursor)
        self.btn_print.clicked.connect(self.print_profile_pdf)

        btn_close = QPushButton("Close Profile")
        btn_close.setFixedWidth(120)
        btn_close.setFixedHeight(36)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(btn_close)
        main_layout.addLayout(btn_layout)

        scroll.setWidget(container)
        dialog_vbox.addWidget(scroll)

    def print_profile_pdf(self):
        if not self.student:
            return
        try:
            from services.pdf_service import PDFService
            from PySide6.QtWidgets import QMessageBox
            pdf_path = PDFService.generate_student_profile_pdf(self.student)

            import os, sys
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", pdf_path])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", pdf_path])

            QMessageBox.information(
                self,
                "Profile PDF Generated",
                f"Student Profile (Single-Page PDF) generated successfully:\n\n{pdf_path}\n\nThe PDF has been opened in your system's default PDF viewer."
            )
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "PDF Generation Error", f"Failed to generate profile PDF:\n{str(e)}")

    def _val_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-weight: 600; color: #0f172a; border: none;")
        return lbl

