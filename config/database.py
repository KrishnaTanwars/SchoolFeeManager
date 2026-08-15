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
            if "course" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN course VARCHAR(100);")
            if "branch" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN branch VARCHAR(100);")
            if "academic_year" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN academic_year VARCHAR(50);")
            if "semester" not in receipt_cols:
                cursor.execute("ALTER TABLE receipts ADD COLUMN semester VARCHAR(50);")

            # Check students columns
            cursor.execute("PRAGMA table_info(students);")
            student_cols = {row[1] for row in cursor.fetchall()}
            if "course" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN course VARCHAR(100);")
            if "branch" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN branch VARCHAR(100);")
            if "year" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN year VARCHAR(50);")
            if "semester" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN semester VARCHAR(50);")
            if "date_of_birth" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN date_of_birth DATE;")
            if "aadhaar_number" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN aadhaar_number VARCHAR(12);")
            if "photo_path" not in student_cols:
                cursor.execute("ALTER TABLE students ADD COLUMN photo_path VARCHAR(255);")

            # Check fee_categories columns and indexes
            cursor.execute("PRAGMA table_info(fee_categories);")
            fee_cat_cols = {row[1] for row in cursor.fetchall()}
            if "course" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN course VARCHAR(100) DEFAULT 'All';")
            if "branch" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN branch VARCHAR(100) DEFAULT 'All';")
            if "academic_year" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN academic_year VARCHAR(50) DEFAULT 'All';")
            if "semester" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN semester VARCHAR(50) DEFAULT 'All';")
            if "academic_session" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN academic_session VARCHAR(20) DEFAULT 'All';")
            if "created_at" not in fee_cat_cols:
                cursor.execute("ALTER TABLE fee_categories ADD COLUMN created_at DATETIME;")

            # Remove legacy unique constraint on name if present
            cursor.execute("PRAGMA index_list(fee_categories);")
            indexes = cursor.fetchall()
            has_unique_name = False
            for idx in indexes:
                idx_name, is_unique = idx[1], idx[2]
                if is_unique:
                    cursor.execute(f"PRAGMA index_info('{idx_name}');")
                    cols = [info[2] for info in cursor.fetchall()]
                    if cols == ['name']:
                        has_unique_name = True
                        break

            if has_unique_name:
                cursor.execute("""
                    CREATE TABLE fee_categories_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(150) NOT NULL,
                        course VARCHAR(20) NOT NULL DEFAULT 'UG',
                        default_amount FLOAT NOT NULL DEFAULT 0.0,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        description VARCHAR(255),
                        created_at DATETIME
                    );
                """)
                cursor.execute("""
                    INSERT INTO fee_categories_new (id, name, course, default_amount, is_active, description, created_at)
                    SELECT id, name, COALESCE(course, 'UG'), default_amount, is_active, description, created_at FROM fee_categories;
                """)
                cursor.execute("DROP TABLE fee_categories;")
                cursor.execute("ALTER TABLE fee_categories_new RENAME TO fee_categories;")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_fee_categories_name ON fee_categories (name);")
                cursor.execute("CREATE INDEX IF NOT EXISTS ix_fee_categories_course ON fee_categories (course);")

            # Check school_information columns
            cursor.execute("PRAGMA table_info(school_information);")
            school_cols = {row[1] for row in cursor.fetchall()}
            if "city" not in school_cols:
                cursor.execute("ALTER TABLE school_information ADD COLUMN city VARCHAR(100) DEFAULT 'New Delhi';")
            if "state" not in school_cols:
                cursor.execute("ALTER TABLE school_information ADD COLUMN state VARCHAR(100) DEFAULT 'Delhi';")
            if "pin_code" not in school_cols:
                cursor.execute("ALTER TABLE school_information ADD COLUMN pin_code VARCHAR(20) DEFAULT '110001';")
            if "principal_name" not in school_cols:
                cursor.execute("ALTER TABLE school_information ADD COLUMN principal_name VARCHAR(100) DEFAULT 'Dr. A. K. Sharma';")

            # Check users columns
            cursor.execute("PRAGMA table_info(users);")
            user_cols = {row[1] for row in cursor.fetchall()}
            if "failed_attempts" not in user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;")

            # Check backup_history columns
            cursor.execute("PRAGMA table_info(backup_history);")
            backup_cols = {row[1] for row in cursor.fetchall()}
            if "created_by" not in backup_cols:
                cursor.execute("ALTER TABLE backup_history ADD COLUMN created_by VARCHAR(100) DEFAULT 'Administrator';")

            # Data backfill for legacy V1.0 records
            cursor.execute("UPDATE receipts SET paid_amount = total_amount WHERE paid_amount IS NULL OR paid_amount = 0.0;")
            cursor.execute("UPDATE receipts SET due_amount = 0.0 WHERE due_amount IS NULL;")
            conn.commit()
            logger.info("Executed database schema migrations successfully.")

            # Seed Default UG and PG Fee Heads
            try:
                from controllers.fee_controller import FeeController
                FeeController.seed_default_fee_heads()
            except Exception as seed_err:
                logger.warning(f"Default fee head seeding notice: {seed_err}")
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)

def init_db():
    """Imports all models and initializes database tables."""
    from models.base import Base
    import models.academic
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
