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
from models.receipt import FeeReceipt, ReceiptItem
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
        st, msg = StudentController.create_student(
            name="SecTest Student",
            admission_no="ADM/SEC/001",
            class_name="Class 10"
        )
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
        cat, msg = FeeController.create_category(
            name="SecTest Fee Head",
            default_amount=1500.0,
            code="STFH"
        )
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
        st, _ = StudentController.create_student("ReceiptSec Student", "ADM/REC/SEC01", "Class 5")
        cat, _ = FeeController.create_category("Tuition Fee Sec", 2500.0, "TFS")

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
