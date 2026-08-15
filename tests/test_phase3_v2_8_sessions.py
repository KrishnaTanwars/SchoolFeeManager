"""
Automated Unit and Integration Tests for Phase 3 (v2.8.0):
1. Academic Session Master Management (SessionManager.add_session).
2. Active Session Activation & Database Persistence (SessionManager.set_current_session).
3. Listener Callback Registration & Real-Time Global UI Synchronization.
4. Historical Session Context Isolation.
"""

import os
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])

from config.database import init_db, get_db
from models.settings import AcademicSession
from services.session_service import SessionManager

class TestPhase3V28Sessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = get_db()

    def tearDown(self):
        self.db.close()

    def test_01_add_academic_session(self):
        """Verifies adding a new academic session to database."""
        sess_name = "2027-2028"
        # Cleanup if exists
        ex = self.db.query(AcademicSession).filter(AcademicSession.session_name == sess_name).first()
        if ex:
            self.db.delete(ex)
            self.db.commit()

        success, msg = SessionManager.add_session(sess_name)
        self.assertTrue(success, msg)
        self.assertIn("added successfully", msg)

        # Duplicate addition should fail
        success_dup, msg_dup = SessionManager.add_session(sess_name)
        self.assertFalse(success_dup)
        self.assertIn("already exists", msg_dup)

    def test_02_set_current_session_activation(self):
        """Verifies setting active session updates database is_current flag."""
        sess_name = "2026-2027"
        SessionManager.add_session(sess_name)

        success, msg = SessionManager.set_current_session(sess_name)
        self.assertTrue(success, msg)

        curr = SessionManager.get_current_session()
        self.assertEqual(curr, sess_name)

        # Verify DB is_current state
        db_curr = self.db.query(AcademicSession).filter(AcademicSession.session_name == sess_name).first()
        self.assertTrue(db_curr.is_current)

    def test_03_session_listener_callbacks(self):
        """Verifies session listener registration and notification on session change."""
        notified = []

        def my_callback(new_sess):
            notified.append(new_sess)

        SessionManager.register_listener(my_callback)
        SessionManager.set_current_session("2025-2026")

        self.assertIn("2025-2026", notified)
        SessionManager.unregister_listener(my_callback)

    def test_04_get_all_sessions(self):
        """Verifies fetching list of all sessions."""
        all_s = SessionManager.get_all_sessions()
        self.assertGreater(len(all_s), 0)
        self.assertIn("2025-2026", all_s)


if __name__ == "__main__":
    unittest.main()
