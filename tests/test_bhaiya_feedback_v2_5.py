"""
Automated Test Suite for All New Client Testing Feedback (v2.5 Development Cycle).
"""

import unittest
from datetime import date
from config.database import init_db, get_db
from models.student import Student
from models.fee_category import FeeCategory
from controllers.student_controller import StudentController
from controllers.academic_controller import AcademicController
from controllers.fee_controller import FeeController
from services.export_service import ExportService


class TestBhaiyaFeedbackV25(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        FeeController.seed_default_fee_heads()

    def test_01_add_student_with_and_without_photo(self):
        """Part 1 & 26: Add student registration flow with optional photo upload."""
        adm_no_1 = "TEST/ADM/V25/001"
        adm_no_2 = "TEST/ADM/V25/002"

        # Cleanup existing test data
        s1 = StudentController.get_student_by_admission_no(adm_no_1)
        if s1:
            StudentController.delete_student(s1.id)
        s2 = StudentController.get_student_by_admission_no(adm_no_2)
        if s2:
            StudentController.delete_student(s2.id)

        # 1. Student WITH Photo (UG B.Pharm)
        data1 = {
            "admission_no": adm_no_1,
            "roll_no": "101",
            "name": "Rahul Sharma (UG)",
            "father_name": "Ramesh Sharma",
            "mother_name": "Sunita Sharma",
            "date_of_birth": date(2003, 5, 14),
            "course_category": "UG",
            "course": "Bachelor of Pharmacy",
            "branch": "Pharmacy",
            "year": "1st",
            "semester": "1st Sem",
            "mobile": "9876543210",
            "aadhaar_number": "123456789012",
            "address": "New Delhi",
            "admission_date": date.today(),
            "academic_session": "2026-2027",
            "status": "Active",
            "photo_path": "photo_test_ug_101.jpg"
        }
        success1, msg1 = StudentController.create_student(data1)
        self.assertTrue(success1, f"UG Add Student failed: {msg1}")

        # 2. Student WITHOUT Photo (PG M.Pharm)
        data2 = {
            "admission_no": adm_no_2,
            "roll_no": "102",
            "name": "Priya Verma (PG)",
            "father_name": "Suresh Verma",
            "mother_name": "Kavita Verma",
            "date_of_birth": date(2001, 8, 22),
            "course_category": "PG",
            "course": "Master of Pharmacy",
            "branch": "Pharmacy",
            "year": "1st",
            "semester": "1st Sem",
            "mobile": "9123456789",
            "aadhaar_number": "987654321098",
            "address": "Mumbai",
            "admission_date": date.today(),
            "academic_session": "2026-2027",
            "status": "Active",
            "photo_path": None
        }
        success2, msg2 = StudentController.create_student(data2)
        self.assertTrue(success2, f"PG Add Student failed: {msg2}")

        # Verification from DB
        st1 = StudentController.get_student_by_admission_no(adm_no_1)
        self.assertIsNotNone(st1)
        self.assertEqual(st1.course_category, "UG")
        self.assertEqual(st1.course, "Bachelor of Pharmacy")
        self.assertEqual(st1.photo_path, "photo_test_ug_101.jpg")

        st2 = StudentController.get_student_by_admission_no(adm_no_2)
        self.assertIsNotNone(st2)
        self.assertEqual(st2.course_category, "PG")
        self.assertEqual(st2.course, "Master of Pharmacy")
        self.assertIsNone(st2.photo_path)

    def test_02_student_export_photo_column(self):
        """Part 2: Verify Student export contains 'Student Photo' column reference."""
        headers = ["Admission / Enrollment No", "Student Name", "Student Photo", "Date of Birth", "Class / Course"]
        students = StudentController.get_all_students(status_filter="All")
        rows = [
            [
                s.admission_no,
                s.name,
                getattr(s, "photo_path", None) or "",
                str(s.date_of_birth or ""),
                s.course or ""
            ]
            for s in students
        ]

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        success, msg = ExportService.export_to_csv(headers, rows, output_path=tmp_path)
        self.assertTrue(success)

        import csv
        with open(tmp_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header_row = next(reader)
            self.assertIn("Student Photo", header_row)

    def test_03_course_category_and_semester_dependencies(self):
        """Part 4-8: Verify UG/PG course hierarchy, semester constraints, and year mapping."""
        ug_courses = AcademicController.get_courses_by_category("UG")
        self.assertIn("Bachelor of Pharmacy", ug_courses)
        self.assertNotIn("Master of Pharmacy", ug_courses)

        pg_courses = AcademicController.get_courses_by_category("PG")
        self.assertIn("Master of Pharmacy", pg_courses)
        self.assertNotIn("Bachelor of Pharmacy", pg_courses)

        # B.Pharm Years (1st..4th) and Semesters (1st..8th)
        bpharm_years = AcademicController.get_years(course_name="Bachelor of Pharmacy")
        self.assertEqual(len(bpharm_years), 4)
        bpharm_sems = AcademicController.get_semesters(course_name="Bachelor of Pharmacy")
        self.assertEqual(len(bpharm_sems), 8)

        # M.Pharm Years (1st..2nd) and Semesters (1st..4th)
        mpharm_years = AcademicController.get_years(course_name="Master of Pharmacy")
        self.assertEqual(len(mpharm_years), 2)
        mpharm_sems = AcademicController.get_semesters(course_name="Master of Pharmacy")
        self.assertEqual(len(mpharm_sems), 4)

    def test_04_fee_head_ug_pg_isolation(self):
        """Part 11 & 12: Verify UG student receives ONLY UG fee heads and PG student receives ONLY PG fee heads."""
        ug_student = StudentController.get_student_by_admission_no("TEST/ADM/V25/001")
        pg_student = StudentController.get_student_by_admission_no("TEST/ADM/V25/002")

        self.assertIsNotNone(ug_student)
        self.assertIsNotNone(pg_student)

        ug_cats = FeeController.get_applicable_categories(ug_student)
        pg_cats = FeeController.get_applicable_categories(pg_student)

        # Verify UG fee heads contain UG heads and NO PG heads
        ug_cat_names = [c.name for c in ug_cats]
        ug_cat_courses = [c.course for c in ug_cats]
        self.assertIn("UG Tuition Fee", ug_cat_names)
        self.assertNotIn("PG Tuition Fee", ug_cat_names)

        # Verify PG fee heads contain PG heads and NO UG heads
        pg_cat_names = [c.name for c in pg_cats]
        self.assertIn("PG Tuition Fee", pg_cat_names)
        self.assertNotIn("UG Tuition Fee", pg_cat_names)

    def test_05_bulk_student_deletion(self):
        """Part 17-21 & 25: Verify bulk student deletion works permanently in database."""
        adm_1 = "TEST/ADM/BULK/001"
        adm_2 = "TEST/ADM/BULK/002"

        StudentController.create_student({
            "admission_no": adm_1, "name": "Bulk Test 1", "father_name": "Father B1",
            "course_category": "UG", "course": "Bachelor of Pharmacy", "mobile": "9998887771", "status": "Active"
        })
        StudentController.create_student({
            "admission_no": adm_2, "name": "Bulk Test 2", "father_name": "Father B2",
            "course_category": "PG", "course": "Master of Pharmacy", "mobile": "9998887772", "status": "Active"
        })

        st1 = StudentController.get_student_by_admission_no(adm_1)
        st2 = StudentController.get_student_by_admission_no(adm_2)
        self.assertIsNotNone(st1)
        self.assertIsNotNone(st2)

        # Perform Bulk Delete
        success, msg, deleted_count = StudentController.delete_students_bulk([st1.id, st2.id])
        self.assertTrue(success, f"Bulk delete failed: {msg}")
        self.assertEqual(deleted_count, 2)

        # Confirm permanent deletion
        self.assertIsNone(StudentController.get_student_by_admission_no(adm_1))
        self.assertIsNone(StudentController.get_student_by_admission_no(adm_2))


if __name__ == "__main__":
    unittest.main()
