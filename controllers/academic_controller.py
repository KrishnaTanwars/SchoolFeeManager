"""
AcademicController — Centralized Controller for Course, Branch, Academic Year, and Semester Masters.
"""

from typing import List, Dict, Any, Optional
from config.database import get_db
from models.academic import Course, Branch, AcademicYear, Semester
from utils.logger import logger

class AcademicController:
    
    DEFAULT_COURSES = [
        {"code": "BTECH", "name": "B.Tech", "course_type": "College", "duration_years": 4, "total_semesters": 8},
        {"code": "MBA", "name": "MBA", "course_type": "College", "duration_years": 2, "total_semesters": 4},
        {"code": "BCA", "name": "BCA", "course_type": "College", "duration_years": 3, "total_semesters": 6},
        {"code": "BBA", "name": "BBA", "course_type": "College", "duration_years": 3, "total_semesters": 6},
        {"code": "MCA", "name": "MCA", "course_type": "College", "duration_years": 2, "total_semesters": 4},
        {"code": "CLASS10", "name": "Class 10", "course_type": "School", "duration_years": 1, "total_semesters": 0},
    ]

    DEFAULT_BRANCHES = [
        {"code": "CSE", "name": "Computer Science", "course_code": "BTECH"},
        {"code": "ME", "name": "Mechanical Engineering", "course_code": "BTECH"},
        {"code": "IT", "name": "Information Technology", "course_code": "BTECH"},
        {"code": "FIN", "name": "Finance", "course_code": "MBA"},
        {"code": "HR", "name": "Human Resource", "course_code": "MBA"},
        {"code": "GEN", "name": "General", "course_code": None},
    ]

    DEFAULT_YEARS = [
        {"code": "Y1", "name": "1st Year", "order_no": 1},
        {"code": "Y2", "name": "2nd Year", "order_no": 2},
        {"code": "Y3", "name": "3rd Year", "order_no": 3},
        {"code": "Y4", "name": "4th Year", "order_no": 4},
        {"code": "Y5", "name": "5th Year", "order_no": 5},
    ]

    DEFAULT_SEMESTERS = [
        {"code": "SEM1", "name": "Semester 1", "order_no": 1},
        {"code": "SEM2", "name": "Semester 2", "order_no": 2},
        {"code": "SEM3", "name": "Semester 3", "order_no": 3},
        {"code": "SEM4", "name": "Semester 4", "order_no": 4},
        {"code": "SEM5", "name": "Semester 5", "order_no": 5},
        {"code": "SEM6", "name": "Semester 6", "order_no": 6},
        {"code": "SEM7", "name": "Semester 7", "order_no": 7},
        {"code": "SEM8", "name": "Semester 8", "order_no": 8},
    ]

    @classmethod
    def seed_academic_masters_if_empty(cls):
        """Ensures default Courses, Branches, Academic Years, and Semesters are present."""
        db = get_db()
        try:
            # Seed Courses
            if db.query(Course).count() == 0:
                for c in cls.DEFAULT_COURSES:
                    db.add(Course(**c))
                db.commit()

            # Seed Branches
            if db.query(Branch).count() == 0:
                for b in cls.DEFAULT_BRANCHES:
                    db.add(Branch(**b))
                db.commit()

            # Seed Years
            if db.query(AcademicYear).count() == 0:
                for y in cls.DEFAULT_YEARS:
                    db.add(AcademicYear(**y))
                db.commit()

            # Seed Semesters
            if db.query(Semester).count() == 0:
                for s in cls.DEFAULT_SEMESTERS:
                    db.add(Semester(**s))
                db.commit()
            logger.info("Academic master tables initialized successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding academic masters: {e}")

    @classmethod
    def get_courses(cls) -> List[str]:
        """Returns list of active course names."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            courses = db.query(Course).filter(Course.is_active == True).order_by(Course.id).all()
            return [c.name for c in courses]
        except Exception as e:
            logger.error(f"Error fetching courses: {e}")
            return [c["name"] for c in cls.DEFAULT_COURSES]

    @classmethod
    def get_branches(cls, course_name: Optional[str] = None) -> List[str]:
        """Returns list of branch names, optionally filtered by course."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            query = db.query(Branch).filter(Branch.is_active == True)
            branches = query.order_by(Branch.id).all()
            return [b.name for b in branches]
        except Exception as e:
            logger.error(f"Error fetching branches: {e}")
            return [b["name"] for b in cls.DEFAULT_BRANCHES]

    @classmethod
    def get_years(cls) -> List[str]:
        """Returns list of academic year names."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            years = db.query(AcademicYear).filter(AcademicYear.is_active == True).order_by(AcademicYear.order_no).all()
            return [y.name for y in years]
        except Exception as e:
            logger.error(f"Error fetching academic years: {e}")
            return [y["name"] for y in cls.DEFAULT_YEARS]

    @classmethod
    def get_semesters(cls, total_semesters: Optional[int] = None) -> List[str]:
        """Returns list of semester names (e.g. Semester 1 to Semester 8)."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            query = db.query(Semester).filter(Semester.is_active == True).order_by(Semester.order_no)
            if total_semesters and total_semesters > 0:
                query = query.filter(Semester.order_no <= total_semesters)
            semesters = query.all()
            return [s.name for s in semesters]
        except Exception as e:
            logger.error(f"Error fetching semesters: {e}")
            return [s["name"] for s in cls.DEFAULT_SEMESTERS]
