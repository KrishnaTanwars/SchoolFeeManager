"""
Authentication and User Session Controller with Expunged Session Instances.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from config.database import get_db
from models.user import User
from models.audit import AuditLog
from utils.security import verify_password, hash_password
from utils.logger import logger

class AuthController:
    _current_user: Optional[User] = None

    @classmethod
    def login(cls, username: str, password: str) -> bool:
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and user.status == "Active" and verify_password(password, user.password_hash):
                user.last_login = datetime.utcnow()
                user.failed_attempts = 0
                
                # Add audit log
                audit = AuditLog(user_id=user.id, action="LOGIN", module="Auth", details=f"User '{user.username}' logged in successfully.", status="Success")
                db.add(audit)
                db.commit()

                # Expunge from DB session so attributes stay loaded in memory
                db.expunge(user)
                cls._current_user = user
                logger.info(f"Successful login for user: {username}")
                return True
            
            if user:
                user.failed_attempts = (user.failed_attempts or 0) + 1
                audit = AuditLog(user_id=user.id, action="LOGIN_FAILED", module="Auth", details=f"Failed login attempt for user '{username}' (Failed count: {user.failed_attempts}).", status="Failed")
                db.add(audit)
                db.commit()
            else:
                audit = AuditLog(user_id=None, action="LOGIN_FAILED", module="Auth", details=f"Failed login attempt for non-existent username '{username}'.", status="Failed")
                db.add(audit)
                db.commit()

            logger.warning(f"Failed login attempt for username: {username}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Login error: {e}", exc_info=True)
            return False
        finally:
            db.close()

    @classmethod
    def logout(cls):
        if cls._current_user:
            logger.info(f"User logged out: {cls._current_user.username}")
        cls._current_user = None

    @classmethod
    def get_current_user(cls) -> Optional[User]:
        return cls._current_user

    @classmethod
    def is_authenticated(cls) -> bool:
        return cls._current_user is not None

    @classmethod
    def is_admin(cls) -> bool:
        return cls._current_user is not None and cls._current_user.role in ("Admin", "Administrator")

    @classmethod
    def verify_admin_password(cls, password: str, module: Optional[str] = "General") -> bool:
        from services.security_service import SecurityService
        return SecurityService.verify_admin_password(password, module=module)

    @classmethod
    def get_all_users(cls) -> List[User]:
        db = get_db()
        try:
            users = db.query(User).all()
            for u in users:
                db.expunge(u)
            return users
        finally:
            db.close()

    @classmethod
    def create_user(cls, username: str, password: str, full_name: str, role: str) -> bool:
        db = get_db()
        try:
            if db.query(User).filter(User.username == username).first():
                return False
            norm_role = "Admin" if role in ("Admin", "Administrator") else ("Viewer" if role == "Viewer" else "Operator")
            new_user = User(
                username=username,
                password_hash=hash_password(password),
                full_name=full_name,
                role=norm_role,
                status="Active",
                failed_attempts=0
            )
            db.add(new_user)
            db.commit()

            curr = cls.get_current_user()
            audit = AuditLog(user_id=curr.id if curr else None, action="CREATE_USER", module="UserManagement", details=f"Created user '{username}' with role '{norm_role}'.", status="Success")
            db.add(audit)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}", exc_info=True)
            return False
        finally:
            db.close()

    @classmethod
    def update_user(cls, user_id: int, full_name: str, role: str, status: str) -> Tuple[bool, str]:
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found."

            norm_role = "Admin" if role in ("Admin", "Administrator") else ("Viewer" if role == "Viewer" else "Operator")
            
            # Check if changing role/status of last active admin
            if user.role == "Admin" and norm_role != "Admin":
                active_admins = db.query(User).filter(User.role == "Admin", User.status == "Active", User.id != user_id).count()
                if active_admins == 0:
                    return False, "Cannot change role of the last active Administrator."

            if user.role == "Admin" and status != "Active":
                active_admins = db.query(User).filter(User.role == "Admin", User.status == "Active", User.id != user_id).count()
                if active_admins == 0:
                    return False, "Cannot disable the last active Administrator."

            user.full_name = full_name
            user.role = norm_role
            user.status = status
            db.commit()

            curr = cls.get_current_user()
            audit = AuditLog(user_id=curr.id if curr else None, action="UPDATE_USER", module="UserManagement", details=f"Updated user '{user.username}' details (Role: {norm_role}, Status: {status}).", status="Success")
            db.add(audit)
            db.commit()
            return True, "User updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}", exc_info=True)
            return False, f"Failed to update user: {str(e)}"
        finally:
            db.close()

    @classmethod
    def delete_user(cls, user_id: int) -> Tuple[bool, str]:
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found."

            if user.role == "Admin":
                active_admins = db.query(User).filter(User.role == "Admin", User.id != user_id).count()
                if active_admins == 0:
                    return False, "Cannot delete the last Administrator account."

            username = user.username
            db.delete(user)
            db.commit()

            curr = cls.get_current_user()
            audit = AuditLog(user_id=curr.id if curr else None, action="DELETE_USER", module="UserManagement", details=f"Deleted user '{username}'.", status="Success")
            db.add(audit)
            db.commit()
            return True, f"User '{username}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {e}", exc_info=True)
            return False, f"Failed to delete user: {str(e)}"
        finally:
            db.close()

    @classmethod
    def reset_password(cls, user_id: int, new_password: str) -> Tuple[bool, str]:
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found."

            user.password_hash = hash_password(new_password)
            user.failed_attempts = 0
            db.commit()

            curr = cls.get_current_user()
            audit = AuditLog(user_id=curr.id if curr else None, action="RESET_PASSWORD", module="UserManagement", details=f"Reset password for user '{user.username}'.", status="Success")
            db.add(audit)
            db.commit()
            return True, f"Password for '{user.username}' reset successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting password: {e}", exc_info=True)
            return False, f"Failed to reset password: {str(e)}"
        finally:
            db.close()

    @classmethod
    def change_password(cls, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found."

            if not verify_password(old_password, user.password_hash):
                return False, "Current password is incorrect."

            user.password_hash = hash_password(new_password)
            db.commit()

            audit = AuditLog(user_id=user.id, action="CHANGE_PASSWORD", module="UserManagement", details=f"User '{user.username}' changed their password.", status="Success")
            db.add(audit)
            db.commit()
            return True, "Password changed successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {e}", exc_info=True)
            return False, f"Failed to change password: {str(e)}"
        finally:
            db.close()
