"""
Application Entry Point for School Fee Management System v1.0.
"""

import sys
import os
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QFile, QTextStream

from config.app_config import APP_NAME, APP_VERSION, STYLES_DIR
from config.database import init_db
from services.db_seed import seed_initial_data
from views.main_window import MainWindow
from utils.logger import logger

def uncaught_exception_handler(exctype, value, tb):
    """Global exception hook for catching uncaught application exceptions."""
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Uncaught Exception Crash: {err_msg}")
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Application Error")
    msg_box.setText("An unexpected error occurred. Details have been logged.")
    msg_box.setDetailedText(err_msg)
    msg_box.exec()

def main():
    sys.excepthook = uncaught_exception_handler

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Initialize Database & Seed Data
    try:
        init_db()
        seed_initial_data()
    except Exception as e:
        logger.critical(f"Failed DB setup: {e}", exc_info=True)
        QMessageBox.critical(None, "Database Initialization Failed", f"Database error: {str(e)}")
        sys.exit(1)

    # Load QSS Stylesheet
    qss_file = STYLES_DIR / "theme.qss"
    if qss_file.exists():
        with open(qss_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Loaded theme.qss stylesheet.")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
