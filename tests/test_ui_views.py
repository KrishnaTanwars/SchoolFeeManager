"""
Automated Headless End-to-End Test Suite for PySide6 Views & Workflows.
Runs in offscreen mode to verify every screen, dialog, PDF generation, backup, and controller.
"""

import unittest
import sys
import os
import uuid
from datetime import date
from PySide6.QtWidgets import QApplication

# Set offscreen QPA platform for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

app = QApplication.instance() or QApplication(sys.argv)

from config.database import init_db, get_db
from services.db_seed import seed_initial_data
from views.main_window import MainWindow
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.student_view import StudentView
from views.fee_category_view import FeeCategoryView
from views.receipt_view import ReceiptView
from views.receipt_history_view import ReceiptHistoryView
from views.report_view import ReportView
from views.settings_view import SettingsView

from dialogs.student_dialog import StudentDialog
from dialogs.fee_category_dialog import FeeCategoryDialog
from dialogs.user_dialog import UserDialog

from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from controllers.report_controller import ReportController
from services.pdf_service import PDFService
from services.backup_service import BackupService

class TestFullApplicationWorkflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_initial_data()

    def test_01_authentication_flow(self):
        # Admin Login
        self.assertTrue(AuthController.login("admin", "admin123"))
        self.assertTrue(AuthController.is_admin())
        self.assertIsNotNone(AuthController.get_current_user())

        # Logout
        AuthController.logout()
        self.assertIsNone(AuthController.get_current_user())

        # Operator Login
        self.assertTrue(AuthController.login("operator", "operator123"))
        self.assertFalse(AuthController.is_admin())
        AuthController.logout()

        # Re-login Admin
        AuthController.login("admin", "admin123")

    def test_02_student_lifecycle(self):
        # Create Student with unique admission number
        adm_no = f"ADM/TEST/{uuid.uuid4().hex[:6].upper()}"
        student_data = {
            "admission_no": adm_no,
            "roll_no": "101",
            "name": "Arjun Sharma",
            "father_name": "Rajesh Sharma",
            "mother_name": "Sunita Sharma",
            "class_name": "Class 10",
            "section": "A",
            "mobile": "9876543210",
            "address": "123 Connaught Place, New Delhi",
            "admission_date": date.today(),
            "academic_session": "2024-2025",
            "status": "Active"
        }

        success, msg = StudentController.create_student(student_data)
        self.assertTrue(success, f"Create student failed: {msg}")

        # Fetch
        student = StudentController.get_student_by_admission_no(adm_no)
        self.assertIsNotNone(student)
        self.assertEqual(student.name, "Arjun Sharma")

        # Duplicate check
        dup_success, _ = StudentController.create_student(student_data)
        self.assertFalse(dup_success)

        # Update
        student_data["name"] = "Arjun Kumar Sharma"
        up_success, _ = StudentController.update_student(student.id, student_data)
        self.assertTrue(up_success)

    def test_03_fee_collection_and_pdf_generation(self):
        # Create test student first
        adm_no = f"ADM/REC/{uuid.uuid4().hex[:6].upper()}"
        student_data = {
            "admission_no": adm_no,
            "roll_no": "102",
            "name": "Priya Singh",
            "father_name": "Vikram Singh",
            "class_name": "Class 12",
            "mobile": "9812345678",
            "academic_session": "2024-2025"
        }
        StudentController.create_student(student_data)
        student = StudentController.get_student_by_admission_no(adm_no)
        self.assertIsNotNone(student)

        cats = FeeController.get_all_categories()
        cid1 = cats[0].id if len(cats) > 0 else 1
        cname1 = cats[0].name if len(cats) > 0 else "Tuition Fee"
        cid2 = cats[1].id if len(cats) > 1 else cid1
        cname2 = cats[1].name if len(cats) > 1 else cname1

        # Create Receipt
        fee_items = [
            {"fee_category_id": cid1, "category_name": cname1, "amount": 2500.0},
            {"fee_category_id": cid2, "category_name": cname2, "amount": 500.0}
        ]

        success, msg, receipt = ReceiptController.create_receipt(
            student_id=student.id,
            academic_session="2024-2025",
            items=fee_items,
            discount_amount=100.0,
            fine_amount=50.0,
            payment_mode="Cash",
            remarks="Term 1 Fee"
        )

        self.assertTrue(success, f"Create receipt failed: {msg}")
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.total_amount, 2950.0)
        self.assertIn("Two Thousand Nine Hundred Fifty Rupees", receipt.amount_in_words)

        # PDF Generation
        pdf_path = PDFService.generate_receipt_pdf(receipt)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(pdf_path.endswith(".pdf"))

    def test_04_backup_and_restore_cycle(self):
        # Create Backup
        success, msg, backup_path = BackupService.create_backup()
        self.assertTrue(success, f"Backup creation failed: {msg}")
        self.assertTrue(os.path.exists(backup_path))

        # Restore Backup
        restore_success, restore_msg = BackupService.restore_backup(backup_path)
        self.assertTrue(restore_success, f"Restore failed: {restore_msg}")

    def test_05_main_window_and_views_instantiation(self):
        # Instantiate Main Window & Navigations
        window = MainWindow()
        self.assertIsNotNone(window)

        # Navigate every view
        for view_key in ["dashboard", "receipt", "history", "students", "fees", "reports", "settings"]:
            window.navigate_to(view_key)
            self.assertEqual(window.stacked_widget.currentWidget(), window.views[view_key])

        # Test Dialogs Instantiation
        st_dlg = StudentDialog(None)
        self.assertIsNotNone(st_dlg)

        cat_dlg = FeeCategoryDialog(None)
        self.assertIsNotNone(cat_dlg)

        user_dlg = UserDialog(None)
        self.assertIsNotNone(user_dlg)

if __name__ == "__main__":
    unittest.main()
