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

if __name__ == "__main__":
    unittest.main()
