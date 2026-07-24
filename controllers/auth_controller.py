"""
Authentication and User Session Controller with Expunged Session Instances.
"""

from typing import Optional, Dict, Any, List
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
            user = db.query(User).filter(User.username == username, User.status == "Active").first()
            if user and verify_password(password, user.password_hash):
                user.last_login = datetime.utcnow()
                
                # Add audit log
                audit = AuditLog(user_id=user.id, action="LOGIN", details=f"User {user.username} logged in.")
                db.add(audit)
                db.commit()

                # Expunge from DB session so attributes stay loaded in memory
                db.expunge(user)
                cls._current_user = user
                logger.info(f"Successful login for user: {username}")
                return True
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
    def is_admin(cls) -> bool:
        return cls._current_user is not None and cls._current_user.role == "Admin"

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
            new_user = User(
                username=username,
                password_hash=hash_password(password),
                full_name=full_name,
                role=role,
                status="Active"
            )
            db.add(new_user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}", exc_info=True)
            return False
        finally:
            db.close()
