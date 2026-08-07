"""
Database Backup, Restore, Auto-Backup & Maintenance Service for EduLedger ERP v1.9.0.
Creates timestamped ZIP backups bundling DB, configuration, preferences, and logs;
enforces auto-backup scheduling and retention rules; performs VACUUM, REINDEX, and integrity checks.
"""

import os
import shutil
import zipfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

from config.app_config import DB_PATH, BACKUP_DIR, APP_DIR
from config.database import get_db, SessionLocal, engine
from models.audit import BackupHistory, AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger


class BackupService:
    @staticmethod
    def create_backup(dest_dir: Optional[Path] = None, backup_type: str = "Manual") -> Tuple[bool, str, str]:
        """
        Creates a timestamped backup ZIP bundling school_fee.db, school_settings, preferences, and logs.
        Returns: (success: bool, message: str, backup_path: str)
        """
        if not DB_PATH.exists():
            return False, "Database file does not exist.", ""

        if dest_dir is None:
            dest_dir = BACKUP_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"school_fee_backup_{timestamp}.zip"
        backup_path = dest_dir / backup_filename

        db = get_db()
        try:
            # Checkpoint WAL before backup
            with sqlite3.connect(str(DB_PATH)) as conn:
                conn.execute("PRAGMA wal_checkpoint(FULL);")

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. Database file
                zipf.write(DB_PATH, arcname=DB_PATH.name)

                # 2. School Settings & Preferences
                settings_file = APP_DIR / "school_settings.json"
                if settings_file.exists():
                    zipf.write(settings_file, arcname=settings_file.name)

                prefs_file = APP_DIR / "app_preferences.json"
                if prefs_file.exists():
                    zipf.write(prefs_file, arcname=prefs_file.name)

                # 3. Recent logs
                log_file = APP_DIR / "logs" / "app.log"
                if log_file.exists():
                    zipf.write(log_file, arcname="logs/app.log")

            file_size_mb = f"{backup_path.stat().st_size / (1024 * 1024):.2f} MB"

            # Log to DB
            user = AuthController.get_current_user()
            user_id = user.id if user else None

            history = BackupHistory(
                filename=backup_filename,
                file_size=file_size_mb,
                backup_type=backup_type,
                status="Success"
            )
            audit = AuditLog(
                user_id=user_id,
                action="CREATE_BACKUP",
                details=f"Created {backup_type} backup: {backup_filename} ({file_size_mb})"
            )
            db.add_all([history, audit])
            db.commit()

            logger.info(f"Database backup created successfully: {backup_path}")
            return True, f"Backup created successfully: {backup_filename}", str(backup_path)
        except Exception as e:
            db.rollback()
            logger.error(f"Backup creation error: {e}", exc_info=True)
            return False, f"Backup failed: {str(e)}", ""
        finally:
            db.close()

    @staticmethod
    def get_backup_preview(backup_zip_path: str) -> Dict[str, Any]:
        """Inspects a ZIP backup file and returns metadata preview."""
        zip_path = Path(backup_zip_path)
        if not zip_path.exists() or not zip_path.name.endswith(".zip"):
            return {"valid": False, "message": "File does not exist or is not a .zip archive."}

        try:
            stat = zip_path.stat()
            size_mb = f"{stat.st_size / (1024 * 1024):.2f} MB"
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                has_db = "school_fee.db" in file_list
                has_settings = "school_settings.json" in file_list or "app_preferences.json" in file_list

            return {
                "valid": has_db,
                "filename": zip_path.name,
                "path": str(zip_path),
                "size": size_mb,
                "date": mod_time,
                "has_db": has_db,
                "has_settings": has_settings,
                "contents": ", ".join(file_list),
                "message": "Valid backup package ready for restore." if has_db else "Corrupted backup (school_fee.db missing)."
            }
        except Exception as e:
            return {"valid": False, "message": f"Corrupted zip archive: {str(e)}"}

    @staticmethod
    def restore_backup(backup_zip_path: str) -> Tuple[bool, str]:
        """
        Verifies and restores database from a ZIP backup file.
        Performs an automatic safety backup of current database first.
        """
        preview = BackupService.get_backup_preview(backup_zip_path)
        if not preview.get("valid"):
            return False, preview.get("message", "Invalid backup file.")

        zip_path = Path(backup_zip_path)
        try:
            # Step 1: Automatic Safety Backup of current DB
            safety_success, safety_msg, _ = BackupService.create_backup(backup_type="Safety_PreRestore")
            if not safety_success:
                return False, f"Failed to create pre-restore safety backup: {safety_msg}"

            # Step 2: Extract to temp folder & check SQLite integrity
            temp_extract = BACKUP_DIR / "temp_restore"
            temp_extract.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_extract)

            extracted_db = temp_extract / "school_fee.db"

            # SQLite integrity check
            with sqlite3.connect(str(extracted_db)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA quick_check;")
                res = cursor.fetchone()
                if not res or res[0] != "ok":
                    shutil.rmtree(temp_extract, ignore_errors=True)
                    return False, f"Database integrity check failed: {res[0] if res else 'Unknown error'}"

            # Step 3: Close existing SQLAlchemy connections
            SessionLocal.remove()
            engine.dispose()

            # Step 4: Overwrite active database
            shutil.copy2(extracted_db, DB_PATH)

            # Restore settings/preferences if present
            ext_settings = temp_extract / "school_settings.json"
            if ext_settings.exists():
                shutil.copy2(ext_settings, APP_DIR / "school_settings.json")

            ext_prefs = temp_extract / "app_preferences.json"
            if ext_prefs.exists():
                shutil.copy2(ext_prefs, APP_DIR / "app_preferences.json")

            shutil.rmtree(temp_extract, ignore_errors=True)

            logger.info(f"Successfully restored database from: {zip_path.name}")
            return True, f"Database restored successfully from '{zip_path.name}'. App session refreshed."
        except Exception as e:
            logger.error(f"Restore database error: {e}", exc_info=True)
            return False, f"Restore failed: {str(e)}"

    @staticmethod
    def check_and_run_auto_backup() -> Tuple[bool, str]:
        """Checks auto-backup settings frequency and retention limits, executing backup if due."""
        from controllers.settings_controller import SettingsController
        prefs = SettingsController.get_app_preferences()

        if not prefs.get("auto_backup_enabled", True):
            return False, "Auto backup is disabled in settings."

        freq = prefs.get("auto_backup_frequency", "Daily")
        retention = prefs.get("backup_retention", "10")

        # Determine if backup is due
        backups = sorted(BACKUP_DIR.glob("school_fee_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        is_due = False

        if not backups:
            is_due = True
        else:
            last_time = datetime.fromtimestamp(backups[0].stat().st_mtime)
            now = datetime.now()
            if freq == "Daily" and (now - last_time) >= timedelta(days=1):
                is_due = True
            elif freq == "Weekly" and (now - last_time) >= timedelta(days=7):
                is_due = True
            elif freq == "Monthly" and (now - last_time) >= timedelta(days=30):
                is_due = True

        res_msg = "No auto backup due."
        if is_due:
            success, msg, _ = BackupService.create_backup(backup_type="Auto")
            res_msg = msg if success else f"Auto backup failed: {msg}"

        # Enforce retention policy
        BackupService.enforce_retention_policy(retention)

        return True, res_msg

    @staticmethod
    def enforce_retention_policy(retention: str):
        """Purges oldest backup ZIP files if count exceeds retention limit."""
        if retention == "Unlimited":
            return

        try:
            limit = int(retention)
            backups = sorted(BACKUP_DIR.glob("school_fee_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
            if len(backups) > limit:
                for b_file in backups[limit:]:
                    try:
                        b_file.unlink()
                        logger.info(f"Purged old backup under retention policy ({retention}): {b_file.name}")
                    except Exception:
                        pass
        except ValueError:
            pass

    # ---------------- DATABASE MAINTENANCE TOOLS ----------------
    @staticmethod
    def optimize_database() -> Tuple[bool, str]:
        """Executes SQLite VACUUM and ANALYZE optimization."""
        if not DB_PATH.exists():
            return False, "Database file missing."

        try:
            SessionLocal.remove()
            engine.dispose()

            with sqlite3.connect(str(DB_PATH)) as conn:
                conn.execute("VACUUM;")
                conn.execute("ANALYZE;")

            size_mb = f"{DB_PATH.stat().st_size / (1024 * 1024):.2f} MB"
            logger.info("Executed database VACUUM and ANALYZE optimization.")
            return True, f"Database optimized successfully (`VACUUM` & `ANALYZE` completed).\nCurrent DB Size: {size_mb}"
        except Exception as e:
            logger.error(f"Database optimization error: {e}", exc_info=True)
            return False, f"Optimization error: {str(e)}"

    @staticmethod
    def repair_database() -> Tuple[bool, str]:
        """Executes SQLite REINDEX database repair."""
        if not DB_PATH.exists():
            return False, "Database file missing."

        try:
            SessionLocal.remove()
            engine.dispose()

            with sqlite3.connect(str(DB_PATH)) as conn:
                conn.execute("REINDEX;")

            logger.info("Executed database REINDEX repair.")
            return True, "Database indices rebuilt successfully (`REINDEX` completed)."
        except Exception as e:
            logger.error(f"Database repair error: {e}", exc_info=True)
            return False, f"Repair error: {str(e)}"

    @staticmethod
    def verify_database_integrity() -> Tuple[bool, str]:
        """Executes PRAGMA integrity_check on active database."""
        if not DB_PATH.exists():
            return False, "Database file missing."

        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                res = cursor.fetchall()
                results_str = "\n".join(r[0] for r in res)

            logger.info("Executed PRAGMA integrity_check.")
            return True, f"Database Integrity Check Results:\n{results_str}"
        except Exception as e:
            logger.error(f"Database integrity verification error: {e}", exc_info=True)
            return False, f"Integrity check error: {str(e)}"
