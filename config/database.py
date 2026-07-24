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
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA journal_mode=WAL;")
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
        logger.info(f"Database initialized successfully at: {DB_PATH}")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        raise e
