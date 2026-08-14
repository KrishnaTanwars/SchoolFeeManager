"""
Centralized Active Academic Session Service for EduLedger ERP.
Single source of truth for active academic session across all modules with real-time PySide6 signal propagation.
"""

from typing import Tuple, Optional, List
from PySide6.QtCore import QObject, Signal
from config.database import get_db
from models.settings import AcademicSession, SchoolInformation
from utils.logger import logger

class SessionManager(QObject):
    """
    Centralized Session Manager Service emitting real-time signals on active session state change.
    """
    session_changed = Signal(str)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if not hasattr(self, "_initialized"):
            super().__init__(parent)
            self._active_session: Optional[str] = None
            self._initialized = True

    def get_active_session(self) -> str:
        """
        Retrieves current active academic session name from DB / cache.
        Single source of truth for entire ERP application.
        """
        db = get_db()
        try:
            active_s = db.query(AcademicSession).filter(AcademicSession.is_current == True).first()
            if active_s and active_s.session_name:
                self._active_session = active_s.session_name.strip()
                return self._active_session

            # Fallback 1: Check SchoolInformation.current_session
            info = db.query(SchoolInformation).first()
            if info and info.current_session:
                self._active_session = info.current_session.strip()
                return self._active_session

            # Fallback 2: Default operational session
            self._active_session = "2024-2025"
            return self._active_session
        except Exception as e:
            logger.error(f"Error fetching active academic session: {e}", exc_info=True)
            return self._active_session or "2024-2025"
        finally:
            db.close()

    def set_active_session(self, session_name: str) -> Tuple[bool, str]:
        """
        Updates the active academic session in database and emits real-time session_changed signal.
        """
        s_name = session_name.strip()
        if not s_name:
            return False, "Session name cannot be empty."

        db = get_db()
        try:
            sessions = db.query(AcademicSession).all()
            found = False
            for s in sessions:
                if s.session_name == s_name:
                    s.is_current = True
                    found = True
                else:
                    s.is_current = False

            if not found:
                new_session = AcademicSession(session_name=s_name, is_current=True)
                db.add(new_session)

            info = db.query(SchoolInformation).first()
            if info:
                info.current_session = s_name

            db.commit()

            old_session = self._active_session
            self._active_session = s_name

            # Log Audit Trail
            try:
                from services.security_service import SecurityService
                SecurityService.log_audit(
                    action="Session Changed",
                    module="Settings",
                    details=f"Switched active academic session from '{old_session}' to '{s_name}'",
                    status="Success"
                )
            except Exception as audit_err:
                logger.warning(f"Could not log audit for session change: {audit_err}")

            logger.info(f"Active academic session updated to: {s_name}")
            
            # Emit PySide6 signal for real-time header and UI updates
            self.session_changed.emit(s_name)

            return True, f"Switched to academic session '{s_name}' successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting active session '{s_name}': {e}", exc_info=True)
            return False, f"Database error updating active session: {str(e)}"
        finally:
            db.close()

    def refresh(self) -> str:
        """
        Forces refresh of cached active session from DB and notifies listeners if changed.
        """
        old_val = self._active_session
        new_val = self.get_active_session()
        if old_val != new_val:
            self.session_changed.emit(new_val)
        return new_val


# Global singleton instance
session_manager = SessionManager()
