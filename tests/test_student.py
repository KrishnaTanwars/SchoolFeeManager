"""
Unit Tests for Student CRUD Operations and Validation.
"""

import unittest
from datetime import date
from config.database import init_db
from controllers.student_controller import StudentController

class TestStudentController(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_create_and_delete_student(self):
        test_adm = "TEST/ADM/9999"
        data = {
            "admission_no": test_adm,
            "roll_no": "99",
            "name": "Test Student",
            "father_name": "Test Father",
            "mother_name": "Test Mother",
            "class_name": "Class 10",
            "section": "A",
            "mobile": "9876543210",
            "address": "Test Address",
            "admission_date": date.today(),
            "academic_session": "2024-2025",
            "status": "Active"
        }

        # Create
        success, msg = StudentController.create_student(data)
        self.assertTrue(success, f"Failed: {msg}")

        # Fetch
        st = StudentController.get_student_by_admission_no(test_adm)
        self.assertIsNotNone(st)
        self.assertEqual(st.name, "Test Student")

        # Duplicate check
        dup_success, dup_msg = StudentController.create_student(data)
        self.assertFalse(dup_success)

        # Delete
        del_success, del_msg = StudentController.delete_student(st.id)
        self.assertTrue(del_success)

    def test_student_search_and_filter(self):
        adm_no = "TEST/ADM/SECNET/888"
        data = {
            "admission_no": adm_no,
            "roll_no": "88",
            "name": "Phase3 Filter Student",
            "father_name": "Father P3",
            "mother_name": "Mother P3",
            "class_name": "Class 12",
            "section": "C",
            "course": "Science Stream",
            "mobile": "9123456789",
            "academic_session": "2024-2025",
            "status": "Active"
        }
        succ, _ = StudentController.create_student(data)
        self.assertTrue(succ)

        # Search by Mother Name
        results = StudentController.get_all_students(search_query="Mother P3")
        self.assertTrue(any(s.admission_no == adm_no for s in results))

        # Search by Course
        results_course = StudentController.get_all_students(search_query="Science Stream")
        self.assertTrue(any(s.admission_no == adm_no for s in results_course))

        # Section Filter
        sec_results = StudentController.get_all_students(section_filter="C")
        self.assertTrue(any(s.admission_no == adm_no for s in sec_results))

        # Distinct Sections test
        sections = StudentController.get_distinct_sections()
        self.assertIn("C", sections)

        # Clean up
        st = StudentController.get_student_by_admission_no(adm_no)
        if st:
            StudentController.delete_student(st.id)

if __name__ == "__main__":
    unittest.main()
