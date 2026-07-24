"""
Database Backup & Restore Service.
Creates timestamped ZIP database backups and verifies SQLite integrity before restore.
"""

import shutil
import zipfile
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional
from config.app_config import DB_PATH, BACKUP_DIR
from config.database import get_db, SessionLocal, engine
from models.audit import BackupHistory, AuditLog
from controllers.auth_controller import AuthController
from utils.logger import logger

class BackupService:
    @staticmethod
    def create_backup(dest_dir: Optional[Path] = None) -> Tuple[bool, str, str]:
        """
        Creates a timestamped backup ZIP of school_fee.db.
        Returns: (success: bool, message: str, backup_filename: str)
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
                zipf.write(DB_PATH, arcname=DB_PATH.name)

            file_size_mb = f"{backup_path.stat().st_size / (1024 * 1024):.2f} MB"

            # Log to DB
            user = AuthController.get_current_user()
            user_id = user.id if user else None
            
            history = BackupHistory(
                filename=backup_filename,
                file_size=file_size_mb,
                backup_type="Manual",
                status="Success"
            )
            audit = AuditLog(
                user_id=user_id,
                action="CREATE_BACKUP",
                details=f"Created database backup: {backup_filename} ({file_size_mb})"
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
    def restore_backup(backup_zip_path: str) -> Tuple[bool, str]:
        """
        Verifies and restores database from a ZIP backup file.
        Performs an automatic safety backup of current database first.
        """
        zip_path = Path(backup_zip_path)
        if not zip_path.exists() or not zip_path.name.endswith(".zip"):
            return False, "Invalid backup zip file."

        try:
            # Step 1: Automatic Safety Backup of current DB
            safety_success, safety_msg, _ = BackupService.create_backup()
            if not safety_success:
                return False, f"Failed to create pre-restore safety backup: {safety_msg}"

            # Step 2: Extract to temp folder & check SQLite integrity
            temp_extract = BACKUP_DIR / "temp_restore"
            temp_extract.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_extract)

            extracted_db = temp_extract / "school_fee.db"
            if not extracted_db.exists():
                shutil.rmtree(temp_extract, ignore_errors=True)
                return False, "Corrupted backup archive (school_fee.db not found inside zip)."

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
            shutil.rmtree(temp_extract, ignore_errors=True)

            logger.info(f"Successfully restored database from: {zip_path.name}")
            return True, f"Database restored successfully from '{zip_path.name}'. App will refresh session."
        except Exception as e:
            logger.error(f"Restore database error: {e}", exc_info=True)
            return False, f"Restore failed: {str(e)}"
