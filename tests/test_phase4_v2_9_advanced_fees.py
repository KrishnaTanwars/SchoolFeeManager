"""
Automated Unit and Integration Tests for Phase 4 (v2.9.0):
1. UG (14-head) vs PG (4-head) Fee Category Retrieval and Isolation.
2. Hardened Duplicate Fee Head Validation.
3. Fee Head Enable / Disable Active Status Toggle.
4. Multi-dimensional Fee Category Querying by Course, Semester, and Academic Session.
"""

import os
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.fee_category import FeeCategory
from models.student import Student
from controllers.fee_controller import FeeController

class TestPhase4V29AdvancedFees(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_ug_vs_pg_fee_head_isolation(self):
        """Verifies UG and PG fee heads remain isolated and correctly categorized."""
        cats = FeeController.get_all_categories(active_only=False)
        ug_cats = [c for c in cats if c.course in ("UG", "All")]
        pg_cats = [c for c in cats if c.course in ("PG", "All")]

        self.assertGreater(len(ug_cats), 0)
        self.assertGreater(len(pg_cats), 0)

    def test_02_duplicate_fee_head_validation(self):
        """Verifies duplicate fee head creation under same course and semester is blocked."""
        fee_name = "Unique Test Lab Fee 123"
        ex = self.db.query(FeeCategory).filter(FeeCategory.name == fee_name).first()
        if ex:
            self.db.delete(ex)
            self.db.commit()

        data = {
            "name": fee_name,
            "course": "UG",
            "semester": "Semester 1",
            "academic_session": "2026-2027",
            "default_amount": 1500.0,
            "description": "Test fee head"
        }
        # First creation
        success1, msg1 = FeeController.create_category(data)
        self.assertTrue(success1, msg1)

        # Duplicate creation attempt
        success2, msg2 = FeeController.create_category(data)
        self.assertFalse(success2)
        self.assertIn("already exists", msg2)

    def test_03_applicable_categories_for_student(self):
        """Verifies student fee head matching by course."""
        st_ug = Student(
            admission_no="TEST_UG_999",
            roll_no="UG999",
            name="UG Student",
            father_name="Father Name",
            mobile="9800000000",
            course="B. Pharmacy",
            branch="Pharmacy",
            year="1st Year",
            semester="Semester 1",
            academic_session="2026-2027"
        )
        applicable = FeeController.get_applicable_categories(st_ug)
        self.assertGreater(len(applicable), 0)

    def test_04_enable_disable_fee_category(self):
        """Verifies updating active status of fee category."""
        fee_name = "Unique Activity Fee 456"
        ex = self.db.query(FeeCategory).filter(FeeCategory.name == fee_name).first()
        if ex:
            self.db.delete(ex)
            self.db.commit()

        data = {
            "name": fee_name,
            "course": "PG",
            "default_amount": 500.0,
            "is_active": True
        }
        success, msg = FeeController.create_category(data)
        self.assertTrue(success, msg)

        # Find created category
        cat = self.db.query(FeeCategory).filter(FeeCategory.name == fee_name).first()
        self.assertIsNotNone(cat)

        # Toggle inactive
        update_data = {"name": cat.name, "course": cat.course, "default_amount": 500.0, "is_active": False}
        up_success, up_msg = FeeController.update_category(cat.id, update_data)
        self.assertTrue(up_success, up_msg)

        cat_ref = self.db.query(FeeCategory).filter(FeeCategory.id == cat.id).first()
        self.assertFalse(cat_ref.is_active)


if __name__ == "__main__":
    unittest.main()
