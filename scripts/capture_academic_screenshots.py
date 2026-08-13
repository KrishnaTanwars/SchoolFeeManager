"""
Automated Screenshot Capture Script for Phase X — Academic Structure Refactor (Semester & Year Based ERP).
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

app = QApplication.instance() or QApplication(sys.argv)

from config.database import init_db
from views.main_window import MainWindow
from controllers.auth_controller import AuthController

DOCS_SHOTS_DIR = BASE_DIR / "docs" / "screenshots"
DOCS_SHOTS_DIR.mkdir(parents=True, exist_ok=True)

def capture_widget(widget, filename):
    widget.repaint()
    QApplication.processEvents()
    pix = widget.grab()
    out_path = DOCS_SHOTS_DIR / filename
    pix.save(str(out_path), "PNG")
    print(f"Captured screenshot: {filename} -> {out_path}")

def run_capture():
    init_db()
    AuthController.login("admin", "admin123")

    win = MainWindow()
    win.resize(1366, 768)
    win.show()
    QApplication.processEvents()

    # 1. Student Directory View with Academic Filters
    win.navigate_to("students")
    QApplication.processEvents()
    capture_widget(win, "08_student_academic_directory.png")

    # 2. Fee Collection View
    win.navigate_to("receipt")
    QApplication.processEvents()
    capture_widget(win, "09_academic_fee_collection.png")

    # 3. Receipt History Ledger View
    win.navigate_to("history")
    QApplication.processEvents()
    capture_widget(win, "10_academic_receipt_history.png")

    win.close()
    print("ALL ACADEMIC SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run_capture()
