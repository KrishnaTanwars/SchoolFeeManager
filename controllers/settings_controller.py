"""
College Information and Academic Session Settings Controller with Expunge Safety.
"""

from typing import Optional, List, Tuple, Dict, Any
from config.database import get_db
from models.settings import SchoolInformation, AcademicSession
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

import os
import sqlite3
from pathlib import Path
from PySide6.QtCore import QSettings
from config.app_config import DB_PATH
from models.student import Student
from models.receipt import Receipt
from models.fee_category import FeeCategory
from models.user import User

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
    def get_active_logo_path() -> Optional[str]:
        """
        Resolves active logo file path across user installations safely.
        Checks DB school_info.logo_path -> assets/custom_logo.png -> assets/college_logo.png.
        """
        info = SettingsController.get_school_info()
        if info and info.logo_path:
            lp = Path(info.logo_path)
            if lp.exists():
                return str(lp.resolve())
            rel_app = Path(__file__).resolve().parent.parent / info.logo_path
            if rel_app.exists():
                return str(rel_app.resolve())

        default_logo = Path(__file__).resolve().parent.parent / "assets" / "college_logo.png"
        if default_logo.exists():
            return str(default_logo.resolve())
        return None

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
            info.city = data.get("city", info.city or "").strip()
            info.state = data.get("state", info.state or "").strip()
            info.pin_code = data.get("pin_code", info.pin_code or "").strip()
            info.phone = data.get("phone", info.phone).strip()
            info.email = data.get("email", info.email).strip()
            info.website = data.get("website", info.website or "").strip()
            info.principal_name = data.get("principal_name", info.principal_name or "").strip()
            info.logo_path = data.get("logo_path", info.logo_path)
            info.receipt_prefix = data.get("receipt_prefix", info.receipt_prefix or "REC/").strip()
            info.receipt_footer = data.get("receipt_footer", info.receipt_footer or "").strip()
            info.current_session = data.get("current_session", info.current_session or "2025-2026").strip()

            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Settings Updated",
                module="Settings",
                details=f"Updated college profile settings for {info.school_name}",
                status="Success"
            )

            db.commit()
            logger.info("Updated college information settings.")
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
    def get_current_session() -> str:
        from services.session_service import session_manager
        return session_manager.get_active_session()

    @staticmethod
    def set_current_session(session_name: str) -> Tuple[bool, str]:
        from services.session_service import session_manager
        return session_manager.set_active_session(session_name)

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        db = get_db()
        try:
            db_size_bytes = DB_PATH.stat().st_size if DB_PATH.exists() else 0
            size_str = f"{db_size_bytes / (1024 * 1024):.2f} MB" if db_size_bytes >= 1024 * 1024 else f"{db_size_bytes / 1024:.1f} KB"

            student_count = db.query(Student).count()
            receipt_count = db.query(Receipt).count()
            fee_head_count = db.query(FeeCategory).count()
            user_count = db.query(User).count()
            audit_count = db.query(AuditLog).count()

            return {
                "db_path": str(DB_PATH.resolve()),
                "db_size": size_str,
                "db_size_bytes": db_size_bytes,
                "student_count": student_count,
                "receipt_count": receipt_count,
                "fee_head_count": fee_head_count,
                "user_count": user_count,
                "audit_count": audit_count
            }
        except Exception as e:
            logger.error(f"Error getting DB statistics: {e}", exc_info=True)
            return {
                "db_path": str(DB_PATH.resolve()),
                "db_size": "Unknown",
                "student_count": 0,
                "receipt_count": 0,
                "fee_head_count": 0,
                "user_count": 0,
                "audit_count": 0
            }
        finally:
            db.close()

    @staticmethod
    def optimize_database() -> Tuple[bool, str]:
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                conn.execute("VACUUM;")
                conn.execute("ANALYZE;")
            logger.info("Database optimized (VACUUM and ANALYZE completed).")
            return True, "Database vacuumed and optimized successfully."
        except Exception as e:
            logger.error(f"Error optimizing database: {e}", exc_info=True)
            return False, f"Optimization failed: {str(e)}"

    @staticmethod
    def verify_database_integrity() -> Tuple[bool, str]:
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                msg = result[0] if result else "Unknown"
                if msg == "ok":
                    return True, "Database integrity verification passed: OK"
                else:
                    return False, f"Integrity check issue: {msg}"
        except Exception as e:
            logger.error(f"Error verifying DB integrity: {e}", exc_info=True)
            return False, f"Integrity check failed: {str(e)}"

    @staticmethod
    def get_audit_logs(
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        db = get_db()
        try:
            query = db.query(AuditLog, User.username).outerjoin(User, AuditLog.user_id == User.id)

            if module and module != "All":
                query = query.filter(AuditLog.module == module)
            if action and action != "All":
                query = query.filter(AuditLog.action.ilike(f"%{action}%"))
            if username and username != "All":
                query = query.filter(User.username == username)
            if search and search.strip():
                s = f"%{search.strip()}%"
                query = query.filter(
                    (AuditLog.action.ilike(s)) |
                    (AuditLog.module.ilike(s)) |
                    (AuditLog.details.ilike(s)) |
                    (User.username.ilike(s))
                )

            query = query.order_by(AuditLog.timestamp.desc())
            if limit and limit > 0:
                query = query.limit(limit)

            records = query.all()
            results = []
            for audit, uname in records:
                dt_str = audit.timestamp.strftime("%Y-%m-%d") if audit.timestamp else ""
                tm_str = audit.timestamp.strftime("%H:%M:%S") if audit.timestamp else ""
                results.append({
                    "id": audit.id,
                    "date": dt_str,
                    "time": tm_str,
                    "timestamp": audit.timestamp,
                    "user_id": audit.user_id,
                    "user": uname or "Administrator",
                    "action": audit.action or "System Action",
                    "module": audit.module or "General",
                    "details": audit.details or "",
                    "status": audit.status or "Success",
                    "ip_address": getattr(audit, "ip_address", getattr(audit, "machine_name", "Localhost")) or "Localhost"
                })

            if date_from:
                results = [r for r in results if r["date"] >= date_from]
            if date_to:
                results = [r for r in results if r["date"] <= date_to]

            return results
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}", exc_info=True)
            return []
        finally:
            db.close()

    @staticmethod
    def clear_audit_logs() -> Tuple[bool, str]:
        if not AuthController.is_admin():
            return False, "Only Administrators can clear audit logs."

        db = get_db()
        try:
            count = db.query(AuditLog).count()
            db.query(AuditLog).delete(synchronize_session=False)
            db.commit()

            curr = AuthController.get_current_user()
            audit = AuditLog(
                user_id=curr.id if curr else None,
                action="CLEAR_AUDIT_LOGS",
                module="AuditLogs",
                details=f"Cleared {count} audit log records.",
                status="Success"
            )
            db.add(audit)
            db.commit()
            return True, f"Successfully cleared {count} audit log records."
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing audit logs: {e}", exc_info=True)
            return False, f"Failed to clear audit logs: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_preferences() -> Dict[str, Any]:
        settings = QSettings("EduLedger", "CollegeFeeManager")
        return {
            "window_size": settings.value("window_size", "1280x750"),
            "sidebar_expanded": settings.value("sidebar_expanded", False, type=bool),
            "theme": settings.value("theme", "Professional Navy"),
            "auto_backup_enabled": settings.value("auto_backup_enabled", True, type=bool),
            "auto_backup_frequency": settings.value("auto_backup_frequency", "Daily"),
            "backup_retention": settings.value("backup_retention", "10"),
            "auto_backup": settings.value("auto_backup", True, type=bool),
            "backup_frequency": settings.value("backup_frequency", "Daily"),
            "receipt_printer": settings.value("receipt_printer", "Default PDF Printer"),
            "export_folder": settings.value("export_folder", str(Path.home() / "Documents" / "EduLedger_Exports")),
            "backup_folder": settings.value("backup_folder", str(Path.home() / "Documents" / "EduLedger_Backups")),
            "currency_symbol": settings.value("currency_symbol", "₹"),
            "date_format": settings.value("date_format", "DD/MM/YYYY"),
            "time_format": settings.value("time_format", "12-Hour (AM/PM)"),
            "auto_logout_minutes": settings.value("auto_logout_minutes", 30, type=int),
            "remember_login": settings.value("remember_login", False, type=bool)
        }

    @staticmethod
    def get_app_preferences() -> Dict[str, Any]:
        return SettingsController.get_preferences()

    @staticmethod
    def save_preferences(prefs: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            settings = QSettings("EduLedger", "CollegeFeeManager")
            for k, v in prefs.items():
                settings.setValue(k, v)
            logger.info("Saved application preferences to QSettings.")
            return True, "Application preferences saved successfully."
        except Exception as e:
            logger.error(f"Error saving preferences: {e}", exc_info=True)
            return False, f"Failed to save preferences: {str(e)}"

    @staticmethod
    def save_app_preferences(prefs: Dict[str, Any]) -> Tuple[bool, str]:
        return SettingsController.save_preferences(prefs)

