"""
Phase 4 — Fee Heads Master Professionalization Unit Tests.
Tests UG & PG Fee Head CRUD, Short Code removal, duplicate validation within course,
course filtering, and default fee head seeding.
"""

import unittest
from config.database import init_db, get_db, DB_PATH
from models.fee_category import FeeCategory
from models.student import Student
from controllers.fee_controller import FeeController
from controllers.student_controller import StudentController

class TestPhase4FeeHeadsMaster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        FeeController.seed_default_fee_heads()
        self.db = get_db()

    def tearDown(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def test_01_default_seed_fee_heads(self):
        """Verifies seeding of 14 UG and 3 PG default fee heads."""
        ug_heads = self.db.query(FeeCategory).filter(FeeCategory.course == "UG").all()
        pg_heads = self.db.query(FeeCategory).filter(FeeCategory.course == "PG").all()

        self.assertGreaterEqual(len(ug_heads), 14)
        self.assertGreaterEqual(len(pg_heads), 3)

        ug_names = [h.name for h in ug_heads]
        self.assertIn("Admission Form Fee", ug_names)
        self.assertIn("UG Tuition Fee", ug_names)
        self.assertIn("Other Fine", ug_names)

        pg_names = [h.name for h in pg_heads]
        self.assertIn("PG Tuition Fee", pg_names)
        self.assertIn("PG Laboratory Usage Fee", pg_names)

    def test_02_create_ug_pg_fee_heads(self):
        """Verifies creating UG and PG fee heads without short code."""
        # Cleanup if left over from prior test run
        for c in FeeController.get_all_categories():
            if c.name in ["UG Special Library Fee", "PG Special Research Fee"]:
                FeeController.delete_category(c.id)

        succ_ug, msg_ug = FeeController.create_category({
            "name": "UG Special Library Fee",
            "course": "UG",
            "default_amount": 750.0,
            "description": "Library expansion charge"
        })
        self.assertTrue(succ_ug)

        succ_pg, msg_pg = FeeController.create_category({
            "name": "PG Special Research Fee",
            "course": "PG",
            "default_amount": 3500.0,
            "description": "Postgraduate research support"
        })
        self.assertTrue(succ_pg)

    def test_03_duplicate_validation_within_course(self):
        """Verifies duplicate prevention within same course, while allowing same name across UG and PG."""
        # Cleanup if left over from prior test run
        for cid in [c.id for c in FeeController.get_all_categories() if c.name == "Unique Custom Shared Fee"]:
            FeeController.delete_category(cid)

        # Create UG Tuition Custom
        FeeController.create_category({
            "name": "Unique Custom Shared Fee",
            "course": "UG",
            "default_amount": 1000.0
        })

        # Creating duplicate under UG should fail
        dup_succ, dup_msg = FeeController.create_category({
            "name": "Unique Custom Shared Fee",
            "course": "UG",
            "default_amount": 1200.0
        })
        self.assertFalse(dup_succ)
        self.assertIn("already exists", dup_msg)

        # Creating under PG should succeed
        pg_succ, pg_msg = FeeController.create_category({
            "name": "Unique Custom Shared Fee",
            "course": "PG",
            "default_amount": 2000.0
        })
        self.assertTrue(pg_succ)

    def test_04_course_filtering(self):
        """Verifies get_all_categories with course filtering and search query."""
        all_cats = FeeController.get_all_categories()
        ug_only = FeeController.get_all_categories(course_filter="UG")
        pg_only = FeeController.get_all_categories(course_filter="PG")

        self.assertTrue(all(c.course == "UG" for c in ug_only))
        self.assertTrue(all(c.course == "PG" for c in pg_only))

        search_res = FeeController.get_all_categories(search_query="Laboratory")
        self.assertTrue(any("Laboratory" in c.name for c in search_res))

    def test_05_update_and_delete_fee_head(self):
        """Verifies updating and deleting fee head."""
        succ, msg = FeeController.create_category({
            "name": "Temp Test Fee",
            "course": "UG",
            "default_amount": 500.0
        })
        self.assertTrue(succ)

        cats = FeeController.get_all_categories(search_query="Temp Test Fee")
        self.assertEqual(len(cats), 1)
        temp_id = cats[0].id

        # Update
        upd_succ, upd_msg = FeeController.update_category(temp_id, {
            "name": "Updated Temp Test Fee",
            "course": "PG",
            "default_amount": 600.0,
            "is_active": True
        })
        self.assertTrue(upd_succ)

        # Delete
        del_succ, del_msg = FeeController.delete_category(temp_id)
        self.assertTrue(del_succ)

if __name__ == "__main__":
    unittest.main()
