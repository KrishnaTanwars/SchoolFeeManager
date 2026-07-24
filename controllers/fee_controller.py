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
    def get_all_categories(active_only: bool = False) -> List[FeeCategory]:
        db = get_db()
        try:
            query = db.query(FeeCategory)
            if active_only:
                query = query.filter(FeeCategory.is_active == True)
            cats = query.order_by(FeeCategory.name.asc()).all()
            for c in cats:
                db.expunge(c)
            return cats
        finally:
            db.close()

    @staticmethod
    def create_category(name: str, code: str, default_amount: float, description: str = "") -> Tuple[bool, str]:
        db = get_db()
        try:
            name_clean = name.strip()
            if not name_clean:
                return False, "Category Name is required."

            existing = db.query(FeeCategory).filter(FeeCategory.name == name_clean).first()
            if existing:
                return False, f"Fee Category '{name_clean}' already exists."

            cat = FeeCategory(
                name=name_clean,
                code=code.strip().upper(),
                default_amount=max(0.0, default_amount),
                is_active=True,
                description=description.strip()
            )
            db.add(cat)

            user = AuthController.get_current_user()
            user_id = user.id if user else None
            audit = AuditLog(user_id=user_id, action="CREATE_FEE_CATEGORY", details=f"Added fee head: {name_clean}")
            db.add(audit)

            db.commit()
            logger.info(f"Created fee category: {name_clean}")
            return True, "Fee category created successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating fee category: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def update_category(
        cat_id: int, name: str, code: str, default_amount: float, is_active: bool, description: str = ""
    ) -> Tuple[bool, str]:
        db = get_db()
        try:
            cat = db.query(FeeCategory).filter(FeeCategory.id == cat_id).first()
            if not cat:
                return False, "Fee Category not found."

            name_clean = name.strip()
            if name_clean != cat.name:
                existing = db.query(FeeCategory).filter(FeeCategory.name == name_clean).first()
                if existing:
                    return False, f"Fee Category '{name_clean}' already exists."

            cat.name = name_clean
            cat.code = code.strip().upper()
            cat.default_amount = max(0.0, default_amount)
            cat.is_active = is_active
            cat.description = description.strip()

            db.commit()
            logger.info(f"Updated fee category ID {cat_id}: {name_clean}")
            return True, "Fee Category updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating fee category {cat_id}: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()
