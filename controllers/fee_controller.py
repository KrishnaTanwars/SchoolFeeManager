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
    def create_category(data: Any, *args, **kwargs) -> Tuple[bool, str]:
        """
        Creates fee category. Supports dict or legacy positional args.
        data dict keys: name, course, default_amount, description, is_active
        """
        db = get_db()
        try:
            if isinstance(data, dict):
                name = data.get("name", "").strip()
                course = data.get("course", "UG").strip().upper()
                default_amount = float(data.get("default_amount", 0.0))
                description = data.get("description", "").strip()
                is_active = bool(data.get("is_active", True))
            else:
                name = str(data).strip()
                course = str(args[0]).strip().upper() if args else "UG"
                default_amount = float(args[1]) if len(args) > 1 else (float(kwargs.get("default_amount", 0.0)))
                description = kwargs.get("description", "").strip()
                is_active = kwargs.get("is_active", True)

            if not name:
                return False, "Description / Fee Head Name is required."
            if course not in ("UG", "PG"):
                course = "UG"

            # Check duplicate within the same course
            existing = db.query(FeeCategory).filter(
                FeeCategory.name.ilike(name),
                FeeCategory.course == course
            ).first()
            if existing:
                return False, f"Fee Head '{name}' already exists under {course} course."

            cat = FeeCategory(
                name=name,
                course=course,
                default_amount=max(0.0, default_amount),
                is_active=is_active,
                description=description
            )
            db.add(cat)

            user = AuthController.get_current_user()
            user_id = user.id if user else None
            audit = AuditLog(user_id=user_id, action="CREATE_FEE_CATEGORY", details=f"Added {course} fee head: {name}")
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

            # Duplicate check
            existing = db.query(FeeCategory).filter(
                FeeCategory.name.ilike(name),
                FeeCategory.course == course,
                FeeCategory.id != cat_id
            ).first()
            if existing:
                return False, f"Fee Head '{name}' already exists under {course} course."

            cat.name = name
            cat.course = course
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
        """Seeds default 14 UG and 3 PG Fee Heads if they do not exist."""
        db = get_db()
        try:
            ug_heads = [
                ("Admission Form Fee", 500.0),
                ("UG Tuition Fee", 12000.0),
                ("UG Development Fee", 3000.0),
                ("Social Gathering Fee", 500.0),
                ("Sports Fee", 300.0),
                ("Eligibility Fee", 400.0),
                ("Identity Card Fee", 100.0),
                ("SRTMU Exam Fee", 800.0),
                ("SRTMU GRM / Photocopy Fee", 150.0),
                ("UG Laboratory Deposit", 1000.0),
                ("UG Club Fee", 200.0),
                ("UG Laboratory Charges", 1500.0),
                ("Caution Money", 500.0),
                ("Other Fine", 100.0)
            ]

            pg_heads = [
                ("PG Tuition Fee", 18000.0),
                ("PG Development Fee", 5000.0),
                ("PG Laboratory Usage Fee", 2500.0)
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
            logger.info("Default UG and PG fee heads seeded successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to seed default fee heads: {e}", exc_info=True)
        finally:
            db.close()
