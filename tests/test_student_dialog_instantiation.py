"""
Regression Test Suite for StudentDialog Instantiation, Field Completeness, Validation Rules, and Safe DB Saving.
"""

import os
import unittest
from datetime import date
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.student import Student
from controllers.student_controller import StudentController
from dialogs.student_dialog import StudentDialog
from dialogs.student_details_dialog import StudentDetailsDialog
from dialogs.student_ledger_dialog import StudentFeeLedgerDialog
from dialogs.student_import_dialog import StudentImportDialog
from dialogs.fee_category_dialog import FeeCategoryDialog
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog
from dialogs.admin_auth_dialog import AdminAuthDialog
from dialogs.user_dialog import UserDialog


class TestStudentDialogRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_student_dialog_instantiation_without_name_error(self):
        """Verifies StudentDialog instantiates for New and Edit mode without NameError (e.g. QWidget)."""
        dlg_new = StudentDialog(parent=None, student=None)
        self.assertIsNotNone(dlg_new)
        self.assertEqual(dlg_new.windowTitle(), "Register New Student")

        # Check widget presence
        self.assertTrue(hasattr(dlg_new, "txt_admission_no"))
        self.assertTrue(hasattr(dlg_new, "txt_name"))
        self.assertTrue(hasattr(dlg_new, "dt_dob"))
        self.assertTrue(hasattr(dlg_new, "txt_aadhaar"))
        self.assertTrue(hasattr(dlg_new, "txt_father_name"))
        self.assertTrue(hasattr(dlg_new, "txt_mother_name"))
        self.assertTrue(hasattr(dlg_new, "cmb_course"))
        self.assertTrue(hasattr(dlg_new, "cmb_branch"))
        self.assertTrue(hasattr(dlg_new, "cmb_year"))
        self.assertTrue(hasattr(dlg_new, "cmb_semester"))
        self.assertTrue(hasattr(dlg_new, "txt_mobile"))
        self.assertTrue(hasattr(dlg_new, "dt_admission"))
        self.assertTrue(hasattr(dlg_new, "cmb_session"))
        self.assertTrue(hasattr(dlg_new, "cmb_status"))
        self.assertTrue(hasattr(dlg_new, "txt_address"))
        self.assertTrue(hasattr(dlg_new, "lbl_photo_preview"))
        self.assertTrue(hasattr(dlg_new, "btn_choose_photo"))
        self.assertTrue(hasattr(dlg_new, "btn_remove_photo"))
        self.assertTrue(hasattr(dlg_new, "btn_save"))
        self.assertTrue(hasattr(dlg_new, "btn_cancel"))

    def test_02_all_dialog_instantiations(self):
        """Verifies all dialogs in dialogs/ directory instantiate cleanly without missing Qt imports."""
        # StudentDetailsDialog
        st = Student(
            admission_no="TEST/REG/001",
            name="Reg Student",
            father_name="Father",
            mobile="9876543210",
            academic_session="2025-2026",
            status="Active",
            date_of_birth=date(2004, 5, 15),
            aadhaar_number="123456789012"
        )
        dlg_details = StudentDetailsDialog(parent=None, student=st)
        self.assertIsNotNone(dlg_details)

        # StudentFeeLedgerDialog
        dlg_ledger = StudentFeeLedgerDialog(parent=None, student=st)
        self.assertIsNotNone(dlg_ledger)

        # StudentImportDialog
        dlg_import = StudentImportDialog(parent=None)
        self.assertIsNotNone(dlg_import)

        # FeeCategoryDialog
        dlg_fee = FeeCategoryDialog(parent=None, category=None)
        self.assertIsNotNone(dlg_fee)

        # AdminAuthDialog
        dlg_auth = AdminAuthDialog(parent=None, action_title="Test Auth")
        self.assertIsNotNone(dlg_auth)

        # UserDialog
        dlg_user = UserDialog(parent=None)
        self.assertIsNotNone(dlg_user)

    def test_03_student_creation_and_aadhaar_validation(self):
        """Verifies 12-digit numeric Aadhaar validation and duplicate prevention."""
        import uuid
        adm_no = f"REG/TEST/{uuid.uuid4().hex[:8]}"

        # Invalid Aadhaar length
        val_ok, msg = StudentController.create_student({
            "admission_no": adm_no,
            "name": "Test Student",
            "father_name": "Father",
            "course": "B. Pharmacy",
            "mobile": "9876543210",
            "academic_session": "2025-2026",
            "aadhaar_number": "12345"  # Short length
        })
        self.assertFalse(val_ok)
        self.assertIn("12 numeric digits", msg)

        # Non-numeric Aadhaar
        val_ok2, msg2 = StudentController.create_student({
            "admission_no": adm_no,
            "name": "Test Student",
            "father_name": "Father",
            "course": "B. Pharmacy",
            "mobile": "9876543210",
            "academic_session": "2025-2026",
            "aadhaar_number": "12345678901A"  # Non-numeric
        })
        self.assertFalse(val_ok2)
        self.assertIn("numeric", msg2)

        # Valid student creation with 12-digit Aadhaar & Date of Birth
        import random
        aadhaar_valid = str(random.randint(100000000000, 999999999999))
        data = {
            "admission_no": adm_no,
            "name": "Full Registration Student",
            "father_name": "Rajesh Kumar",
            "mother_name": "Sunita Kumar",
            "course": "B. Pharmacy",
            "branch": "Pharmacy",
            "year": "1st Year",
            "semester": "Semester 1",
            "class_name": "Degree College",
            "mobile": "9876512345",
            "date_of_birth": date(2003, 8, 20),
            "aadhaar_number": aadhaar_valid,
            "address": "Campus Hostels, New Delhi",
            "academic_session": "2025-2026",
            "status": "Active"
        }
        create_ok, create_msg = StudentController.create_student(data)
        self.assertTrue(create_ok, f"Creation failed: {create_msg}")

        # Duplicate Aadhaar check
        val_dup, msg_dup = StudentController.create_student({
            "admission_no": f"{adm_no}_2",
            "name": "Another Student",
            "father_name": "Father",
            "course": "B. Pharmacy",
            "mobile": "9876599999",
            "academic_session": "2025-2026",
            "aadhaar_number": aadhaar_valid  # Duplicate
        })
        self.assertFalse(val_dup)
        self.assertIn("already registered", msg_dup)

    def test_04_course_structure_validation(self):
        """Verifies UG vs PG year/semester validation rules."""
        from controllers.academic_controller import AcademicController

        # M. Pharmacy (PG) with 3rd Year -> Invalid
        ok_pg_yr, msg_pg_yr = AcademicController.validate_course_structure("M. Pharmacy", "3rd Year", "Semester 1")
        self.assertFalse(ok_pg_yr)

        # M. Pharmacy (PG) with Semester 5 -> Invalid
        ok_pg_sem, msg_pg_sem = AcademicController.validate_course_structure("M. Pharmacy", "1st Year", "Semester 5")
        self.assertFalse(ok_pg_sem)

        # B. Pharmacy (UG) with 3rd Year & Semester 5 -> Valid
        ok_ug, msg_ug = AcademicController.validate_course_structure("B. Pharmacy", "3rd Year", "Semester 5")
        self.assertTrue(ok_ug)


if __name__ == "__main__":
    unittest.main()
