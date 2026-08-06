"""
Centralized Security & Audit Logging Service for EduLedger ERP.
Provides administrator password verification, permission checks, and centralized audit trails.
"""

import socket
from typing import Optional
from config.database import get_db
from models.user import User
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.security import verify_password
from utils.logger import logger

class SecurityService:
    @classmethod
    def verify_admin_password(cls, password: str) -> bool:
        """
        Verifies if the provided plain-text password matches ANY active Administrator account.
        UI views MUST call this function rather than comparing raw password hashes directly.
        """
        if not password or not password.strip():
            return False
            
        db = get_db()
        try:
            # Retrieve all active admin users
            admin_users = db.query(User).filter(
                User.role == "Admin",
                User.status == "Active"
            ).all()

            for admin in admin_users:
                if verify_password(password, admin.password_hash):
                    logger.info(f"Administrator password verified successfully (Admin User: {admin.username})")
                    return True

            logger.warning("Administrator password verification failed: Incorrect password")
            return False
        except Exception as e:
            logger.error(f"Error verifying admin password: {e}", exc_info=True)
            return False
        finally:
            db.close()

    @classmethod
    def log_audit(
        cls,
        action: str,
        module: Optional[str] = None,
        details: Optional[str] = None,
        status: str = "Success",
        user_id: Optional[int] = None
    ) -> bool:
        """
        Centralized audit logging helper that records security events and administrative operations.
        Captures Date, Time, Username, Action, Module, Details, Status, and Hostname.
        """
        db = get_db()
        try:
            curr_user = AuthController.get_current_user()
            target_user_id = user_id or (curr_user.id if curr_user else None)
            machine_name = socket.gethostname()

            audit_entry = AuditLog(
                user_id=target_user_id,
                action=action,
                module=module,
                details=details,
                status=status,
                machine_name=machine_name
            )
            db.add(audit_entry)
            db.commit()
            logger.info(f"Audit log recorded: Action='{action}', Module='{module}', Status='{status}'")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record audit log: {e}", exc_info=True)
            return False
        finally:
            db.close()
