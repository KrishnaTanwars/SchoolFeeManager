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

    def test_migration_course_category_addition(self):
        import sqlite3, tempfile, os
        from pathlib import Path
        from unittest.mock import patch

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db")
        os.close(tmp_fd)
        tmp_db_path = Path(tmp_path)

        try:
            with sqlite3.connect(str(tmp_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        admission_no VARCHAR(50) UNIQUE,
                        name VARCHAR(100),
                        father_name VARCHAR(100),
                        mobile VARCHAR(15),
                        academic_session VARCHAR(20)
                    );
                """)
                cursor.execute("""
                    CREATE TABLE receipts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        receipt_no VARCHAR(50) UNIQUE,
                        total_amount FLOAT
                    );
                """)
                cursor.execute("""
                    CREATE TABLE fee_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(150)
                    );
                """)
                cursor.execute("""
                    CREATE TABLE school_information (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                    );
                """)
                cursor.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                    );
                """)
                cursor.execute("""
                    CREATE TABLE backup_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                    );
                """)
                conn.commit()

            with patch("config.database.DB_PATH", tmp_db_path):
                from config.database import run_migrations
                run_migrations()

            with sqlite3.connect(str(tmp_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(students);")
                cols = {row[1] for row in cursor.fetchall()}
                self.assertIn("course_category", cols)
        finally:
            try:
                if tmp_db_path.exists():
                    os.remove(tmp_db_path)
            except PermissionError:
                pass

if __name__ == "__main__":
    unittest.main()
