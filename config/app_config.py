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

# Base Storage Directory Selection with Portable Override and AppData Fallback
IS_PORTABLE = (APP_DIR / ".portable").exists() or "--portable" in sys.argv

def _get_writable_base(app_dir: Path) -> Path:
    """Returns app_dir if portable mode or writable non-Program Files, otherwise %APPDATA%/EduLedger/SchoolFeeERP."""
    if IS_PORTABLE:
        return app_dir
    
    # Check if app_dir is inside Program Files or not writable
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    pf_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    is_in_pf = str(app_dir).lower().startswith(pf.lower()) or str(app_dir).lower().startswith(pf_x86.lower())
    
    if not is_in_pf:
        try:
            app_dir.mkdir(parents=True, exist_ok=True)
            test_file = app_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            return app_dir
        except Exception:
            pass
            
    app_data = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    fallback = Path(app_data) / "EduLedger" / "SchoolFeeERP"
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
    SETTINGS_DIR = TMP_BASE / "settings"
    REPORTS_DIR = TMP_BASE / "reports"
    CACHE_DIR = TMP_BASE / "cache"
    TEMP_DIR = TMP_BASE / "temp"
else:
    DATA_DIR = WRITABLE_BASE / "database"
    LOG_DIR = WRITABLE_BASE / "logs"
    BACKUP_DIR = WRITABLE_BASE / "backup"
    EXPORTS_DIR = WRITABLE_BASE / "exports"
    SETTINGS_DIR = WRITABLE_BASE / "settings"
    REPORTS_DIR = WRITABLE_BASE / "reports"
    CACHE_DIR = WRITABLE_BASE / "cache"
    TEMP_DIR = WRITABLE_BASE / "temp"
    STUDENT_PHOTOS_DIR = WRITABLE_BASE / "student_photos"

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"

for d in [DATA_DIR, LOG_DIR, BACKUP_DIR, EXPORTS_DIR, SETTINGS_DIR, REPORTS_DIR, CACHE_DIR, TEMP_DIR, STUDENT_PHOTOS_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# Database Config
DB_PATH = DATA_DIR / "school_fee.db"

# Copy initial seed database if DB doesn't exist yet
if not DB_PATH.exists():
    import shutil
    candidate_seeds = [
        BASE_DIR / "database" / "school_fee.db",
        APP_DIR / "database" / "school_fee.db",
    ]
    for seed_db in candidate_seeds:
        if seed_db.exists() and seed_db != DB_PATH:
            try:
                shutil.copy2(seed_db, DB_PATH)
                break
            except Exception:
                pass

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Read Version String
def _load_version() -> str:
    vfile = BASE_DIR / "Version.txt"
    if not vfile.exists():
        vfile = APP_DIR / "Version.txt"
    if vfile.exists():
        try:
            return vfile.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return "3.4.0"

# Application Metadata
APP_NAME = "School Fee ERP"
APP_VERSION = _load_version()
COMPANY_NAME = "EduLedger"
PUBLISHER_NAME = "EduLedger Software Solutions"

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

