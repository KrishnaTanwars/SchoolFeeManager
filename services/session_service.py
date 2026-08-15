"""
Centralized Academic Session Management Service.
Manages current session state, real-time UI header synchronization, and listener notifications.
"""

from typing import Callable, List, Optional
from config.database import get_db
from models.settings import AcademicSession
from utils.logger import logger

class SessionManager:
    _listeners: List[Callable[[str], None]] = []
    _cached_session: Optional[str] = None

    @classmethod
    def register_listener(cls, callback: Callable[[str], None]):
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def unregister_listener(cls, callback: Callable[[str], None]):
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    @classmethod
    def _notify_listeners(cls, new_session: str):
        for cb in list(cls._listeners):
            try:
                cb(new_session)
            except Exception as e:
                logger.error(f"Error notifying session listener: {e}")

    @classmethod
    def get_current_session(cls) -> str:
        """Returns the currently marked active session name, or '2024-2025' default."""
        if cls._cached_session:
            return cls._cached_session

        db = get_db()
        try:
            curr = db.query(AcademicSession).filter(AcademicSession.is_current == True).first()
            if curr:
                cls._cached_session = curr.session_name
                return curr.session_name
            
            # Fallback to first session or default
            first_s = db.query(AcademicSession).first()
            if first_s:
                cls._cached_session = first_s.session_name
                return first_s.session_name
            return "2024-2025"
        except Exception as e:
            logger.error(f"Error retrieving current session: {e}")
            return "2024-2025"
        finally:
            db.close()

    @classmethod
    def set_current_session(cls, session_name: str) -> tuple[bool, str]:
        """Sets the active session in database and notifies all UI listeners."""
        if not session_name or not session_name.strip():
            return False, "Session name cannot be empty."

        s_name = session_name.strip()
        db = get_db()
        try:
            db.query(AcademicSession).update({AcademicSession.is_current: False})
            target = db.query(AcademicSession).filter(AcademicSession.session_name == s_name).first()
            if target:
                target.is_current = True
            else:
                target = AcademicSession(session_name=s_name, is_current=True)
                db.add(target)
            db.commit()
            
            cls._cached_session = s_name
            cls._notify_listeners(s_name)
            logger.info(f"SessionManager updated current session to: {s_name}")
            return True, f"Active session changed to '{s_name}'."
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting current session: {e}")
            return False, f"Failed to set session: {str(e)}"
        finally:
            db.close()

    @classmethod
    def get_active_session(cls) -> str:
        return cls.get_current_session()

    @classmethod
    def set_active_session(cls, session_name: str) -> tuple[bool, str]:
        return cls.set_current_session(session_name)

    @classmethod
    def add_session(cls, session_name: str) -> tuple[bool, str]:
        """Adds a new academic session to the database if it doesn't already exist."""
        if not session_name or not session_name.strip():
            return False, "Session name cannot be empty."

        s_name = session_name.strip()
        db = get_db()
        try:
            existing = db.query(AcademicSession).filter(AcademicSession.session_name == s_name).first()
            if existing:
                return False, f"Academic Session '{s_name}' already exists."

            new_s = AcademicSession(session_name=s_name, is_current=False)
            db.add(new_s)
            db.commit()
            logger.info(f"Added new academic session: {s_name}")
            return True, f"Academic Session '{s_name}' added successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding academic session: {e}")
            return False, f"Failed to add session: {str(e)}"
        finally:
            db.close()

    @classmethod
    def get_all_sessions(cls) -> List[str]:
        """Returns list of all session names."""
        db = get_db()
        try:
            sessions = db.query(AcademicSession).order_by(AcademicSession.session_name.desc()).all()
            if not sessions:
                return ["2024-2025", "2025-2026"]
            return [s.session_name for s in sessions]
        except Exception as e:
            logger.error(f"Error fetching all sessions: {e}")
            return ["2024-2025"]
        finally:
            db.close()

session_manager = SessionManager()

