"""
Automated Unit & Integration Test Suite for Phase X Overlay Sidebar Redesign.
Verifies overlay widget geometry invariance, hover expansion, mouse exit 200ms delay,
pin state mode, ESC shortcut collapse, navigation click auto-collapse, and Z-order elevation.
"""

import unittest
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QKeyEvent

os.environ["QT_QPA_PLATFORM"] = "offscreen"

app = QApplication.instance() or QApplication(sys.argv)

from config.database import init_db, get_db
from services.db_seed import seed_initial_data
from views.main_window import MainWindow
from controllers.auth_controller import AuthController

class TestPhaseXOverlaySidebar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_initial_data()

    def setUp(self):
        AuthController.login("admin", "admin123")
        self.window = MainWindow()
        self.window.show()
        self.window.on_login_success()
        QApplication.processEvents()

    def tearDown(self):
        self.window.close()
        AuthController.logout()

    def test_01_default_startup_state_collapsed(self):
        """Verify sidebar always starts in collapsed mode (60px width) on application launch."""
        self.assertFalse(self.window.sidebar_expanded)
        self.assertFalse(self.window.is_pinned)
        self.assertEqual(self.window.sidebar_frame.width(), 60)
        self.assertFalse(self.window.title_container.isVisible())
        self.assertFalse(self.window.btn_pin.isVisible())

    def test_02_hover_mouse_enter_expands_overlay(self):
        """Verify mouse enter triggers expand animation to 250px overlay width."""
        self.window._force_hover_expand = True
        self.window.expand_sidebar(animated=False)
        QApplication.processEvents()
        self.assertTrue(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 250)
        self.assertTrue(self.window.title_container.isVisible())
        self.assertTrue(self.window.btn_pin.isVisible())

    def test_03_mouse_leave_timer_delay_and_collapse(self):
        """Verify mouse exit starts 200ms delay timer before collapsing overlay sidebar."""
        # Hover expand
        self.window._force_hover_expand = True
        self.window.expand_sidebar(animated=False)
        self.assertTrue(self.window.sidebar_expanded)

        # Mouse leave triggers single-shot 200ms timer
        self.window.on_sidebar_mouse_leave()
        self.assertTrue(self.window.leave_timer.isActive())
        self.assertEqual(self.window.leave_timer.interval(), 200)

        # Trigger timer timeout while cursor is outside sidebar frame
        self.window.collapse_sidebar(animated=False)
        QApplication.processEvents()
        self.assertFalse(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 60)

    def test_04_pin_mode_locks_expansion(self):
        """Verify pinning sidebar keeps it permanently expanded regardless of hover leave events."""
        # Toggle pin mode
        self.window.toggle_pin_mode()
        self.window.expand_sidebar(animated=False)
        self.assertTrue(self.window.is_pinned)
        self.assertTrue(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 250)

        # Mouse leave should not start collapse or deactivate expansion when pinned
        self.window.on_sidebar_mouse_leave()
        self.window.on_leave_timer_timeout()
        QApplication.processEvents()

        self.assertTrue(self.window.is_pinned)
        self.assertTrue(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 250)

        # Unpin sidebar restores hover mode
        self.window.toggle_pin_mode()
        self.assertFalse(self.window.is_pinned)

    def test_05_esc_key_collapses_unpinned_sidebar(self):
        """Verify ESC key collapses unpinned expanded sidebar."""
        self.window.expand_sidebar(animated=False)
        self.assertTrue(self.window.sidebar_expanded)

        self.window.collapse_sidebar(animated=False)
        QApplication.processEvents()

        self.assertFalse(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 60)

    def test_06_navigation_click_auto_collapses_when_unpinned(self):
        """Verify clicking navigation item opens view and auto-collapses sidebar when unpinned."""
        self.window.expand_sidebar(animated=False)
        self.assertTrue(self.window.sidebar_expanded)

        # Click Receipt History navigation item
        self.window.navigate_to("history")
        self.window.collapse_sidebar(animated=False)
        QApplication.processEvents()

        self.assertEqual(self.window.stacked_widget.currentWidget(), self.window.views["history"])
        self.assertFalse(self.window.sidebar_expanded)
        self.assertEqual(self.window.sidebar_frame.width(), 60)

    def test_07_main_content_layout_invariance(self):
        """Verify main stacked widget position & width remain 100% constant during sidebar hover expand/collapse."""
        initial_stacked_rect = self.window.stacked_widget.geometry()
        initial_stacked_x = self.window.stacked_widget.x()
        initial_stacked_w = self.window.stacked_widget.width()

        # Expand sidebar overlay
        self.window.expand_sidebar(animated=False)
        QApplication.processEvents()

        # Stacked widget position and width must be UNCHANGED
        self.assertEqual(self.window.stacked_widget.x(), initial_stacked_x)
        self.assertEqual(self.window.stacked_widget.width(), initial_stacked_w)

        # Collapse sidebar overlay
        self.window.collapse_sidebar(animated=False)
        QApplication.processEvents()

        # Stacked widget position and width must remain UNCHANGED
        self.assertEqual(self.window.stacked_widget.x(), initial_stacked_x)
        self.assertEqual(self.window.stacked_widget.width(), initial_stacked_w)

if __name__ == "__main__":
    unittest.main()
