"""
Unit and Integration Test Suite for Phase X — Academic Structure Refactor (Semester & Year Based ERP).
Tests Course, Branch, Year, Semester Masters, Student CRUD, Fee Head Matching, Receipt Snapshots, and School Mode Compatibility.
"""

import os
import unittest
from datetime import date

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from config.database import init_db, get_db
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt
from controllers.academic_controller import AcademicController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController
from controllers.receipt_controller import ReceiptController
from services.import_service import ImportService


class TestPhaseXAcademicStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        AcademicController.seed_academic_masters_if_empty()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_academic_masters_seeding(self):
        """Verify Courses, Branches, Academic Years, and Semesters master data."""
        courses = AcademicController.get_courses()
        self.assertGreater(len(courses), 0)

        branches = AcademicController.get_branches()
        self.assertGreater(len(branches), 0)

        years = AcademicController.get_years()
        self.assertTrue(any("1st" in y for y in years))
        self.assertTrue(any("2nd" in y for y in years))

        semesters = AcademicController.get_semesters()
        self.assertTrue(any("1" in s for s in semesters))
        self.assertTrue(any("3" in s for s in semesters))

    def test_02_student_crud_with_academic_fields(self):
        """Verify Student creation and updating with Course, Branch, Year, and Semester."""
        adm_no = "TEST/ADM/SEM/999"
        
        # Cleanup if exists
        existing = self.db.query(Student).filter(Student.admission_no == adm_no).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        data = {
            "admission_no": adm_no,
            "roll_no": "999",
            "name": "Academic Test Student",
            "father_name": "Test Father",
            "mother_name": "Test Mother",
            "course": "B.Tech",
            "branch": "Computer Science",
            "year": "2nd Year",
            "semester": "Semester 3",
            "class_name": "Degree College",
            "section": "A",
            "mobile": "9999888877",
            "address": "Campus Block C",
            "academic_session": "2025-2026",
            "status": "Active"
        }

        ok, msg = StudentController.create_student(data)
        self.assertTrue(ok, f"Student creation failed: {msg}")

        student = StudentController.get_student_by_admission_no(adm_no)
        self.assertIsNotNone(student)
        self.assertEqual(student.course, "B.Tech")
        self.assertEqual(student.branch, "Computer Science")
        self.assertEqual(student.year, "2nd Year")
        self.assertEqual(student.semester, "Semester 3")

    def test_03_fee_head_applicable_matching(self):
        """Verify Fee Heads match student Course, Branch, Year, and Semester."""
        student = Student(
            admission_no="TEST/ADM/MATCH/111",
            name="Fee Match Student",
            father_name="Father",
            course="B.Tech",
            branch="Computer Science",
            year="2nd Year",
            semester="Semester 3",
            class_name="Degree College",
            mobile="9876543210",
            academic_session="2025-2026"
        )

        applicable = FeeController.get_applicable_categories(student)
        self.assertGreater(len(applicable), 0)

    def test_04_receipt_creation_academic_snapshot(self):
        """Verify generated receipt captures student's course, branch, year, semester snapshot."""
        st = StudentController.get_all_students(search_query="Academic Test Student")
        if not st:
            self.skipTest("Prerequisite student not found.")

        student = st[0]
        items = [{"fee_category_id": None, "category_name": "Tuition Fee Sem 3", "amount": 45000.0}]

        ok, msg, receipt = ReceiptController.create_receipt(
            student_id=student.id,
            academic_session=student.academic_session,
            items=items,
            payment_mode="UPI"
        )

        self.assertTrue(ok, f"Receipt creation failed: {msg}")
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.course, "B.Tech")
        self.assertEqual(receipt.branch, "Computer Science")
        self.assertEqual(receipt.academic_year, "2nd Year")
        self.assertEqual(receipt.semester, "Semester 3")

    def test_05_receipt_history_academic_filtering(self):
        """Verify Receipt History paginated query filters by Course, Branch, Year, Semester."""
        receipts, total_recs, total_pgs, summary = ReceiptController.get_receipts_paginated(
            course_filter="B.Tech",
            branch_filter="Computer Science",
            year_filter="2nd Year",
            semester_filter="Semester 3"
        )
        self.assertGreaterEqual(total_recs, 1)

    def test_06_sample_csv_generation_headers(self):
        """Verify sample CSV template includes Academic Structure headers."""
        ok, path = ImportService.generate_sample_csv()
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))

        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            self.assertIn("Course", content)
            self.assertIn("Branch", content)
            self.assertIn("Academic Year", content)
            self.assertIn("Semester", content)

    def test_07_school_mode_backward_compatibility(self):
        """Verify existing school mode students without semester continue functioning normally."""
        adm_no = "SCHOOL/2025/101"
        existing = self.db.query(Student).filter(Student.admission_no == adm_no).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        data = {
            "admission_no": adm_no,
            "roll_no": "101",
            "name": "School Student Class 10",
            "father_name": "School Father",
            "class_name": "Class 10",
            "section": "B",
            "course": "Class 10",
            "mobile": "9876500000",
            "academic_session": "2025-2026",
            "status": "Active"
        }

        ok, msg = StudentController.create_student(data)
        self.assertTrue(ok)

        st = StudentController.get_student_by_admission_no(adm_no)
        self.assertEqual(st.class_name, "Class 10")
        self.assertEqual(st.section, "B")
        self.assertTrue(st.year in (None, ""))
        self.assertTrue(st.semester in (None, ""))


if __name__ == "__main__":
    unittest.main()
