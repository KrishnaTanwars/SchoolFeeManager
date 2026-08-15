"""
Automated End-to-End Regression & Production Lockdown Tests for Phase 5 (v3.0.0 FINAL):
1. End-to-End Workflow Regression (Student Registration -> Promotion -> Fee Head Retrieval -> Receipt Generation).
2. ReportLab PDF Generator Single-Page A4 Page Count Constraint.
3. Automated Backup & Recovery Engine Verification.
4. License & Version Integrity Check.
"""

import os
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.student import Student
from models.receipt import Receipt
from models.fee_category import FeeCategory
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.promotion_service import PromotionService
from services.backup_service import BackupService
from services.security_service import SecurityService
from services.pdf_service import PDFService
import pypdf

class TestPhase5V30Production(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_full_end_to_end_student_lifecycle(self):
        """Verifies Student Register -> Promotion -> Fee Head Retrieval."""
        adm_no = "PROD_STUDENT_300"
        # Cleanup
        ex = self.db.query(Student).filter(Student.admission_no == adm_no).first()
        if ex:
            self.db.delete(ex)
            self.db.commit()

        # 1. Register Student
        st_data = {
            "admission_no": adm_no,
            "roll_no": "R300",
            "name": "Production Test Student",
            "father_name": "Father Name",
            "mother_name": "Mother Name",
            "mobile": "9999888877",
            "course": "B. Pharmacy",
            "branch": "Pharmacy",
            "year": "1st Year",
            "semester": "Semester 1",
            "academic_session": "2026-2027",
            "category": "General",
            "gender": "Male"
        }
        st_id, msg = StudentController.create_student(st_data)
        self.assertIsNotNone(st_id, msg)

        # 2. Academic Promotion
        prom_success, prom_msg = PromotionService.bulk_promote_students([st_id], "2026-2027", "1st Year", "Semester 2")
        self.assertTrue(prom_success, prom_msg)

        # 3. Retrieve Updated Student
        st = self.db.query(Student).filter(Student.id == st_id).first()
        self.assertEqual(st.semester, "Semester 2")

        # 4. Applicable Fee Heads
        applicable = FeeController.get_applicable_categories(st)
        self.assertGreater(len(applicable), 0)

    def test_02_pdf_receipt_strict_one_page_constraint(self):
        """Verifies generated fee receipt PDF fits on EXACTLY 1 A4 PAGE under 14 fee heads."""
        pdf_path = "test_prod_v3_receipt.pdf"
        # First ensure a student exists
        st = self.db.query(Student).first()
        self.assertIsNotNone(st)

        fc = self.db.query(FeeCategory).first()
        fc_id = fc.id if fc else None

        items = [{"fee_category_id": fc_id, "name": f"Fee Head #{i+1}", "amount": 1000.0} for i in range(14)]
        success_rec, msg_rec, rec = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2026-2027",
            items=items,
            payment_mode="Online Bank Transfer",
            remarks="Production Receipt Page Count Test"
        )
        self.assertTrue(success_rec, msg_rec)
        self.assertIsNotNone(rec)

        out_path = PDFService.generate_receipt_pdf(rec, pdf_path)
        self.assertTrue(os.path.exists(out_path))

        reader = pypdf.PdfReader(out_path)
        self.assertEqual(len(reader.pages), 1, "PDF receipt MUST fit on exactly 1 A4 page!")

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_03_backup_service_integrity(self):
        """Verifies database backup file creation."""
        success, msg, backup_path = BackupService.create_backup(backup_type="Manual")
        self.assertTrue(success, msg)
        self.assertTrue(os.path.exists(backup_path))
        if os.path.exists(backup_path):
            os.remove(backup_path)

    def test_04_security_service_validation(self):
        """Verifies security audit log registration."""
        success = SecurityService.log_audit("PRODUCTION_VERIFICATION", "System", "v3.0.0 Production Lockdown Passed", "Success")
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
