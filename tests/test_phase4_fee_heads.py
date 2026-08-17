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
        self.db = get_db()
        FeeController.seed_default_fee_heads()

    def tearDown(self):
        self.db.close()

    def test_01_default_seed_fee_heads(self):
        """Verifies seeding of 14 UG and 3 PG default fee heads."""
        ug_heads = self.db.query(FeeCategory).filter(FeeCategory.course == "UG").all()
        pg_heads = self.db.query(FeeCategory).filter(FeeCategory.course == "PG").all()

        self.assertGreaterEqual(len(ug_heads), 14)
        self.assertGreaterEqual(len(pg_heads), 3)

        ug_names = [h.name.upper() for h in ug_heads]
        self.assertIn("ADMISSION FORM FEE", ug_names)
        self.assertIn("UG TUTION FEE", ug_names)
        self.assertIn("OTHER FINE", ug_names)

        pg_names = [h.name.upper() for h in pg_heads]
        self.assertIn("PG TUTION FEE", pg_names)
        self.assertIn("PG LABORATORY USAGES", pg_names)

    def test_02_create_ug_pg_fee_heads(self):
        """Verifies creating UG and PG fee heads without short code."""
        succ_ug, msg_ug = FeeController.create_category({
            "name": "UG Custom Special Library Fee",
            "course": "UG",
            "default_amount": 750.0,
            "description": "Library expansion charge"
        })
        self.assertTrue(succ_ug or "already exists" in msg_ug)

        succ_pg, msg_pg = FeeController.create_category({
            "name": "PG Custom Special Research Fee",
            "course": "PG",
            "default_amount": 3500.0,
            "description": "Postgraduate research support"
        })
        self.assertTrue(succ_pg or "already exists" in msg_pg)

    def test_03_duplicate_validation_within_course(self):
        """Verifies duplicate prevention within same course, while allowing same name across UG and PG."""
        cat_name = "Unique Custom Shared Fee Test"

        # Create UG Tuition Custom
        FeeController.create_category({
            "name": cat_name,
            "course": "UG",
            "default_amount": 1000.0
        })

        # Creating duplicate under UG should fail
        dup_succ, dup_msg = FeeController.create_category({
            "name": cat_name,
            "course": "UG",
            "default_amount": 1200.0
        })
        self.assertFalse(dup_succ)
        self.assertIn("already exists", dup_msg)

        # Creating under PG should succeed (or already exists if run again)
        pg_succ, pg_msg = FeeController.create_category({
            "name": cat_name,
            "course": "PG",
            "default_amount": 2000.0
        })
        self.assertTrue(pg_succ or "already exists" in pg_msg)

    def test_04_course_filtering(self):
        """Verifies get_all_categories with course filtering and search query."""
        all_cats = FeeController.get_all_categories()
        ug_only = FeeController.get_all_categories(course_filter="UG")
        pg_only = FeeController.get_all_categories(course_filter="PG")

        self.assertTrue(all(c.course == "UG" for c in ug_only))
        self.assertTrue(all(c.course == "PG" for c in pg_only))

        search_res = FeeController.get_all_categories(search_query="LAB")
        self.assertTrue(any("LAB" in c.name.upper() for c in search_res))

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

    def test_06_bulk_delete_fee_heads(self):
        """Verifies bulk deletion of multiple fee heads in one operation."""
        FeeController.create_category({"name": "Bulk Fee Head 1", "course": "UG", "default_amount": 100.0})
        FeeController.create_category({"name": "Bulk Fee Head 2", "course": "UG", "default_amount": 200.0})

        c1 = FeeController.get_all_categories(search_query="Bulk Fee Head 1")
        c2 = FeeController.get_all_categories(search_query="Bulk Fee Head 2")

        self.assertEqual(len(c1), 1)
        self.assertEqual(len(c2), 1)

        ids = [c1[0].id, c2[0].id]
        succ, msg, del_cnt = FeeController.delete_categories_bulk(ids)
        self.assertTrue(succ)
        self.assertEqual(del_cnt, 2)

if __name__ == "__main__":
    unittest.main()
