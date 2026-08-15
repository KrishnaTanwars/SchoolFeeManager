"""
FeeCategory Controller for managing unlimited Fee Heads with session expunge safety.
"""

from typing import List, Optional, Tuple, Dict, Any
from config.database import get_db
from models.fee_category import FeeCategory
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

class FeeController:
    @staticmethod
    def get_all_categories(
        active_only: bool = False,
        course_filter: str = "All",
        search_query: str = ""
    ) -> List[FeeCategory]:
        db = get_db()
        try:
            query = db.query(FeeCategory)
            if active_only:
                query = query.filter(FeeCategory.is_active == True)

            if course_filter and course_filter != "All":
                query = query.filter(FeeCategory.course == course_filter)

            if search_query:
                pattern = f"%{search_query.strip()}%"
                query = query.filter(
                    (FeeCategory.name.ilike(pattern)) |
                    (FeeCategory.course.ilike(pattern)) |
                    (FeeCategory.description.ilike(pattern))
                )

            cats = query.order_by(FeeCategory.course.asc(), FeeCategory.name.asc()).all()
            for c in cats:
                db.expunge(c)
            return cats
        finally:
            db.close()

    @staticmethod
    def get_applicable_categories(student: Any) -> List[FeeCategory]:
        """
        Returns active Fee Heads applicable to the given student based on:
        Course, Branch, Academic Year, Semester, and Academic Session.
        Falls back to all active fee heads if student parameters are unassigned.
        """
        db = get_db()
        try:
            query = db.query(FeeCategory).filter(FeeCategory.is_active == True)
            cats = query.all()

            matched = []
            st_course = getattr(student, "course", None) or "All"
            st_branch = getattr(student, "branch", None) or "All"
            st_year = getattr(student, "year", None) or "All"
            st_sem = getattr(student, "semester", None) or "All"
            st_session = getattr(student, "academic_session", None) or "All"

            for c in cats:
                # Check course match
                if c.course not in ("All", "UG", "PG") and st_course != "All" and c.course.lower() != st_course.lower():
                    continue
                # Check branch match
                if c.branch != "All" and st_branch != "All" and c.branch.lower() != st_branch.lower():
                    continue
                # Check year match
                if c.academic_year != "All" and st_year != "All" and c.academic_year.lower() != st_year.lower():
                    continue
                # Check semester match
                if c.semester != "All" and st_sem != "All" and c.semester.lower() != st_sem.lower():
                    continue
                # Check session match
                if c.academic_session != "All" and st_session != "All" and c.academic_session.lower() != st_session.lower():
                    continue
                matched.append(c)

            for c in matched:
                db.expunge(c)
            return matched if matched else cats
        finally:
            db.close()

    @staticmethod
    def create_category(data: Any, *args, **kwargs) -> Tuple[bool, str]:
        """
        Creates fee category. Supports dict or legacy positional args.
        data dict keys: name, course, branch, academic_year, semester, academic_session, default_amount, description, is_active
        """
        db = get_db()
        try:
            if isinstance(data, dict):
                name = data.get("name", "").strip()
                course = data.get("course", "All").strip()
                branch = data.get("branch", "All").strip()
                academic_year = data.get("academic_year", "All").strip()
                semester = data.get("semester", "All").strip()
                academic_session = data.get("academic_session", "All").strip()
                default_amount = float(data.get("default_amount", 0.0))
                description = data.get("description", "").strip()
                is_active = bool(data.get("is_active", True))
            else:
                name = str(data).strip()
                course = str(args[0]).strip() if args else "All"
                branch = "All"
                academic_year = "All"
                semester = "All"
                academic_session = "All"
                default_amount = float(args[1]) if len(args) > 1 else (float(kwargs.get("default_amount", 0.0)))
                description = kwargs.get("description", "").strip()
                is_active = kwargs.get("is_active", True)

            if not name:
                return False, "Description / Fee Head Name is required."

            target_course = course if course else "All"
            existing = db.query(FeeCategory).filter(
                FeeCategory.name.ilike(name),
                FeeCategory.course == target_course,
                FeeCategory.semester == (semester if semester else "All"),
                FeeCategory.academic_session == (academic_session if academic_session else "All")
            ).first()
            if existing:
                return False, f"Fee Head '{name}' already exists for {target_course} ({semester}, {academic_session})."

            cat = FeeCategory(
                name=name,
                course=target_course,
                branch=branch if branch else "All",
                academic_year=academic_year if academic_year else "All",
                semester=semester if semester else "All",
                academic_session=academic_session if academic_session else "All",
                default_amount=max(0.0, default_amount),
                is_active=is_active,
                description=description
            )
            db.add(cat)

            user = AuthController.get_current_user()
            user_id = user.id if user else None
            audit = AuditLog(user_id=user_id, action="CREATE_FEE_CATEGORY", details=f"Added fee head: {name} ({course})")
            db.add(audit)

            db.commit()
            logger.info(f"Created fee category: {name} ({course})")
            return True, f"Fee Head '{name}' ({course}) created successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating fee category: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def update_category(cat_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        db = get_db()
        try:
            cat = db.query(FeeCategory).filter(FeeCategory.id == cat_id).first()
            if not cat:
                return False, "Fee Category not found."

            name = data.get("name", cat.name).strip()
            course = data.get("course", cat.course).strip().upper()
            default_amount = float(data.get("default_amount", cat.default_amount))
            is_active = bool(data.get("is_active", cat.is_active))
            description = data.get("description", cat.description or "").strip()

            if not name:
                return False, "Description / Fee Head Name is required."

            branch = data.get("branch", cat.branch or "All").strip()
            academic_year = data.get("academic_year", cat.academic_year or "All").strip()
            semester = data.get("semester", cat.semester or "All").strip()
            academic_session = data.get("academic_session", cat.academic_session or "All").strip()

            # Duplicate check
            existing = db.query(FeeCategory).filter(
                FeeCategory.name.ilike(name),
                FeeCategory.course == course,
                FeeCategory.semester == semester,
                FeeCategory.academic_session == academic_session,
                FeeCategory.id != cat_id
            ).first()
            if existing:
                return False, f"Fee Head '{name}' already exists under {course} ({semester}, {academic_session})."

            cat.name = name
            cat.course = course
            cat.branch = branch
            cat.academic_year = academic_year
            cat.semester = semester
            cat.academic_session = academic_session
            cat.default_amount = max(0.0, default_amount)
            cat.is_active = is_active
            cat.description = description

            db.commit()
            logger.info(f"Updated fee category ID {cat_id}: {name} ({course})")
            return True, f"Fee Head '{name}' updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating fee category {cat_id}: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def delete_category(cat_id: int) -> Tuple[bool, str]:
        db = get_db()
        try:
            cat = db.query(FeeCategory).filter(FeeCategory.id == cat_id).first()
            if not cat:
                return False, "Fee Category not found."

            cat_name = cat.name
            db.delete(cat)
            db.commit()

            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Fee Head Deleted",
                module="Fee Heads",
                details=f"Deleted Fee Head: '{cat_name}' (ID {cat_id})",
                status="Success"
            )
            logger.info(f"Deleted fee category ID {cat_id}: {cat_name}")
            return True, f"Fee Category '{cat_name}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting fee category {cat_id}: {e}", exc_info=True)
            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Fee Head Delete Failed",
                module="Fee Heads",
                details=f"Failed to delete Fee Head ID {cat_id}: {str(e)}",
                status="Failed"
            )
            return False, f"Cannot delete Fee Category in use by active receipts. {str(e)}"
        finally:
            db.close()

    @staticmethod
    def seed_default_fee_heads():
        """Seeds official 14 UG and 4 PG Fee Heads with exact college-provided spellings."""
        db = get_db()
        try:
            ug_heads = [
                ("ADMISSION FORM FEE", 500.0),
                ("UG TUTION FEE", 12000.0),
                ("UG DEVELOPMENT FEE", 3000.0),
                ("SOCIAL GATHERING FEE", 500.0),
                ("SPORT FEE", 300.0),
                ("ELIGIBILTY FEE", 400.0),
                ("IDENTITY CARD FEE", 100.0),
                ("SRTMU EXAM FEE", 800.0),
                ("SRTMU GRM/PHOTOCOPY FEE", 150.0),
                ("UG LABORATORY DEPOSIT", 1000.0),
                ("UG CLUB FEES", 200.0),
                ("UG LABROTARY CHARGES", 1500.0),
                ("CAUTION MONEY", 500.0),
                ("OTHER FINE", 100.0)
            ]

            pg_heads = [
                ("ADMISSION FORM FEE", 500.0),
                ("PG TUTION FEE", 18000.0),
                ("PG DEVELOPMENT FEE", 5000.0),
                ("PG LABORATORY USAGES", 2500.0)
            ]

            for name, amt in ug_heads:
                existing = db.query(FeeCategory).filter(FeeCategory.name == name, FeeCategory.course == "UG").first()
                if not existing:
                    db.add(FeeCategory(name=name, course="UG", default_amount=amt, is_active=True))

            for name, amt in pg_heads:
                existing = db.query(FeeCategory).filter(FeeCategory.name == name, FeeCategory.course == "PG").first()
                if not existing:
                    db.add(FeeCategory(name=name, course="PG", default_amount=amt, is_active=True))

            db.commit()
            logger.info("Default official UG and PG fee heads seeded successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to seed default fee heads: {e}", exc_info=True)
        finally:
            db.close()
