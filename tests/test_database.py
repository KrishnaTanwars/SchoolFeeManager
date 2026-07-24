"""
Unit Tests for Database Initialization, ORM Models & Relationships.
"""

import unittest
from config.database import init_db, get_db
from models.user import User
from models.fee_category import FeeCategory
from services.db_seed import seed_initial_data

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()
        seed_initial_data()

    def test_database_connection_and_seed(self):
        db = get_db()
        try:
            admin_user = db.query(User).filter(User.username == "admin").first()
            self.assertIsNotNone(admin_user)
            self.assertEqual(admin_user.role, "Admin")

            fee_cats = db.query(FeeCategory).all()
            self.assertGreaterEqual(len(fee_cats), 10)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
