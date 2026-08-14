"""
Comprehensive Phase 01 Runtime Validation Test Suite for EduLedger ERP (v1.1.0).
Performs end-to-end runtime verification of all Phase 1 security features, UI dialogs,
controllers, services, and regression workflows.
"""

import os
import sys
import unittest
from datetime import date
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication(sys.argv)

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
from controllers.report_controller import ReportController
from controllers.settings_controller import SettingsController

from services.security_service import SecurityService
from services.pdf_service import PDFService
from services.backup_service import BackupService
from services.export_service import ExportService
from services.db_seed import seed_initial_data

from dialogs.admin_auth_dialog import AdminAuthDialog

class TestRuntimeValidationPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_initial_data()

    def test_step3_login_verification(self):
        """STEP 3: Test Admin & Operator login, wrong password rejection, empty password."""
        # 1. Admin login success
        self.assertTrue(AuthController.login("admin", "admin123"))
        curr = AuthController.get_current_user()
        self.assertIsNotNone(curr)
        self.assertEqual(curr.username, "admin")
        self.assertTrue(AuthController.is_admin())
        AuthController.logout()

        # 2. Operator login success
        self.assertTrue(AuthController.login("operator", "operator123"))
        curr = AuthController.get_current_user()
        self.assertIsNotNone(curr)
        self.assertEqual(curr.username, "operator")
        self.assertFalse(AuthController.is_admin())
        AuthController.logout()

        # 3. Wrong password rejection
        self.assertFalse(AuthController.login("admin", "WrongPass123!"))

        # 4. Empty password rejection
        self.assertFalse(AuthController.login("admin", ""))

    def test_step4_security_admin_auth_dialog(self):
        """STEP 4: Test AdminAuthDialog password validation and verification logic."""
        # Test SecurityService password verification directly
        self.assertTrue(SecurityService.verify_admin_password("admin123"))
        self.assertFalse(SecurityService.verify_admin_password("WrongAdminPass"))
        self.assertFalse(SecurityService.verify_admin_password(""))

        # Test AdminAuthDialog widget instantiation and authorize method
        dlg = AdminAuthDialog(action_title="Test Authorization", action_context="Validation Test")
        dlg.txt_password.setText("WrongPassword")
        dlg.authorize()
        self.assertIn("Incorrect administrator password", dlg.lbl_error.text())

        dlg.txt_password.setText("admin123")
        dlg.authorize()
        self.assertEqual(dlg.result(), AdminAuthDialog.Accepted)

    def test_step4_delete_protection_student(self):
        """STEP 4: Test Student Delete Protection & Audit Trail."""
        adm_no = "RUN/ADM/001"
        StudentController.create_student({
            "admission_no": adm_no,
            "name": "Runtime Student",
            "father_name": "Father Name",
            "class_name": "Class 10",
            "mobile": "9123456789",
            "academic_session": "2024-2025"
        })
        st = StudentController.get_student_by_admission_no(adm_no)
        self.assertIsNotNone(st)

        # Delete student
        succ, msg = StudentController.delete_student(st.id)
        self.assertTrue(succ)

        # Verify audit log
        db = get_db()
        try:
            audit = db.query(AuditLog).filter(AuditLog.action == "Student Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.module, "Student Master")
            self.assertEqual(audit.status, "Success")
            self.assertIsNotNone(audit.machine_name)
        finally:
            db.close()

    def test_step4_delete_protection_fee_head(self):
        """STEP 4: Test Fee Head Delete Protection & Audit Trail."""
        cat_name = "Runtime Head Fee"
        FeeController.create_category(cat_name, "RHF", 750.0, "Test fee head")
        cats = FeeController.get_all_categories()
        target = next((c for c in cats if c.name == cat_name), None)
        self.assertIsNotNone(target)

        succ, msg = FeeController.delete_category(target.id)
        self.assertTrue(succ)

        db = get_db()
        try:
            audit = db.query(AuditLog).filter(AuditLog.action == "Fee Head Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.module, "Fee Heads")
        finally:
            db.close()

    def test_step4_delete_protection_receipt_and_bulk(self):
        """STEP 4: Test Receipt Cancel & Bulk Delete Protection & Audit Trail."""
        st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")
        if not st:
            StudentController.create_student({
                "admission_no": "TEST/ADM/V11/001",
                "name": "Receipt Runtime Student",
                "father_name": "Father Name",
                "class_name": "Class 10",
                "mobile": "9876500000",
                "academic_session": "2024-2025"
            })
            st = StudentController.get_student_by_admission_no("TEST/ADM/V11/001")

        cats = FeeController.get_all_categories()
        fee_cat_id = cats[0].id if cats else 1
        cat_name = cats[0].name if cats else "Tuition Fee"

        rec_ok, _, receipt = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2024-2025",
            items=[{"fee_category_id": fee_cat_id, "category_name": cat_name, "amount": 1500.0}],
            paid_amount=1500.0,
            payment_mode="Cash"
        )
        self.assertTrue(rec_ok)

        # Cancel receipt
        c_ok, _ = ReceiptController.cancel_receipt(receipt.id)
        self.assertTrue(c_ok)

        # Bulk delete
        b_ok, _, cnt = ReceiptController.bulk_delete_receipts()
        self.assertTrue(b_ok)

        db = get_db()
        try:
            audit_rec = db.query(AuditLog).filter(AuditLog.action == "Receipt Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit_rec)
            self.assertEqual(audit_rec.module, "Receipt History")

            audit_bulk = db.query(AuditLog).filter(AuditLog.action == "Bulk Receipt Deleted").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit_bulk)
            self.assertEqual(audit_bulk.module, "Receipt History")
        finally:
            db.close()

    def test_step5_settings_verification(self):
        """STEP 5: Test Settings protection and audit log recording."""
        succ, msg = SettingsController.update_school_info({
            "school_name": "DPS Modern School Baseline",
            "address": "123 Knowledge Park, New Delhi",
            "phone": "+91 98765 43210",
            "email": "info@school.edu.in"
        })
        self.assertTrue(succ)

        db = get_db()
        try:
            audit = db.query(AuditLog).filter(AuditLog.action == "Settings Updated").order_by(AuditLog.id.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.module, "Settings")
        finally:
            db.close()

    def test_step7_regression_testing(self):
        """STEP 7: Test existing core ERP modules (Dashboard, PDF, Backup, Reports, Export)."""
        # 1. Dashboard metrics
        cnt = ReportController.get_total_students_count()
        self.assertGreaterEqual(cnt, 0)
        today_col = ReportController.get_today_collection()
        self.assertGreaterEqual(today_col, 0.0)

        # 2. ReportLab PDF Generation
        receipts = ReceiptController.get_all_receipts()
        if receipts:
            pdf_path = PDFService.generate_receipt_pdf(receipts[0])
            self.assertTrue(os.path.exists(pdf_path))

        # 3. Backup & Restore Service
        bk_ok, msg, bk_file = BackupService.create_backup()
        self.assertTrue(bk_ok)
        self.assertTrue(os.path.exists(os.path.join("backup", bk_file)))

        # 4. CSV Export
        headers = ["Col1", "Col2"]
        rows = [["Val1", "Val2"]]
        out_csv = "runtime_test.csv"
        exp_ok, actual_path = ExportService.export_to_csv(headers, rows, out_csv)
        self.assertTrue(exp_ok)
        self.assertTrue(os.path.exists(actual_path))

if __name__ == "__main__":
    unittest.main()
