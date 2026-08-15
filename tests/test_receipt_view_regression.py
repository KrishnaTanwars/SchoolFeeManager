"""
Regression Test Suite for ReceiptView UI, Student Card Reset, and Full Receipt Generation Workflow.
"""

import os
import unittest
from datetime import date
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.student import Student
from models.receipt import Receipt
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.pdf_service import PDFService
from views.receipt_view import ReceiptView


class TestReceiptViewRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()
        FeeController.seed_default_fee_heads()

    def tearDown(self):
        self.db.close()

    def test_01_receipt_view_instantiation_and_clear_card(self):
        """Verifies ReceiptView instantiates and clear_student_card executes without AttributeError (e.g. lbl_class)."""
        view = ReceiptView(parent=None)
        self.assertIsNotNone(view)

        # Call clear_student_card directly (the exact crash point reported)
        view.clear_student_card()
        self.assertIsNone(view.selected_student)
        self.assertEqual(view.lbl_adm_no.text(), "-")
        self.assertEqual(view.lbl_name.text(), "-")
        self.assertEqual(view.lbl_course.text(), "-")
        self.assertEqual(view.lbl_yr_sem.text(), "-")

    def test_02_update_student_card_with_various_students(self):
        """Verifies update_student_card and reset with UG, PG, and optional Class/Sec students."""
        view = ReceiptView(parent=None)

        # 1. UG Student
        st_ug = Student(
            id=99901,
            admission_no="TEST/CARD/UG01",
            name="Aniket Sharma",
            father_name="Rajesh Sharma",
            course="B. Pharmacy",
            branch="Pharmacy",
            year="2nd Year",
            semester="Semester 3",
            mobile="9876543210",
            academic_session="2025-2026",
            status="Active"
        )
        view.update_student_card(st_ug)
        self.assertEqual(view.lbl_adm_no.text(), "TEST/CARD/UG01")
        self.assertEqual(view.lbl_name.text(), "Aniket Sharma")
        self.assertIn("B. Pharmacy", view.lbl_course.text())

        view.clear_student_card()
        self.assertEqual(view.lbl_adm_no.text(), "-")

        # 2. PG Student without Class/Sec
        st_pg = Student(
            id=99902,
            admission_no="TEST/CARD/PG01",
            name="Anita Singh",
            father_name="Vikram Singh",
            course="M. Pharmacy",
            branch="Pharmaceutics",
            year="1st Year",
            semester="Semester 1",
            mobile="9123456789",
            academic_session="2025-2026",
            status="Active"
        )
        view.update_student_card(st_pg)
        self.assertEqual(view.lbl_adm_no.text(), "TEST/CARD/PG01")
        self.assertIn("M. Pharmacy", view.lbl_course.text())

        view.clear_student_card()
        self.assertEqual(view.lbl_adm_no.text(), "-")

    def test_03_generate_receipt_full_workflow(self):
        """Verifies complete Generate Receipt workflow: Student select -> Fee calculate -> Save -> Preview -> Reset."""
        import uuid
        test_adm_no = f"REC/TEST/{uuid.uuid4().hex[:6].upper()}"

        # Register test student
        st_data = {
            "admission_no": test_adm_no,
            "name": "Receipt Workflow Test Student",
            "father_name": "Father Name",
            "course": "B. Pharmacy",
            "branch": "Pharmacy",
            "year": "1st Year",
            "semester": "Semester 1",
            "class_name": "Degree College",
            "mobile": "9876543210",
            "academic_session": "2025-2026",
            "status": "Active"
        }
        create_ok, _ = StudentController.create_student(st_data)
        self.assertTrue(create_ok)

        student = StudentController.get_student_by_admission_no(test_adm_no)
        self.assertIsNotNone(student)

        view = ReceiptView(parent=None)
        view.selected_student = student
        view.update_student_card(student)

        # Select fee head
        categories = FeeController.get_applicable_categories(student)
        self.assertGreater(len(categories), 0)
        cat = categories[0]

        items = [{"fee_category_id": cat.id, "category_name": cat.name, "amount": cat.default_amount}]

        # Create receipt via ReceiptController
        rec_ok, msg, receipt = ReceiptController.create_receipt(
            student_id=student.id,
            academic_session="2025-2026",
            items=items,
            paid_amount=cat.default_amount,
            payment_mode="UPI / QR",
            utr_number="UPI998877665544",
            remarks="Automated Workflow Test"
        )
        self.assertTrue(rec_ok, f"Receipt creation failed: {msg}")
        self.assertIsNotNone(receipt)

        # Test PDF generation
        pdf_path = PDFService.generate_receipt_pdf(receipt)
        self.assertTrue(os.path.exists(pdf_path))

        # Reset receipt view after generation
        view.clear_student_card()
        self.assertIsNone(view.selected_student)


if __name__ == "__main__":
    unittest.main()
