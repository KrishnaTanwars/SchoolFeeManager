"""
Student CRUD and Filter Controller with Session Expunge Safety.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_, func
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
        section_filter: str = "All",
        session_filter: str = "All",
        status_filter: str = "Active",
        course_filter: str = "All",
        branch_filter: str = "All",
        year_filter: str = "All",
        semester_filter: str = "All"
    ) -> List[Student]:
        db = get_db()
        try:
            query = db.query(Student)
            
            if status_filter and status_filter != "All":
                query = query.filter(Student.status == status_filter)

            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)

            if section_filter and section_filter != "All":
                query = query.filter(Student.section == section_filter)

            if session_filter and session_filter != "All":
                query = query.filter(Student.academic_session == session_filter)

            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)

            if branch_filter and branch_filter != "All":
                query = query.filter(Student.branch == branch_filter)

            if year_filter and year_filter != "All":
                query = query.filter(Student.year == year_filter)

            if semester_filter and semester_filter != "All":
                query = query.filter(Student.semester == semester_filter)

            if search_query:
                pattern = f"%{search_query.strip()}%"
                query = query.filter(
                    or_(
                        Student.name.ilike(pattern),
                        Student.admission_no.ilike(pattern),
                        Student.roll_no.ilike(pattern),
                        Student.father_name.ilike(pattern),
                        Student.mother_name.ilike(pattern),
                        Student.mobile.ilike(pattern),
                        Student.class_name.ilike(pattern),
                        Student.course.ilike(pattern),
                        Student.branch.ilike(pattern),
                        Student.year.ilike(pattern),
                        Student.semester.ilike(pattern),
                        Student.section.ilike(pattern)
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

            from services.session_service import session_manager
            student = Student(
                admission_no=admission_no,
                roll_no=data.get("roll_no", "").strip(),
                name=data.get("name", "").strip(),
                father_name=data.get("father_name", "").strip(),
                mother_name=data.get("mother_name", "").strip(),
                class_name=data.get("class_name", "").strip() or data.get("course", "").strip(),
                section=data.get("section", "").strip(),
                course=data.get("course", "").strip(),
                branch=data.get("branch", "").strip(),
                year=data.get("year", "").strip(),
                semester=data.get("semester", "").strip(),
                mobile=data.get("mobile", "").strip(),
                address=data.get("address", "").strip(),
                admission_date=data.get("admission_date"),
                academic_session=data.get("academic_session", "").strip() or session_manager.get_active_session(),
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
            student.class_name = data.get("class_name", "").strip() or data.get("course", "").strip()
            student.section = data.get("section", "").strip()
            student.course = data.get("course", "").strip()
            student.branch = data.get("branch", "").strip()
            student.year = data.get("year", "").strip()
            student.semester = data.get("semester", "").strip()
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
            adm_no = student.admission_no
            db.delete(student)
            db.commit()

            # Central Audit Log
            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Student Deleted",
                module="Student Master",
                details=f"Deleted student: '{student_name}' ({adm_no}, ID {student_id})",
                status="Success"
            )

            logger.info(f"Deleted student ID {student_id}")
            return True, f"Student '{student_name}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting student {student_id}: {e}", exc_info=True)
            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Student Delete Failed",
                module="Student Master",
                details=f"Failed to delete student ID {student_id}: {str(e)}",
                status="Failed"
            )
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

    @staticmethod
    def get_student_counts_by_class() -> List[Dict[str, Any]]:
        """Returns student count breakdown by Class."""
        db = get_db()
        try:
            results = db.query(
                Student.class_name,
                func.count(Student.id)
            ).filter(Student.status == "Active")\
             .group_by(Student.class_name).all()

            return [
                {"class_name": r[0] or "Unassigned", "student_count": r[1] or 0}
                for r in results
            ]
        finally:
            db.close()

    @staticmethod
    def get_student_counts_by_course() -> List[Dict[str, Any]]:
        """Returns student count breakdown by Course (future compatible)."""
        db = get_db()
        try:
            # Uses course if populated, falls back to class_name
            course_col = func.coalesce(Student.course, Student.class_name)
            results = db.query(
                course_col,
                func.count(Student.id)
            ).filter(Student.status == "Active")\
             .group_by(course_col).all()

            return [
                {"course_name": r[0] or "General", "student_count": r[1] or 0}
                for r in results
            ]
        finally:
            db.close()

    @staticmethod
    def import_students_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Imports students from CSV file.
        Validates columns, skips duplicates (by admission_no), and returns import summary.
        """
        import csv
        from datetime import datetime, date

        summary = {
            "success_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "failed_rows": [],
            "total_processed": 0
        }

        db = get_db()
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if not headers:
                    return {"error": "CSV file is empty."}

                from services.session_service import session_manager
                hdr_map = {}
                for idx, h in enumerate(headers):
                    clean_h = h.strip().lower().replace(" ", "_").replace("'", "")
                    hdr_map[clean_h] = idx

                # Map variations
                adm_idx = hdr_map.get("admission_number", hdr_map.get("admission_no", hdr_map.get("adm_no", 0)))
                roll_idx = hdr_map.get("roll_number", hdr_map.get("roll_no", 1))
                name_idx = hdr_map.get("student_name", hdr_map.get("name", 2))
                cls_idx = hdr_map.get("class", hdr_map.get("class_name", 3))
                sec_idx = hdr_map.get("section", 4)
                father_idx = hdr_map.get("father_name", hdr_map.get("father", 5))
                mother_idx = hdr_map.get("mother_name", hdr_map.get("mother", 6))
                mob_idx = hdr_map.get("mobile_number", hdr_map.get("mobile", 7))
                addr_idx = hdr_map.get("address", 8)
                date_idx = hdr_map.get("date_of_admission", hdr_map.get("admission_date", 9))
                sess_idx = hdr_map.get("session", hdr_map.get("academic_session", 10))
                status_idx = hdr_map.get("status", 11)

                for row_num, row in enumerate(reader, start=2):
                    if not row or not any(field.strip() for field in row):
                        continue

                    summary["total_processed"] += 1

                    try:
                        adm_no = row[adm_idx].strip() if adm_idx < len(row) else ""
                        name = row[name_idx].strip() if name_idx < len(row) else ""

                        if not adm_no or not name:
                            summary["failed_count"] += 1
                            summary["failed_rows"].append(f"Row {row_num}: Missing Admission Number or Student Name.")
                            continue

                        # Duplicate check
                        existing = db.query(Student).filter(Student.admission_no == adm_no).first()
                        if existing:
                            summary["skipped_count"] += 1
                            continue

                        roll = row[roll_idx].strip() if roll_idx < len(row) else ""
                        cls_name = row[cls_idx].strip() if cls_idx < len(row) else "Class 1"
                        section = row[sec_idx].strip() if sec_idx < len(row) else "A"
                        father = row[father_idx].strip() if father_idx < len(row) else ""
                        mother = row[mother_idx].strip() if mother_idx < len(row) else ""
                        mobile = row[mob_idx].strip() if mob_idx < len(row) else ""
                        address = row[addr_idx].strip() if addr_idx < len(row) else ""
                        date_str = row[date_idx].strip() if date_idx < len(row) else ""
                        session_val = row[sess_idx].strip() if sess_idx < len(row) else "2024-2025"
                        status_val = row[status_idx].strip() if status_idx < len(row) else "Active"

                        adm_date = date.today()
                        if date_str:
                            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                                try:
                                    adm_date = datetime.strptime(date_str, fmt).date()
                                    break
                                except ValueError:
                                    pass

                        st = Student(
                            admission_no=adm_no,
                            roll_no=roll,
                            name=name,
                            father_name=father,
                            mother_name=mother,
                            class_name=cls_name or "Class 1",
                            section=section or "A",
                            mobile=mobile or "0000000000",
                            address=address,
                            admission_date=adm_date,
                            academic_session=session_val or session_manager.get_active_session(),
                            status=status_val if status_val in ("Active", "Inactive") else "Active"
                        )
                        db.add(st)
                        summary["success_count"] += 1
                    except Exception as row_err:
                        summary["failed_count"] += 1
                        summary["failed_rows"].append(f"Row {row_num}: {str(row_err)}")

                db.commit()
                logger.info(f"Imported CSV: {summary['success_count']} added, {summary['skipped_count']} skipped, {summary['failed_count']} failed.")
                return summary
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to import students CSV: {e}", exc_info=True)
            return {"error": f"Failed to import CSV: {str(e)}"}
        finally:
            db.close()

    @staticmethod
    def get_distinct_classes() -> List[str]:
        """Returns sorted list of distinct class names."""
        db = get_db()
        try:
            results = db.query(Student.class_name).distinct().all()
            return sorted([r[0] for r in results if r[0]])
        finally:
            db.close()

    @staticmethod
    def get_distinct_sections() -> List[str]:
        """Returns sorted list of distinct section names."""
        db = get_db()
        try:
            results = db.query(Student.section).distinct().all()
            return sorted([r[0] for r in results if r[0]])
        finally:
            db.close()

    @staticmethod
    def get_distinct_sessions() -> List[str]:
        """Returns sorted list of distinct academic sessions."""
        db = get_db()
        try:
            results = db.query(Student.academic_session).distinct().all()
            return sorted([r[0] for r in results if r[0]])
        finally:
            db.close()
