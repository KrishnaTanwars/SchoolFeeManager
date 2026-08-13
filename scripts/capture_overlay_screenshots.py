"""
Automated Screenshot Capture Script for Phase X Overlay Sidebar Redesign.
Captures 7 high-resolution screenshots verifying collapsed, expanded, pinned, and view overlay states.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

app = QApplication.instance() or QApplication(sys.argv)

from config.database import init_db
from services.db_seed import seed_initial_data
from views.main_window import MainWindow
from controllers.auth_controller import AuthController
DOCS_SHOTS_DIR = BASE_DIR / "docs" / "screenshots"
DOCS_SHOTS_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\tanwa\.gemini\antigravity-ide\brain\992387d7-95d3-47dd-ad32-a372d24bceb6\screenshots")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def capture(window, filename):
    QApplication.processEvents()
    pixmap = window.grab()
    
    out_path1 = DOCS_SHOTS_DIR / filename
    out_path2 = ARTIFACT_DIR / filename
    
    pixmap.save(str(out_path1), "PNG")
    pixmap.save(str(out_path2), "PNG")
    print(f"Captured screenshot: {filename} -> {out_path1}")

def run():
    init_db()
    seed_initial_data()
    AuthController.login("admin", "admin123")

    win = MainWindow()
    win.resize(1280, 800)
    win.show()
    win.on_login_success()
    QApplication.processEvents()

    # 1. Startup Collapsed
    win.collapse_sidebar(animated=False)
    capture(win, "01_startup_collapsed.png")

    # 2. Hover Expanded
    win.expand_sidebar(animated=False)
    capture(win, "02_hover_expanded.png")

    # 3. Pinned State
    win.toggle_pin_mode()
    capture(win, "03_pinned_state.png")
    win.toggle_pin_mode() # unpin

    # 4. Dashboard with Overlay
    win.navigate_to("dashboard")
    win.expand_sidebar(animated=False)
    capture(win, "04_dashboard_overlay.png")

    # 5. Fee Collection with Overlay
    win.navigate_to("receipt")
    win.expand_sidebar(animated=False)
    capture(win, "05_fee_collection_overlay.png")

    # 6. Receipt History with Overlay
    win.navigate_to("history")
    win.expand_sidebar(animated=False)
    capture(win, "06_receipt_history_overlay.png")

    # 7. Student Master with Overlay
    win.navigate_to("students")
    win.expand_sidebar(animated=False)
    capture(win, "07_student_master_overlay.png")

    win.close()
    print("ALL 7 SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
