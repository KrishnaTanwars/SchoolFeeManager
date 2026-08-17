"""
Academic Promotion Service.
Handles single and bulk student academic promotion logic with full transaction safety,
course-based semester/year validation (UG 8-Semesters vs PG 4-Semesters), and audit logging.
"""

from typing import List, Dict, Any, Tuple, Optional
from config.database import get_db
from models.student import Student
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

class PromotionService:
    # Progression Maps
    UG_SEMESTER_MAP = {
        "1 Sem": ("1st Year", "2 Sem"),
        "2 Sem": ("2nd Year", "3 Sem"),
        "3 Sem": ("2nd Year", "4 Sem"),
        "4 Sem": ("3rd Year", "5 Sem"),
        "5 Sem": ("3rd Year", "6 Sem"),
        "6 Sem": ("4th Year", "7 Sem"),
        "7 Sem": ("4th Year", "8 Sem"),
        "8 Sem": ("Graduated", "Completed"),
        "Semester 1": ("1st Year", "2 Sem"),
        "Semester 2": ("2nd Year", "3 Sem"),
        "Semester 3": ("2nd Year", "4 Sem"),
        "Semester 4": ("3rd Year", "5 Sem"),
        "Semester 5": ("3rd Year", "6 Sem"),
        "Semester 6": ("4th Year", "7 Sem"),
        "Semester 7": ("4th Year", "8 Sem"),
        "Semester 8": ("Graduated", "Completed"),
    }

    PG_SEMESTER_MAP = {
        "1 Sem": ("1st Year", "2 Sem"),
        "2 Sem": ("2nd Year", "3 Sem"),
        "3 Sem": ("2nd Year", "4 Sem"),
        "4 Sem": ("Graduated", "Completed"),
        "Semester 1": ("1st Year", "2 Sem"),
        "Semester 2": ("2nd Year", "3 Sem"),
        "Semester 3": ("2nd Year", "4 Sem"),
        "Semester 4": ("Graduated", "Completed"),
    }

    @classmethod
    def calculate_next_stage(cls, course: str, current_year: str, current_sem: str) -> Tuple[str, str]:
        """
        Calculates the recommended next Year and Semester based on course (UG vs PG).
        Returns (next_year, next_semester).
        """
        course_clean = (course or "").strip().upper()
        sem_clean = (current_sem or "").strip()

        # PG Course (M. Pharmacy)
        if "M. PHARM" in course_clean or "PG" in course_clean or "MASTER" in course_clean:
            if sem_clean in cls.PG_SEMESTER_MAP:
                return cls.PG_SEMESTER_MAP[sem_clean]
            return "2nd Year", "4 Sem"

        # UG Course (B. Pharmacy)
        if sem_clean in cls.UG_SEMESTER_MAP:
            return cls.UG_SEMESTER_MAP[sem_clean]

        return "2nd Year", "3 Sem"

    @classmethod
    def validate_promotion(cls, student: Student, target_sem: str) -> Tuple[bool, str]:
        """Validates if target semester is valid for the student's course."""
        course_clean = (student.course or "").strip().upper()
        sem_clean = (target_sem or "").strip()

        is_pg = "M. PHARM" in course_clean or "PG" in course_clean or "MASTER" in course_clean

        if is_pg:
            if sem_clean in ["Semester 5", "Semester 6", "Semester 7", "Semester 8"]:
                return False, f"Invalid Promotion: M. Pharmacy (PG) is a 2-Year / 4-Semester program. Cannot promote to '{sem_clean}'."

        return True, "Valid"

    @classmethod
    def promote_student(
        cls,
        student_id: int,
        target_session: str,
        target_year: str,
        target_sem: str
    ) -> Tuple[bool, str]:
        """Promotes a single student to a new session, year, and semester."""
        res, msg = cls.bulk_promote_students([student_id], target_session, target_year, target_sem)
        return res, msg

    @classmethod
    def bulk_promote_students(
        cls,
        student_ids: List[int],
        target_session: str,
        target_year: str,
        target_sem: str
    ) -> Tuple[bool, str]:
        """
        Executes atomic bulk promotion of multiple students in a single DB transaction.
        Rolls back 100% on any failure.
        """
        if not student_ids:
            return False, "No students selected for promotion."

        if not target_session or not target_session.strip():
            return False, "Target Academic Session is required."

        db = get_db()
        try:
            students = db.query(Student).filter(Student.id.in_(student_ids)).all()
            if not students:
                return False, "No valid student records found for the selected IDs."

            # Validation Pass
            for st in students:
                valid, msg = cls.validate_promotion(st, target_sem)
                if not valid:
                    db.rollback()
                    return False, f"Promotion blocked for {st.name} ({st.admission_no}): {msg}"

            # Execution Pass
            promoted_names = []
            for st in students:
                old_info = f"{st.year} / {st.semester} ({st.academic_session})"
                st.academic_session = target_session.strip()
                st.year = target_year.strip()
                st.semester = target_sem.strip()
                if target_sem == "Completed":
                    st.status = "Graduated"
                promoted_names.append(f"{st.name} [{old_info} -> {st.year}/{st.semester}]")

            # Audit Log
            user = AuthController.get_current_user()
            audit = AuditLog(
                user_id=user.id if user else None,
                action="BULK_PROMOTION",
                details=f"Promoted {len(students)} student(s) to Session '{target_session}', Year '{target_year}', Semester '{target_sem}'. Promoted: {', '.join(promoted_names[:5])}"
            )
            db.add(audit)

            db.commit()
            logger.info(f"Successfully promoted {len(students)} student(s) to Session '{target_session}', {target_year}, {target_sem}")
            return True, f"Successfully promoted {len(students)} student(s) to Session '{target_session}', {target_year}, {target_sem}."

        except Exception as e:
            db.rollback()
            logger.error(f"Error during bulk promotion: {e}", exc_info=True)
            return False, f"Failed to promote students: {str(e)}"
        finally:
            db.close()
