"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Constants
Purpose   : Application Wide Constants
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from pathlib import Path

# =========================================================
# Application Information
# =========================================================

APP_NAME = "Civil Estimate Suite Pro"

APP_VERSION = "4.0.0"

APP_AUTHOR = "Moula Bakhsh"

APP_COMPANY = "Civil Estimate Suite"

DATABASE_NAME = "civil_estimate_suite.db"

# =========================================================
# Directories
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = ROOT_DIR / "assets"

DATABASE_DIR = ROOT_DIR / "database"

LOG_DIR = ROOT_DIR / "logs"

REPORT_DIR = ROOT_DIR / "reports"

EXPORT_DIR = ROOT_DIR / "exports"

CONFIG_DIR = ROOT_DIR / "config"

BACKUP_DIR = ROOT_DIR / "backup"

TEMP_DIR = ROOT_DIR / "temp"

# =========================================================
# Files
# =========================================================

DATABASE_FILE = DATABASE_DIR / DATABASE_NAME

LOG_FILE = LOG_DIR / "application.log"

SETTINGS_FILE = CONFIG_DIR / "settings.json"

# =========================================================
# UI
# =========================================================

WINDOW_WIDTH = 1400

WINDOW_HEIGHT = 850

MIN_WIDTH = 1200

MIN_HEIGHT = 700

# =========================================================
# Theme
# =========================================================

DEFAULT_THEME = "blue"

DEFAULT_MODE = "light"

# =========================================================
# Database
# =========================================================

SQLITE_TIMEOUT = 30

# =========================================================
# Reports
# =========================================================

DEFAULT_EXCEL_NAME = "Estimate_Report.xlsx"

DEFAULT_PDF_NAME = "Estimate_Report.pdf"

# =========================================================
# Status
# =========================================================

STATUS_PLANNING = "Planning"

STATUS_RUNNING = "Running"

STATUS_COMPLETED = "Completed"

STATUS_HOLD = "On Hold"

STATUS_CANCELLED = "Cancelled"

PROJECT_STATUS = (
    STATUS_PLANNING,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_HOLD,
    STATUS_CANCELLED,
)