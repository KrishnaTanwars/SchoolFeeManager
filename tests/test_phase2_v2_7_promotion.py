"""
Automated Unit and Integration Tests for Phase 2 (v2.7.0):
1. Academic Promotion Engine (PromotionService).
2. Atomic Bulk Promotion & Transactional Rollback.
3. UG (8-Semesters) vs PG (4-Semesters) Validation.
4. Hardened Duplicate Admission & Aadhaar Validation in StudentController.
5. Student Profile Fee Summary Card in StudentDetailsDialog.
"""

import os
import unittest
from datetime import date, datetime

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.student import Student
from services.promotion_service import PromotionService
from controllers.student_controller import StudentController
from dialogs.student_details_dialog import StudentDetailsDialog

class TestPhase2V27Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_calculate_next_stage_ug_and_pg(self):
        """Verifies calculation of next year and semester for UG and PG courses."""
        # UG (B. Pharmacy)
        yr, sem = PromotionService.calculate_next_stage("B. Pharmacy", "1st Year", "1 Sem")
        self.assertEqual(yr, "1st Year")
        self.assertIn(sem, ("2 Sem", "Semester 2"))

        yr, sem = PromotionService.calculate_next_stage("B. Pharmacy", "1st Year", "2 Sem")
        self.assertEqual(yr, "2nd Year")
        self.assertIn(sem, ("3 Sem", "Semester 3"))

        yr, sem = PromotionService.calculate_next_stage("B. Pharmacy", "4th Year", "7 Sem")
        self.assertEqual(yr, "4th Year")
        self.assertIn(sem, ("8 Sem", "Semester 8"))

        # PG (M. Pharmacy)
        yr, sem = PromotionService.calculate_next_stage("M. Pharmacy", "1st Year", "1 Sem")
        self.assertEqual(yr, "1st Year")
        self.assertIn(sem, ("2 Sem", "Semester 2"))

        yr, sem = PromotionService.calculate_next_stage("M. Pharmacy", "1st Year", "2 Sem")
        self.assertEqual(yr, "2nd Year")
        self.assertIn(sem, ("3 Sem", "Semester 3"))

        yr, sem = PromotionService.calculate_next_stage("M. Pharmacy", "2nd Year", "4 Sem")
        self.assertEqual(yr, "Graduated")
        self.assertEqual(sem, "Completed")

    def test_02_single_student_promotion(self):
        """Verifies promoting a single student updates session, year, and semester."""
        adm_no = "ADM/PROMO/TEST01"
        existing = self.db.query(Student).filter(Student.admission_no == adm_no).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        st = Student(
            admission_no=adm_no,
            name="Rahul Sharma",
            father_name="Sanjay Sharma",
            mobile="9800000001",
            course="B. Pharmacy",
            branch="Pharmacy",
            year="1st Year",
            semester="Semester 1",
            academic_session="2025-2026",
            status="Active"
        )
        self.db.add(st)
        self.db.commit()

        success, msg = PromotionService.promote_student(st.id, "2026-2027", "1st Year", "Semester 2")
        self.assertTrue(success, msg)

        # Refresh student record
        st_refreshed = self.db.query(Student).filter(Student.id == st.id).first()
        self.assertEqual(st_refreshed.academic_session, "2026-2027")
        self.assertEqual(st_refreshed.year, "1st Year")
        self.assertEqual(st_refreshed.semester, "Semester 2")

    def test_03_pg_invalid_promotion_prevention(self):
        """Verifies that promoting PG (M. Pharmacy) to Semester 5+ is blocked."""
        adm_no = "ADM/PROMO/PG_INVALID"
        existing = self.db.query(Student).filter(Student.admission_no == adm_no).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        st = Student(
            admission_no=adm_no,
            name="Pooja PG Student",
            father_name="Vikas PG",
            mobile="9800000002",
            course="M. Pharmacy",
            branch="Pharmaceutics",
            year="2nd Year",
            semester="Semester 4",
            academic_session="2025-2026",
            status="Active"
        )
        self.db.add(st)
        self.db.commit()

        # Attempt to promote PG to Semester 5 -> should fail
        success, msg = PromotionService.promote_student(st.id, "2026-2027", "3rd Year", "Semester 5")
        self.assertFalse(success)
        self.assertIn("M. Pharmacy (PG) is a 2-Year / 4-Semester program", msg)

    def test_04_atomic_bulk_promotion_rollback_on_error(self):
        """Verifies atomic batch promotion rollbacks if any student promotion fails."""
        s1_adm = "ADM/BULK/GOOD01"
        s2_adm = "ADM/BULK/BAD02"

        for adm in [s1_adm, s2_adm]:
            ex = self.db.query(Student).filter(Student.admission_no == adm).first()
            if ex:
                self.db.delete(ex)
        self.db.commit()

        st1 = Student(admission_no=s1_adm, name="Good UG Student", father_name="UG Father", mobile="9800000003", course="B. Pharmacy", year="1st Year", semester="Semester 1", academic_session="2025-2026")
        st2 = Student(admission_no=s2_adm, name="PG Max Student", father_name="PG Father", mobile="9800000004", course="M. Pharmacy", year="2nd Year", semester="Semester 4", academic_session="2025-2026")
        self.db.add_all([st1, st2])
        self.db.commit()

        st1_id = st1.id
        st2_id = st2.id

        # Try bulk promotion with invalid stage for st2 (Semester 6 for PG)
        success, msg = PromotionService.bulk_promote_students([st1_id, st2_id], "2026-2027", "3rd Year", "Semester 6")
        self.assertFalse(success)

        # Verify st1 was NOT updated due to atomic transaction rollback
        st1_ref = self.db.query(Student).filter(Student.id == st1_id).first()
        self.assertEqual(st1_ref.semester, "Semester 1")

    def test_05_update_student_duplicate_validation(self):
        """Verifies duplicate Admission No and Aadhaar validation on update."""
        adm1 = "ADM/DUP/ST01"
        adm2 = "ADM/DUP/ST02"
        aadh1 = "889977665511"
        aadh2 = "889977665522"

        for adm in [adm1, adm2]:
            ex = self.db.query(Student).filter(Student.admission_no == adm).first()
            if ex:
                self.db.delete(ex)
        self.db.commit()

        st1 = Student(admission_no=adm1, name="Student One", father_name="Father One", mobile="9800000005", aadhaar_number=aadh1, academic_session="2025-2026")
        st2 = Student(admission_no=adm2, name="Student Two", father_name="Father Two", mobile="9800000006", aadhaar_number=aadh2, academic_session="2025-2026")
        self.db.add_all([st1, st2])
        self.db.commit()

        # Update st2 admission_no to adm1 -> should fail
        success, msg = StudentController.update_student(st2.id, {"admission_no": adm1})
        self.assertFalse(success)
        self.assertIn("already registered", msg)

        # Update st2 aadhaar_number to aadh1 -> should fail
        success, msg = StudentController.update_student(st2.id, {"aadhaar_number": aadh1})
        self.assertFalse(success)
        self.assertIn("already registered", msg)

    def test_06_student_details_dialog_profile(self):
        """Verifies StudentDetailsDialog instantiates cleanly with profile data."""
        st = self.db.query(Student).first()
        self.assertIsNotNone(st)
        dlg = StudentDetailsDialog(parent=None, student=st)
        self.assertIsNotNone(dlg)


if __name__ == "__main__":
    unittest.main()
