"""
SQLAlchemy Engine & Database Session Initialization.
Configures SQLite foreign key pragmas and expire_on_commit=False for thread safety.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from config.app_config import DATABASE_URL, DB_PATH
from utils.logger import logger

# SQLite foreign key constraint enforcer
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=MEMORY;")
    except Exception:
        pass
    finally:
        cursor.close()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Prevents DetachedInstanceError on session close
    bind=engine
))

def get_db():
    """Provides a database session context."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def run_migrations():
    """Performs safe schema migrations on existing SQLite databases."""
    import sqlite3
    if not DB_PATH.exists():
        return
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            
            # Check receipts columns
            cursor.execute("PRAGMA table_info(receipts);")
            receipt_cols = {row[1] for row in cursor.fetchall()}
            
            if "paid_amount" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN paid_amount FLOAT DEFAULT 0.0;")
            if "due_amount" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN due_amount FLOAT DEFAULT 0.0;")
            if "utr_number" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN utr_number VARCHAR(100);")
            if "cheque_number" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN cheque_number VARCHAR(50);")
            if "cheque_date" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN cheque_date DATE;")
            if "bank_name" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN bank_name VARCHAR(100);")
            if "payment_date" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN payment_date DATE;")

            # Check students columns
            cursor.execute("PRAGMA table_info(students);")
            student_cols = {row[1] for row in cursor.fetchall()}
            if "course" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN course VARCHAR(100);")

            # Check audit_logs columns
            cursor.execute("PRAGMA table_info(audit_logs);")
            audit_cols = {row[1] for row in cursor.fetchall()}
            if "module" not in audit_cols:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN module VARCHAR(50);")
            if "status" not in audit_cols:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN status VARCHAR(20) DEFAULT 'Success';")
            if "machine_name" not in audit_cols:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN machine_name VARCHAR(100);")

            # Data backfill for legacy V1.0 records
            cursor.execute("UPDATE receipts SET paid_amount = total_amount WHERE paid_amount IS NULL OR paid_amount = 0.0;")
            cursor.execute("UPDATE receipts SET due_amount = 0.0 WHERE due_amount IS NULL;")
            conn.commit()
            logger.info("Executed database schema migrations successfully.")
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)

def init_db():
    """Imports all models and initializes database tables."""
    from models.base import Base
    import models.student
    import models.fee_category
    import models.receipt
    import models.user
    import models.settings
    import models.audit

    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        run_migrations()
        logger.info(f"Database initialized successfully at: {DB_PATH}")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        raise e
