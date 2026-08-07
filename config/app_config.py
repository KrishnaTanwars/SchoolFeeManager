"""
Application Configuration and Constants for School Fee Management System v1.0.
"""

import os
import sys
from pathlib import Path

# Base Paths
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = BASE_DIR

# Base Storage Directory Selection with Writable Fallback
def _get_writable_base(app_dir: Path) -> Path:
    """Returns app_dir if writable, otherwise falls back to %LOCALAPPDATA%/SchoolFeeManager."""
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
        test_file = app_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        return app_dir
    except Exception:
        fallback = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "SchoolFeeManager"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

WRITABLE_BASE = _get_writable_base(APP_DIR)

# Storage & Output Directories
IS_VERCEL = bool(os.environ.get("VERCEL"))
if IS_VERCEL:
    TMP_BASE = Path("/tmp")
    DATA_DIR = TMP_BASE / "database"
    LOG_DIR = TMP_BASE / "logs"
    BACKUP_DIR = TMP_BASE / "backup"
    EXPORTS_DIR = TMP_BASE / "exports"
else:
    DATA_DIR = WRITABLE_BASE / "database"
    LOG_DIR = WRITABLE_BASE / "logs"
    BACKUP_DIR = WRITABLE_BASE / "backup"
    EXPORTS_DIR = WRITABLE_BASE / "exports"

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"

for d in [DATA_DIR, LOG_DIR, BACKUP_DIR, EXPORTS_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# Database Config
DB_PATH = DATA_DIR / "school_fee.db"

# Copy initial seed database to /tmp if on Vercel and DB doesn't exist yet
if IS_VERCEL and not DB_PATH.exists():
    import shutil
    seed_db = BASE_DIR / "database" / "school_fee.db"
    if seed_db.exists():
        try:
            shutil.copy2(seed_db, DB_PATH)
        except Exception:
            pass

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Application Metadata
APP_NAME = "School Fee Management System"
APP_VERSION = "1.6.0"
COMPANY_NAME = "SmartSchool Software Solutions"

# Default Themes & Colors
DEFAULT_THEME = "Professional Navy"
PRIMARY_COLOR = "#1e3a8a"
SECONDARY_COLOR = "#0284c7"
ACCENT_COLOR = "#10b981"
BACKGROUND_COLOR = "#f8fafc"
TEXT_COLOR = "#0f172a"

# Default Receipt Settings
DEFAULT_RECEIPT_PREFIX = "REC/"
DEFAULT_CURRENCY_SYMBOL = "₹"
