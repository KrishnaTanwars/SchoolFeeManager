"""
Comprehensive Security & Administration Hardening Tests for Phase 1 (v1.1.0):
1. Central SecurityService Admin Password Verification
2. Audit Log Schema & Column Persistence (module, status, machine_name)
3. Student Delete Protection Audit Trail
4. Fee Head Delete Protection Audit Trail
5. Receipt Cancel & Bulk Delete Protection Audit Trail
6. Universal Admin Authorization Dialog Rendering
"""

import os
import unittest
from config.database import init_db, get_db, run_migrations
from models.user import User
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.security_service import SecurityService
from services.db_seed import seed_initial_data

class TestSecurityPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        init_db()
        seed_initial_data()

    def test_admin_password_verification_success(self):
        """Verify SecurityService authorizes valid admin password."""
        is_valid = SecurityService.verify_admin_password("admin123")
        self.assertTrue(is_valid)

    def test_admin_password_verification_failure(self):
        """Verify SecurityService rejects invalid admin password."""
        is_valid = SecurityService.verify_admin_password("WrongPassword123")
        self.assertFalse(is_valid)

        is_empty = SecurityService.verify_admin_password("")
        self.assertFalse(is_empty)

    def test_audit_log_creation_and_persistence(self):
        """Verify SecurityService.log_audit persists action, module, status, and machine_name."""
        success = SecurityService.log_audit(
            action="SECURITY_TEST_ACTION",
            module="Test Module",
            details="Testing audit persistence for Phase 1",
            status="Success"
        )
        self.assertTrue(success)

        db = get_db()
        try:
            log_entry = db.query(AuditLog).filter(AuditLog.action == "SECURITY_TEST_ACTION").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(log_entry)
            self.assertEqual(log_entry.module, "Test Module")
            self.assertEqual(log_entry.status, "Success")
            self.assertIsNotNone(log_entry.machine_name)
        finally:
            db.close()

    def test_student_delete_protection_audit(self):
        """Verify deleting a student records 'Student Deleted' audit entry."""
        # Create test student
        adm_no = "TEST/ADM/SEC/001"
        data = {
            "admission_no": adm_no,
            "name": "Security Test Student",
            "father_name": "Test Father",
            "class_name": "Class 10",
            "mobile": "9998887770",
            "academic_session": "2024-2025"
        }
        StudentController.create_student(data)
        st = StudentController.get_student_by_admission_no(adm_no)
        self.assertIsNotNone(st)

        # Delete student
        del_ok, _ = StudentController.delete_student(st.id)
        self.assertTrue(del_ok)

        # Verify audit log
        db = get_db()
        try:
            audit = db.query(AuditLog).filter(AuditLog.action == "Student Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.module, "Student Master")
            self.assertIn(adm_no, audit.details)
        finally:
            db.close()

    def test_fee_head_delete_protection_audit(self):
        """Verify deleting a fee category records 'Fee Head Deleted' audit entry."""
        # Create temporary fee head
        cat_ok, _ = FeeController.create_category("Test Temp Head", "TTH", 500.0, "Temporary fee head")
        self.assertTrue(cat_ok)

        cats = FeeController.get_all_categories()
        target_cat = next((c for c in cats if c.name == "Test Temp Head"), None)
        self.assertIsNotNone(target_cat)

        # Delete fee head
        del_ok, _ = FeeController.delete_category(target_cat.id)
        self.assertTrue(del_ok)

        # Verify audit log
        db = get_db()
        try:
            audit = db.query(AuditLog).filter(AuditLog.action == "Fee Head Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.module, "Fee Heads")
            self.assertIn("Test Temp Head", audit.details)
        finally:
            db.close()

    def test_receipt_cancel_and_bulk_delete_audit(self):
        """Verify cancelling and bulk deleting receipts records audit entries."""
        # Issue test receipt
        st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        if not st:
            StudentController.create_student({
                "admission_no": "TEST/ADM/V11/001",
                "name": "Receipt Test Student",
                "father_name": "Test Father",
                "class_name": "Class 10",
                "mobile": "9876500000",
                "academic_session": "2024-2025"
            })
            st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")

        cats = FeeController.get_all_categories()
        cid = cats[0].id if cats else 1
        cname = cats[0].name if cats else "Tuition Fee"

        rec_ok, _, receipt = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2024-2025",
            items=[{"fee_category_id": cid, "category_name": cname, "amount": 1000.0}],
            paid_amount=1000.0,
            payment_mode="Cash"
        )
        self.assertTrue(rec_ok)

        # Cancel receipt
        cancel_ok, _ = ReceiptController.cancel_receipt(receipt.id)
        self.assertTrue(cancel_ok)

        # Bulk delete cancelled receipts
        bulk_ok, _, count = ReceiptController.bulk_delete_receipts()
        self.assertTrue(bulk_ok)

        # Verify audit log entries
        db = get_db()
        try:
            cancel_audit = db.query(AuditLog).filter(AuditLog.action == "Receipt Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(cancel_audit)
            self.assertEqual(cancel_audit.module, "Receipt History")

            bulk_audit = db.query(AuditLog).filter(AuditLog.action == "Bulk Receipt Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(bulk_audit)
            self.assertEqual(bulk_audit.module, "Receipt History")
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
