"""
Student CRUD and Filter Controller with Session Expunge Safety.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_
from config.database import get_db
from models.student import Student
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

class StudentController:
    @staticmethod
    def get_all_students(
        search_query: str = "",
        class_filter: str = "All",
        session_filter: str = "All",
        status_filter: str = "Active"
    ) -> List[Student]:
        db = get_db()
        try:
            query = db.query(Student)
            
            if status_filter and status_filter != "All":
                query = query.filter(Student.status == status_filter)

            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)

            if session_filter and session_filter != "All":
                query = query.filter(Student.academic_session == session_filter)

            if search_query:
                pattern = f"%{search_query.strip()}%"
                query = query.filter(
                    or_(
                        Student.name.ilike(pattern),
                        Student.admission_no.ilike(pattern),
                        Student.roll_no.ilike(pattern),
                        Student.father_name.ilike(pattern),
                        Student.mobile.ilike(pattern),
                        Student.class_name.ilike(pattern)
                    )
                )

            students = query.order_by(Student.name.asc()).all()
            for s in students:
                db.expunge(s)
            return students
        finally:
            db.close()

    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Student]:
        db = get_db()
        try:
            st = db.query(Student).filter(Student.id == student_id).first()
            if st:
                db.expunge(st)
            return st
        finally:
            db.close()

    @staticmethod
    def get_student_by_admission_no(admission_no: str) -> Optional[Student]:
        db = get_db()
        try:
            st = db.query(Student).filter(Student.admission_no == admission_no.strip()).first()
            if st:
                db.expunge(st)
            return st
        finally:
            db.close()

    @staticmethod
    def create_student(data: Dict[str, Any]) -> tuple[bool, str]:
        """Creates student. Returns (success: bool, message: str)."""
        db = get_db()
        try:
            admission_no = data.get("admission_no", "").strip()
            if not admission_no:
                return False, "Admission Number is required."

            # Check duplicate admission_no
            existing = db.query(Student).filter(Student.admission_no == admission_no).first()
            if existing:
                return False, f"Admission Number '{admission_no}' is already registered."

            student = Student(
                admission_no=admission_no,
                roll_no=data.get("roll_no", "").strip(),
                name=data.get("name", "").strip(),
                father_name=data.get("father_name", "").strip(),
                mother_name=data.get("mother_name", "").strip(),
                class_name=data.get("class_name", "").strip(),
                section=data.get("section", "").strip(),
                mobile=data.get("mobile", "").strip(),
                address=data.get("address", "").strip(),
                admission_date=data.get("admission_date"),
                academic_session=data.get("academic_session", "2024-2025"),
                status="Active"
            )
            db.add(student)

            # Audit Log
            user = AuthController.get_current_user()
            audit = AuditLog(
                user_id=user.id if user else None,
                action="CREATE",
                details=f"Registered new student '{student.name}' ({student.admission_no})"
            )
            db.add(audit)

            db.commit()
            logger.info(f"Created student: {student.name} ({student.admission_no})")
            return True, f"Student '{student.name}' registered successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating student: {e}", exc_info=True)
            return False, f"Failed to register student: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def update_student(student_id: int, data: Dict[str, Any]) -> tuple[bool, str]:
        """Updates student. Returns (success: bool, message: str)."""
        db = get_db()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Student record not found."

            student.roll_no = data.get("roll_no", "").strip()
            student.name = data.get("name", "").strip()
            student.father_name = data.get("father_name", "").strip()
            student.mother_name = data.get("mother_name", "").strip()
            student.class_name = data.get("class_name", "").strip()
            student.section = data.get("section", "").strip()
            student.mobile = data.get("mobile", "").strip()
            student.address = data.get("address", "").strip()
            student.admission_date = data.get("admission_date")
            student.academic_session = data.get("academic_session", student.academic_session)
            student.status = data.get("status", student.status)

            # Audit Log
            user = AuthController.get_current_user()
            audit = AuditLog(
                user_id=user.id if user else None,
                action="UPDATE",
                details=f"Updated student '{student.name}' ({student.admission_no})"
            )
            db.add(audit)

            db.commit()
            logger.info(f"Updated student ID {student_id}: {student.name}")
            return True, f"Student '{student.name}' updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating student {student_id}: {e}", exc_info=True)
            return False, f"Failed to update student: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def delete_student(student_id: int) -> tuple[bool, str]:
        """Deletes student record. Returns (success: bool, message: str)."""
        db = get_db()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Student record not found."

            student_name = student.name
            db.delete(student)

            # Audit Log
            user = AuthController.get_current_user()
            audit = AuditLog(
                user_id=user.id if user else None,
                action="DELETE",
                details=f"Deleted student ID {student_id} ({student_name})"
            )
            db.add(audit)

            db.commit()
            logger.info(f"Deleted student ID {student_id}")
            return True, f"Student '{student_name}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting student {student_id}: {e}", exc_info=True)
            return False, f"Cannot delete student with associated receipt history. {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_distinct_classes() -> List[str]:
        db = get_db()
        try:
            results = db.query(Student.class_name).distinct().all()
            classes = sorted(list({r[0] for r in results if r[0]}))
            return classes
        finally:
            db.close()

    @staticmethod
    def get_distinct_sessions() -> List[str]:
        db = get_db()
        try:
            results = db.query(Student.academic_session).distinct().all()
            sessions = sorted(list({r[0] for r in results if r[0]}))
            return sessions
        finally:
            db.close()
