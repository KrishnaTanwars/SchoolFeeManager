"""
Database Seed Service.
Seeds initial default values for Users, Fee Categories, School Info, and Academic Sessions.
"""

from config.database import get_db
from models.user import User
from models.fee_category import FeeCategory
from models.settings import SchoolInformation, AcademicSession
from utils.security import hash_password
from utils.logger import logger

def seed_initial_data():
    db = get_db()
    try:
        # Seed Users
        if db.query(User).count() == 0:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="System Administrator",
                role="Admin",
                status="Active"
            )
            operator_user = User(
                username="operator",
                password_hash=hash_password("operator123"),
                full_name="Fee Operator",
                role="Operator",
                status="Active"
            )
            db.add_all([admin_user, operator_user])
            logger.info("Seeded default users (admin / operator).")

        # Seed School Information
        if db.query(SchoolInformation).count() == 0:
            school_info = SchoolInformation(
                school_name="DPS International Public School",
                address="Plot 12, Sector 5, RK Puram, New Delhi - 110022",
                phone="+91 98765 43210, 011-26123456",
                email="accounts@dps school.edu.in",
                website="www.dpsschool.edu.in",
                logo_path="assets/school_logo.png",
                receipt_prefix="REC/2025/",
                receipt_footer="Fee once paid is non-refundable. Thank you!",
                current_session="2025-2026"
            )
            db.add(school_info)
            logger.info("Seeded default school information.")

        # Seed Academic Sessions
        if db.query(AcademicSession).count() == 0:
            s1 = AcademicSession(session_name="2025-2026", is_current=True)
            s2 = AcademicSession(session_name="2024-2025", is_current=False)
            s3 = AcademicSession(session_name="2026-2027", is_current=False)
            db.add_all([s1, s2, s3])
            logger.info("Seeded default academic sessions.")

        # Seed Fee Categories (Delegates to FeeController seed helper)
        from controllers.fee_controller import FeeController
        FeeController.seed_default_fee_heads()

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}", exc_info=True)
    finally:
        db.close()
