"""
Comprehensive Automated Regression Tests for Student Search (Name, Adm No, Mobile, Duplicate Names, Case-Insensitive, Reset).
"""

import os
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.student import Student
from controllers.student_controller import StudentController
from views.receipt_view import ReceiptView


class TestStudentSearchRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        db = get_db()
        try:
            # Seed 4 duplicate-named students: Ananya Sharma, Ananya Joshi, Ananya Gupta, Ananya Singh
            ananyas = [
                ("ADM/SRCH/001", "Ananya Sharma", "Rajesh Sharma", "9876500001"),
                ("ADM/SRCH/002", "Ananya Joshi", "Suresh Joshi", "9876500002"),
                ("ADM/SRCH/003", "Ananya Gupta", "Mahesh Gupta", "9876500003"),
                ("ADM/SRCH/004", "Ananya Singh", "Vikram Singh", "9876500004"),
            ]
            for adm, name, father, mob in ananyas:
                existing = db.query(Student).filter(Student.admission_no == adm).first()
                if not existing:
                    st = Student(
                        admission_no=adm,
                        name=name,
                        father_name=father,
                        course="B. Pharmacy",
                        branch="Pharmacy",
                        year="1st Year",
                        semester="Semester 1",
                        mobile=mob,
                        academic_session="2025-2026",
                        status="Active"
                    )
                    db.add(st)
            db.commit()
        finally:
            db.close()

    def test_01_exact_name_search(self):
        """Verifies exact student name search returns matching records."""
        res = StudentController.get_all_students(search_query="Ananya Sharma", status_filter="Active")
        self.assertGreaterEqual(len(res), 1)
        self.assertTrue(any(s.admission_no == "ADM/SRCH/001" for s in res))

    def test_02_partial_name_search(self):
        """Verifies partial name search (ana, anya) returns matching records."""
        res_ana = StudentController.get_all_students(search_query="ana", status_filter="Active")
        self.assertGreaterEqual(len(res_ana), 4)

        res_anya = StudentController.get_all_students(search_query="anya", status_filter="Active")
        self.assertGreaterEqual(len(res_anya), 4)

    def test_03_case_insensitive_search(self):
        """Verifies case-insensitive search (ANANYA, ananya, AnAnYa)."""
        res_upper = StudentController.get_all_students(search_query="ANANYA", status_filter="Active")
        res_lower = StudentController.get_all_students(search_query="ananya", status_filter="Active")
        self.assertEqual(len(res_upper), len(res_lower))
        self.assertGreaterEqual(len(res_upper), 4)

    def test_04_multiple_students_with_same_first_name(self):
        """Verifies 4 students named Ananya are all returned in dropdown list for distinguishing."""
        view = ReceiptView(parent=None)
        view.txt_student_search.setText("Ananya")
        # Trigger text change explicitly
        view.on_search_text_changed("Ananya")

        # Verify popup suggestion widget has at least 4 items
        self.assertGreaterEqual(view.popup_suggestions.count(), 4)

        # Verify items have distinct admission numbers and names
        found_adms = []
        for i in range(view.popup_suggestions.count()):
            item = view.popup_suggestions.item(i)
            st = item.data(Qt.UserRole)
            if st:
                found_adms.append(st.admission_no)

        self.assertIn("ADM/SRCH/001", found_adms)
        self.assertIn("ADM/SRCH/002", found_adms)
        self.assertIn("ADM/SRCH/003", found_adms)
        self.assertIn("ADM/SRCH/004", found_adms)

    def test_05_admission_number_search(self):
        """Verifies searching by admission / enrollment number."""
        res = StudentController.get_all_students(search_query="ADM/SRCH/003", status_filter="Active")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, "Ananya Gupta")

    def test_06_mobile_number_search(self):
        """Verifies searching by student mobile number."""
        res = StudentController.get_all_students(search_query="9876500004", status_filter="Active")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, "Ananya Singh")

    def test_07_empty_search(self):
        """Verifies empty search query hides popup suggestions and does not select student."""
        view = ReceiptView(parent=None)
        view.on_search_text_changed("")
        self.assertTrue(view.popup_suggestions.isHidden())

    def test_08_search_result_clearing(self):
        """Verifies clear_student_card resets search text and student card UI."""
        view = ReceiptView(parent=None)
        st = StudentController.get_student_by_admission_no("ADM/SRCH/001")
        view.update_student_card(st)
        self.assertEqual(view.lbl_adm_no.text(), "ADM/SRCH/001")

        view.clear_student_card()
        self.assertIsNone(view.selected_student)
        self.assertEqual(view.lbl_adm_no.text(), "-")
        self.assertEqual(view.txt_student_search.text(), "")

    def test_09_search_result_selection(self):
        """Verifies selecting item from popup updates student card correctly."""
        view = ReceiptView(parent=None)
        st = StudentController.get_student_by_admission_no("ADM/SRCH/002")

        from PySide6.QtWidgets import QListWidgetItem
        item = QListWidgetItem()
        item.setData(Qt.UserRole, st)

        view.select_student_from_item(item)
        self.assertEqual(view.selected_student.admission_no, "ADM/SRCH/002")
        self.assertEqual(view.lbl_name.text(), "Ananya Joshi")

    def test_10_reselect_different_student(self):
        """Verifies re-selecting a different student updates student card completely without leftover data."""
        view = ReceiptView(parent=None)
        st1 = StudentController.get_student_by_admission_no("ADM/SRCH/001")
        st2 = StudentController.get_student_by_admission_no("ADM/SRCH/003")

        view.update_student_card(st1)
        self.assertEqual(view.lbl_name.text(), "Ananya Sharma")

        view.update_student_card(st2)
        self.assertEqual(view.lbl_name.text(), "Ananya Gupta")
        self.assertEqual(view.lbl_adm_no.text(), "ADM/SRCH/003")


if __name__ == "__main__":
    unittest.main()
