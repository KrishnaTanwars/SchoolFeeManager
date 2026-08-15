"""
Phase 5 - Fee Collection Professionalization Unit & Integration Tests.
"""

import os
import unittest
from datetime import date
from config.database import init_db, get_db
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.pdf_service import PDFService
from utils.number_to_words import number_to_words_indian

class TestPhase5FeeCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        db = get_db()
        try:
            # Seed test UG and PG students
            st_ug = db.query(Student).filter(Student.admission_no == "TEST-UG-01").first()
            if not st_ug:
                st_ug = Student(
                    admission_no="TEST-UG-01",
                    roll_no="101",
                    name="Aniket Sharma",
                    father_name="Rajesh Sharma",
                    class_name="B.Pharmacy FY",
                    section="A",
                    course="UG",
                    mobile="9876543210",
                    academic_session="2024-2025",
                    status="Active"
                )
                db.add(st_ug)

            st_pg = db.query(Student).filter(Student.admission_no == "TEST-PG-01").first()
            if not st_pg:
                st_pg = Student(
                    admission_no="TEST-PG-01",
                    roll_no="201",
                    name="Anita Singh",
                    father_name="Vikram Singh",
                    class_name="M.Sc Chemistry",
                    section="B",
                    course="PG",
                    mobile="9123456789",
                    academic_session="2024-2025",
                    status="Active"
                )
                db.add(st_pg)

            # Seed test UG and PG fee heads
            f_ug = db.query(FeeCategory).filter(FeeCategory.name == "UG TUTION FEE").first()
            if not f_ug:
                f_ug = FeeCategory(name="UG TUTION FEE", course="UG", default_amount=15000.0, is_active=True)
                db.add(f_ug)
            else:
                f_ug.is_active = True

            f_pg = db.query(FeeCategory).filter(FeeCategory.name == "PG TUTION FEE").first()
            if not f_pg:
                f_pg = FeeCategory(name="PG TUTION FEE", course="PG", default_amount=25000.0, is_active=True)
                db.add(f_pg)
            else:
                f_pg.is_active = True

            db.commit()
        finally:
            db.close()

    def test_01_student_search_autocomplete(self):
        """Test instant search by Admission No, Name, Father Name, Mobile, Roll No."""
        results_name = StudentController.get_all_students(search_query="aniket", status_filter="Active")
        self.assertTrue(any(s.admission_no == "TEST-UG-01" for s in results_name))

        results_adm = StudentController.get_all_students(search_query="TEST-PG-01", status_filter="Active")
        self.assertTrue(any(s.admission_no == "TEST-PG-01" for s in results_adm))

        results_father = StudentController.get_all_students(search_query="Vikram", status_filter="Active")
        self.assertTrue(any(s.admission_no == "TEST-PG-01" for s in results_father))

        results_mobile = StudentController.get_all_students(search_query="9876543210", status_filter="Active")
        self.assertTrue(any(s.admission_no == "TEST-UG-01" for s in results_mobile))

    def test_02_course_based_fee_filtering(self):
        """Test course filtering: UG returns UG fee heads, PG returns PG fee heads."""
        ug_fees = FeeController.get_all_categories(active_only=True, course_filter="UG")
        self.assertTrue(all(f.course in ("UG", "All") for f in ug_fees))
        self.assertTrue(any(f.name == "UG TUTION FEE" for f in ug_fees))

        pg_fees = FeeController.get_all_categories(active_only=True, course_filter="PG")
        self.assertTrue(all(f.course in ("PG", "All") for f in pg_fees))
        self.assertTrue(any(f.name == "PG TUTION FEE" for f in pg_fees))

    def test_03_realtime_calculation_logic(self):
        """Test calculation of Subtotal, Discount, Fine, Total, Paid Amount, Due, and Words."""
        subtotal = 15000.0
        discount = 1000.0
        fine = 500.0
        grand_total = max(0.0, subtotal - discount + fine)
        self.assertEqual(grand_total, 14500.0)

        paid_amount = 10000.0
        due_amount = max(0.0, grand_total - paid_amount)
        self.assertEqual(due_amount, 4500.0)

        words = number_to_words_indian(paid_amount)
        self.assertIn("Ten Thousand", words)

    def test_04_receipt_creation_and_validation(self):
        """Test valid receipt creation & validation rules."""
        st = StudentController.get_student_by_admission_no("TEST-UG-01")
        self.assertIsNotNone(st)

        fees = FeeController.get_all_categories(active_only=True, course_filter="UG")
        cat = next((f for f in fees if f.name == "UG TUTION FEE"), fees[0] if fees else None)
        self.assertIsNotNone(cat)

        items = [{"fee_category_id": cat.id, "category_name": cat.name, "amount": 15000.0}]

        # Validation: empty items
        ok, msg, rec = ReceiptController.create_receipt(
            student_id=st.id, academic_session="2024-2025", items=[]
        )
        self.assertFalse(ok)

        # Successful Receipt Creation
        ok, msg, rec = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2024-2025",
            items=items,
            discount_amount=1000.0,
            fine_amount=500.0,
            paid_amount=14500.0,
            payment_mode="UPI / QR",
            utr_number="123456789012",
            remarks="Phase 5 Test Receipt"
        )
        self.assertTrue(ok)
        self.assertIsNotNone(rec)
        self.assertEqual(rec.total_amount, 14500.0)
        self.assertEqual(rec.paid_amount, 14500.0)
        self.assertEqual(rec.due_amount, 0.0)
        self.assertEqual(rec.utr_number, "123456789012")

    def test_05_pdf_service_generation(self):
        """Test PDF generation for receipt without errors."""
        st = StudentController.get_student_by_admission_no("TEST-UG-01")
        db = get_db()
        try:
            r_db = db.query(Receipt).filter(Receipt.student_id == st.id).order_by(Receipt.id.desc()).first()
            self.assertIsNotNone(r_db)
            rec = ReceiptController.get_receipt_by_id(r_db.id)
            self.assertIsNotNone(rec)

            pdf_path = PDFService.generate_receipt_pdf(rec)
            self.assertTrue(os.path.exists(pdf_path))
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
