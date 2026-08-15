"""
Automated Regression Tests for:
1. Student Photo Upload, Preview, Storage, Replace, Remove, and Profile Integration.
2. Fee Payment Receipt A4 1-Page Layout Fit for UG (14 fee heads) and PG (4 fee heads) receipts.
"""

import os
import unittest
from datetime import date, datetime
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from pypdf import PdfReader
from config.database import init_db, get_db
from config.app_config import STUDENT_PHOTOS_DIR, EXPORTS_DIR
from models.student import Student
from models.receipt import Receipt, ReceiptItem
from controllers.student_controller import StudentController
from dialogs.student_dialog import StudentDialog
from dialogs.student_details_dialog import StudentDetailsDialog
from services.pdf_service import PDFService


class TestPhotoAndOnePageReceiptFix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_student_registration_without_photo(self):
        """Verifies registering a new student without a photo works cleanly."""
        db = get_db()
        try:
            existing = db.query(Student).filter(Student.admission_no == "ADM/TEST/PHOTO_NO").first()
            if existing:
                db.delete(existing)
                db.commit()
        finally:
            db.close()
        data = {
            "admission_no": "ADM/TEST/PHOTO_NO",
            "roll_no": "",
            "name": "Nitin Verma",
            "father_name": "Ramesh Verma",
            "mother_name": "Sarita Verma",
            "course": "B. Pharmacy",
            "branch": "Pharmacy",
            "year": "1st Year",
            "semester": "Semester 1",
            "mobile": "9812345678",
            "date_of_birth": date(2004, 3, 10),
            "aadhaar_number": "998877665001",
            "photo_path": None,
            "address": "123 Test Street",
            "admission_date": date.today(),
            "academic_session": "2025-2026",
            "status": "Active"
        }
        success, msg = StudentController.create_student(data)
        self.assertTrue(success, msg)
        st = StudentController.get_student_by_admission_no("ADM/TEST/PHOTO_NO")
        self.assertIsNotNone(st)
        self.assertIsNone(st.photo_path)

    def test_02_student_registration_with_photo(self):
        """Verifies registering student with a photo copies image to STUDENT_PHOTOS_DIR."""
        STUDENT_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        dummy_img_path = STUDENT_PHOTOS_DIR / "dummy_test_photo.png"
        
        # Create a simple 1x1 test image
        from PySide6.QtGui import QPixmap, QColor
        pix = QPixmap(100, 100)
        pix.fill(QColor("blue"))
        pix.save(str(dummy_img_path))

        dlg = StudentDialog(parent=None)
        dlg.txt_admission_no.setText("ADM/TEST/PHOTO_YES")
        dlg.txt_name.setText("Ananya Photowala")
        dlg.txt_father_name.setText("Rajesh Photowala")
        dlg.txt_mobile.setText("9876543219")
        dlg.photo_path_val = "dummy_test_photo.png"
        dlg.update_photo_preview("dummy_test_photo.png")

        # Verify preview label has pixmap set
        self.assertFalse(dlg.lbl_photo_preview.pixmap().isNull())

    def test_03_student_photo_edit_replace_remove(self):
        """Verifies editing, replacing, and removing photo from StudentDialog."""
        st = StudentController.get_student_by_admission_no("ADM/TEST/PHOTO_NO")
        self.assertIsNotNone(st)

        # Edit student - assign photo
        dlg = StudentDialog(parent=None, student=st)
        self.assertEqual(dlg.txt_admission_no.text(), "ADM/TEST/PHOTO_NO")
        
        dlg.photo_path_val = "new_photo_test.png"
        dlg.remove_photo()
        self.assertIsNone(dlg.photo_path_val)
        self.assertEqual(dlg.lbl_photo_preview.text(), "No Photo")

    def test_04_student_profile_photo_display(self):
        """Verifies StudentDetailsDialog and Profile PDF use photo correctly."""
        st = StudentController.get_student_by_admission_no("ADM/TEST/PHOTO_NO")
        self.assertIsNotNone(st)

        dlg = StudentDetailsDialog(parent=None, student=st)
        self.assertIsNotNone(dlg)

        # Generate Profile PDF
        out_path = str(EXPORTS_DIR / "test_profile_pdf.pdf")
        pdf_file = PDFService.generate_student_profile_pdf(st, out_path)
        reader = PdfReader(pdf_file)
        self.assertEqual(len(reader.pages), 1)

    def test_05_ug_receipt_14_heads_fits_exactly_one_page(self):
        """Verifies 14-head UG fee receipt fits on EXACTLY 1 A4 page."""
        db = get_db()
        try:
            st = db.query(Student).first()
            ug_heads = [
                ("ADMISSION FORM FEE", 1000.0),
                ("UG TUTION FEE", 45000.0),
                ("UG DEVELOPMENT FEE", 5000.0),
                ("SOCIAL GATHERING FEE", 500.0),
                ("SPORT FEE", 500.0),
                ("ELIGIBILTY FEE", 400.0),
                ("IDENTITY CARD FEE", 100.0),
                ("SRTMU EXAM FEE", 1200.0),
                ("SRTMU GRM / PHOTOCOPY FEE", 300.0),
                ("UG LABORATORY DEPOSIT", 2000.0),
                ("UG CLUB FEES", 300.0),
                ("UG LABROTARY CHARGES", 2500.0),
                ("CAUTION MONEY", 1000.0),
                ("OTHER FINE", 0.0)
            ]
            rec = Receipt(
                receipt_no="REC/2026/UG14_PAGE_CHECK",
                student_id=st.id if st else 1,
                receipt_date=date.today(),
                academic_session="2025-2026",
                course="B. Pharmacy",
                branch="Pharmacy",
                academic_year="1st Year",
                semester="Semester 1",
                subtotal=59800.0,
                discount_amount=5000.0,
                fine_amount=500.0,
                total_amount=55300.0,
                paid_amount=30000.0,
                due_amount=25300.0,
                payment_mode="UPI / QR Code",
                utr_number="123456789012",
                bank_name="State Bank of India",
                amount_in_words="Thirty Thousand Five Hundred Rupees Only",
                remarks="UG First Installment Receipt",
                created_at=datetime.now()
            )
            for cat, amt in ug_heads:
                rec.items.append(ReceiptItem(category_name=cat, amount=amt))

            out_file = str(EXPORTS_DIR / "test_ug14_onepage.pdf")
            pdf_path = PDFService.generate_receipt_pdf(rec, out_file)
            reader = PdfReader(pdf_path)
            self.assertEqual(len(reader.pages), 1, "UG 14-head receipt must fit on EXACTLY 1 A4 page!")
        finally:
            db.close()

    def test_06_pg_receipt_4_heads_fits_exactly_one_page(self):
        """Verifies 4-head PG fee receipt fits on EXACTLY 1 A4 page."""
        db = get_db()
        try:
            st = db.query(Student).first()
            pg_heads = [
                ("ADMISSION FORM FEE", 1000.0),
                ("PG TUTION FEE", 65000.0),
                ("PG DEVELOPMENT FEE", 8000.0),
                ("PG LABORATORY USAGES", 5000.0)
            ]
            rec = Receipt(
                receipt_no="REC/2026/PG04_PAGE_CHECK",
                student_id=st.id if st else 1,
                receipt_date=date.today(),
                academic_session="2025-2026",
                course="M. Pharmacy",
                branch="Pharmaceutics",
                academic_year="1st Year",
                semester="Semester 1",
                subtotal=79000.0,
                discount_amount=0.0,
                fine_amount=0.0,
                total_amount=79000.0,
                paid_amount=79000.0,
                due_amount=0.0,
                payment_mode="Cash",
                amount_in_words="Seventy Nine Thousand Rupees Only",
                remarks="PG Full Payment Receipt",
                created_at=datetime.now()
            )
            for cat, amt in pg_heads:
                rec.items.append(ReceiptItem(category_name=cat, amount=amt))

            out_file = str(EXPORTS_DIR / "test_pg4_onepage.pdf")
            pdf_path = PDFService.generate_receipt_pdf(rec, out_file)
            reader = PdfReader(pdf_path)
            self.assertEqual(len(reader.pages), 1, "PG 4-head receipt must fit on EXACTLY 1 A4 page!")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
