"""
Comprehensive Unit & Integration Tests for Version 1.1 Features:
1. Partial Fee Collection & Due Amount Tracking
2. Dynamic Payment Details Database Persistence
3. CSV Student Import & Sample Template Generation
4. Student Analytics (by Class & Course)
5. Safe Database Schema Migration
6. PDF Receipt Generation
"""

import os
import unittest
from datetime import date, datetime
from config.database import init_db, get_db, run_migrations
from models.student import Student
from models.receipt import Receipt
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.export_service import ExportService
from services.pdf_service import PDFService
from services.db_seed import seed_initial_data

class TestVersion11Features(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_initial_data()

    def test_database_migration(self):
        """Verify schema migration runs without errors and columns exist."""
        run_migrations()
        db = get_db()
        try:
            r = db.query(Receipt).first()
            if r:
                self.assertTrue(hasattr(r, 'paid_amount'))
                self.assertTrue(hasattr(r, 'due_amount'))
                self.assertTrue(hasattr(r, 'utr_number'))
                self.assertTrue(hasattr(r, 'cheque_number'))
                self.assertTrue(hasattr(r, 'cheque_date'))
                self.assertTrue(hasattr(r, 'bank_name'))
                self.assertTrue(hasattr(r, 'payment_date'))
        finally:
            db.close()

    def test_partial_fee_collection_and_due(self):
        """Test creating a receipt with partial payment and due tracking."""
        # 1. Register student if not exists
        st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        if not st:
            data = {
                "admission_no": "TEST/ADM/V11/001",
                "roll_no": "501",
                "name": "Partial Fee Test Student",
                "father_name": "Test Father",
                "class_name": "Class 10",
                "section": "A",
                "mobile": "9876500000",
                "academic_session": "2024-2025"
            }
            StudentController.create_student(data)
            st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")

        self.assertIsNotNone(st)

        cats = FeeController.get_all_categories()
        cid1 = cats[0].id if len(cats) > 0 else 1
        cname1 = cats[0].name if len(cats) > 0 else "Tuition Fee"
        cid2 = cats[1].id if len(cats) > 1 else cid1
        cname2 = cats[1].name if len(cats) > 1 else cname1

        # 2. Issue receipt with Total = 12500, Paid = 10000, Due = 2500
        items = [{"fee_category_id": cid1, "category_name": cname1, "amount": 12500.0}]
        rec_success, msg, receipt = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2024-2025",
            items=items,
            paid_amount=10000.0,
            payment_mode="UPI / QR",
            utr_number="UPI123456789",
            bank_name="HDFC Bank",
            payment_date=date.today()
        )
        self.assertTrue(rec_success)
        self.assertEqual(receipt.total_amount, 12500.0)
        self.assertEqual(receipt.paid_amount, 10000.0)
        self.assertEqual(receipt.due_amount, 2500.0)
        self.assertEqual(receipt.utr_number, "UPI123456789")
        self.assertEqual(receipt.bank_name, "HDFC Bank")

        # 3. Check cumulative student outstanding due
        cum_due = ReceiptController.get_student_outstanding_due(st.id)
        self.assertGreaterEqual(cum_due, 2500.0)

    def test_cheque_payment_persistence(self):
        """Test Cheque payment details persistence in database."""
        st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        if not st:
            data = {
                "admission_no": "TEST/ADM/V11/001",
                "roll_no": "501",
                "name": "Partial Fee Test Student",
                "father_name": "Test Father",
                "class_name": "Class 10",
                "section": "A",
                "mobile": "9876500000",
                "academic_session": "2024-2025"
            }
            StudentController.create_student(data)
            st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        self.assertIsNotNone(st)

        cats = FeeController.get_all_categories()
        cid = cats[0].id if cats else 1
        cname = cats[0].name if cats else "Development Fee"

        items = [{"fee_category_id": cid, "category_name": cname, "amount": 2000.0}]
        cq_dt = date(2026, 7, 20)
        rec_success, _, receipt = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2024-2025",
            items=items,
            paid_amount=2000.0,
            payment_mode="Cheque",
            cheque_number="CHQ987654",
            cheque_date=cq_dt,
            bank_name="State Bank of India (SBI)"
        )
        self.assertTrue(rec_success)
        self.assertEqual(receipt.cheque_number, "CHQ987654")
        self.assertEqual(receipt.cheque_date, cq_dt)
        self.assertEqual(receipt.bank_name, "State Bank of India (SBI)")

    def test_csv_import_and_sample_template(self):
        """Test sample CSV template generation and CSV student import workflow."""
        # 1. Download Sample CSV
        sample_path = "e:/Downloads/FREELANCING/exports/test_sample_import.csv"
        os.makedirs("e:/Downloads/FREELANCING/exports", exist_ok=True)
        gen_ok, out_path = ExportService.generate_sample_student_csv(output_path=sample_path)
        self.assertTrue(gen_ok)
        self.assertTrue(os.path.exists(out_path))

        # 2. Import Students from CSV
        result = StudentController.import_students_from_csv(out_path)
        self.assertNotIn("error", result)
        self.assertGreaterEqual(result["total_processed"], 1)

    def test_student_analytics(self):
        """Test student counts by class and course breakdown queries."""
        class_stats = StudentController.get_student_counts_by_class()
        self.assertIsInstance(class_stats, list)

        course_stats = StudentController.get_student_counts_by_course()
        self.assertIsInstance(course_stats, list)

    def test_pdf_receipt_generation(self):
        """Test ReportLab PDF generation with payment details block."""
        st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        receipts = ReceiptController.get_all_receipts()
        if receipts:
            rec = receipts[0]
            pdf_path = PDFService.generate_receipt_pdf(rec)
            self.assertTrue(os.path.exists(pdf_path))

if __name__ == "__main__":
    unittest.main()
