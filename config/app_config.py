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

# Storage & Output Directories
DATA_DIR = APP_DIR / "database"
LOG_DIR = APP_DIR / "logs"
BACKUP_DIR = APP_DIR / "backup"
EXPORTS_DIR = APP_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"

for d in [DATA_DIR, LOG_DIR, BACKUP_DIR, EXPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Database Config
DB_PATH = DATA_DIR / "school_fee.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Application Metadata
APP_NAME = "School Fee Management System"
APP_VERSION = "1.0.0"
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
