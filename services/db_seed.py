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
                receipt_prefix="REC/2024/",
                receipt_footer="Fee once paid is non-refundable. Thank you!",
                current_session="2024-2025"
            )
            db.add(school_info)
            logger.info("Seeded default school information.")

        # Seed Academic Sessions
        if db.query(AcademicSession).count() == 0:
            s1 = AcademicSession(session_name="2024-2025", is_current=True)
            s2 = AcademicSession(session_name="2025-2026", is_current=False)
            db.add_all([s1, s2])
            logger.info("Seeded default academic sessions.")

        # Seed Fee Categories
        if db.query(FeeCategory).count() == 0:
            default_categories = [
                FeeCategory(name="Tuition Fee", code="TF", default_amount=2500.0, is_active=True, description="Monthly Tuition Fee"),
                FeeCategory(name="Admission Fee", code="AF", default_amount=5000.0, is_active=True, description="One-time Admission Fee"),
                FeeCategory(name="Development Fee", code="DF", default_amount=1500.0, is_active=True, description="Annual School Development Fee"),
                FeeCategory(name="Computer & IT Fee", code="CF", default_amount=600.0, is_active=True, description="Computer Lab & Digital Class Fee"),
                FeeCategory(name="Sports & Activity Fee", code="SF", default_amount=400.0, is_active=True, description="Sports, Games & Cultural Activities"),
                FeeCategory(name="Library Fee", code="LF", default_amount=300.0, is_active=True, description="Library Books & Reading Room"),
                FeeCategory(name="Laboratory Fee", code="LAB", default_amount=800.0, is_active=True, description="Physics, Chemistry, Biology Labs"),
                FeeCategory(name="Transport Fee", code="TR", default_amount=1200.0, is_active=True, description="Monthly Bus / Van Conveyance"),
                FeeCategory(name="Hostel Fee", code="HF", default_amount=4500.0, is_active=True, description="Boarding & Lodging Fee"),
                FeeCategory(name="Examination Fee", code="EX", default_amount=500.0, is_active=True, description="Term / Semester Exam Fee"),
                FeeCategory(name="Identity Card & Diary", code="ID", default_amount=150.0, is_active=True, description="Student ID Card & School Diary"),
                FeeCategory(name="Fine / Late Payment", code="FN", default_amount=100.0, is_active=True, description="Late Payment Penalty"),
                FeeCategory(name="Miscellaneous", code="MISC", default_amount=200.0, is_active=True, description="Other General Charges"),
            ]
            db.add_all(default_categories)
            logger.info("Seeded 13 default fee categories.")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}", exc_info=True)
    finally:
        db.close()
