"""
Phase 02 Automated Unit Testing Suite — Administrator Security & Permission System.
Tests admin password verification, failed attempt audit logs, facade APIs, and module audit persistence.
"""

import unittest
from config.database import get_db, init_db
from models.user import User
from models.audit import AuditLog
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt, ReceiptItem
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.security_service import SecurityService
import services.admin_auth as admin_auth

class TestPhase2SecuritySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()
        AuthController.login("admin", "admin123")

    def tearDown(self):
        self.db.close()

    def test_01_verify_admin_password_success_and_failure(self):
        """Verifies admin password check and failed attempt audit trail persistence."""
        # 1. Valid Admin Password
        self.assertTrue(SecurityService.verify_admin_password("admin123", module="SecurityTest"))

        # 2. Invalid Admin Password
        self.assertFalse(SecurityService.verify_admin_password("wrong_admin_pass", module="SecurityTest"))

        # 3. Empty Password
        self.assertFalse(SecurityService.verify_admin_password("", module="SecurityTest"))

        # 4. Verify Failed Attempt log in database
        audit_failed = self.db.query(AuditLog).filter(
            AuditLog.module == "SecurityTest",
            AuditLog.status == "Failed"
        ).first()
        self.assertIsNotNone(audit_failed)
        self.assertEqual(audit_failed.action, "Failed Attempt")

    def test_02_admin_auth_facade(self):
        """Verifies facade helper functions in services/admin_auth.py."""
        self.assertTrue(admin_auth.verify_admin_password("admin123", module="FacadeTest"))
        self.assertFalse(admin_auth.verify_admin_password("badpass", module="FacadeTest"))

    def test_03_student_delete_security_and_audit(self):
        """Verifies student deletion security audit logging."""
        # Create student
        succ, msg = StudentController.create_student({
            "name": "SecTest Student",
            "admission_no": "ADM/SEC/001",
            "class_name": "Class 10",
            "father_name": "Father Test",
            "mobile": "9876543210"
        })
        self.assertTrue(succ)
        st = StudentController.get_student_by_admission_no("ADM/SEC/001")
        self.assertIsNotNone(st)

        # Delete student
        del_ok, del_msg = StudentController.delete_student(st.id)
        self.assertTrue(del_ok)

        # Verify audit log
        audit = self.db.query(AuditLog).filter(
            AuditLog.module == "Student Master",
            AuditLog.action == "Student Deleted"
        ).order_by(AuditLog.id.desc()).first()
        self.assertIsNotNone(audit)
        self.assertIn("SecTest Student", audit.details)

    def test_04_fee_category_delete_security_and_audit(self):
        """Verifies fee head/category deletion security audit logging."""
        # Create fee category
        succ, msg = FeeController.create_category({
            "name": "SecTest Fee Head",
            "default_amount": 1500.0,
            "code": "STFH"
        })
        self.assertTrue(succ)
        cats = FeeController.get_all_categories()
        cat = next((c for c in cats if c.name == "SecTest Fee Head"), None)
        self.assertIsNotNone(cat)

        # Delete category
        del_ok, del_msg = FeeController.delete_category(cat.id)
        self.assertTrue(del_ok)

        # Verify audit log
        audit = self.db.query(AuditLog).filter(
            AuditLog.module == "Fee Category",
            AuditLog.action == "Fee Category Deleted"
        ).order_by(AuditLog.id.desc()).first()
        self.assertIsNotNone(audit)
        self.assertIn("SecTest Fee Head", audit.details)

    def test_05_receipt_cancel_security_and_audit(self):
        """Verifies receipt cancellation security audit logging."""
        # Create student & category
        StudentController.create_student({
            "name": "ReceiptSec Student",
            "admission_no": "ADM/REC/SEC01",
            "class_name": "Class 5",
            "father_name": "Father Sec",
            "mobile": "9876543210"
        })
        st = StudentController.get_student_by_admission_no("ADM/REC/SEC01")
        self.assertIsNotNone(st)

        FeeController.create_category({
            "name": "Tuition Fee Sec",
            "default_amount": 2500.0,
            "code": "TFS"
        })
        cats = FeeController.get_all_categories()
        cat = next((c for c in cats if c.name == "Tuition Fee Sec"), None)
        self.assertIsNotNone(cat)

        # Collect fee
        items = [{"fee_category_id": cat.id, "amount": 2500.0}]
        rec, msg = ReceiptController.collect_fee(st.id, items, payment_mode="Cash")
        self.assertIsNotNone(rec)

        # Cancel receipt
        cancel_ok, cancel_msg = ReceiptController.cancel_receipt(rec.id)
        self.assertTrue(cancel_ok)

        # Verify audit log
        audit = self.db.query(AuditLog).filter(
            AuditLog.module == "Receipt History",
            AuditLog.action == "Receipt Cancelled"
        ).order_by(AuditLog.id.desc()).first()
        self.assertIsNotNone(audit)
        self.assertIn(rec.receipt_no, audit.details)

if __name__ == "__main__":
    unittest.main()
