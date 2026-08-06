"""
School Information and Academic Session Settings Controller with Expunge Safety.
"""

from typing import Optional, List, Tuple, Dict, Any
from config.database import get_db
from models.settings import SchoolInformation, AcademicSession
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

class SettingsController:
    @staticmethod
    def get_school_info() -> Optional[SchoolInformation]:
        db = get_db()
        try:
            info = db.query(SchoolInformation).first()
            if info:
                db.expunge(info)
            return info
        finally:
            db.close()

    @staticmethod
    def update_school_info(data: Dict[str, Any]) -> Tuple[bool, str]:
        db = get_db()
        try:
            info = db.query(SchoolInformation).first()
            if not info:
                info = SchoolInformation()
                db.add(info)

            info.school_name = data.get("school_name", info.school_name).strip()
            info.address = data.get("address", info.address).strip()
            info.phone = data.get("phone", info.phone).strip()
            info.email = data.get("email", info.email).strip()
            info.website = data.get("website", info.website).strip()
            info.logo_path = data.get("logo_path", info.logo_path)
            info.receipt_prefix = data.get("receipt_prefix", info.receipt_prefix).strip()
            info.receipt_footer = data.get("receipt_footer", info.receipt_footer).strip()
            info.current_session = data.get("current_session", info.current_session).strip()

            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Settings Updated",
                module="Settings",
                details=f"Updated school profile settings for {info.school_name}",
                status="Success"
            )

            db.commit()
            logger.info("Updated school information settings.")
            return True, "Settings updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating school settings: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_academic_sessions() -> List[AcademicSession]:
        db = get_db()
        try:
            sessions = db.query(AcademicSession).order_by(AcademicSession.session_name.desc()).all()
            for s in sessions:
                db.expunge(s)
            return sessions
        finally:
            db.close()

    @staticmethod
    def set_current_session(session_name: str) -> Tuple[bool, str]:
        db = get_db()
        try:
            sessions = db.query(AcademicSession).all()
            found = False
            for s in sessions:
                if s.session_name == session_name:
                    s.is_current = True
                    found = True
                else:
                    s.is_current = False

            if not found:
                new_s = AcademicSession(session_name=session_name, is_current=True)
                db.add(new_s)

            info = db.query(SchoolInformation).first()
            if info:
                info.current_session = session_name

            db.commit()
            logger.info(f"Switched current academic session to: {session_name}")
            return True, f"Switched to session '{session_name}'."
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting current session: {e}", exc_info=True)
            return False, f"Database error: {str(e)}"
        finally:
            db.close()
