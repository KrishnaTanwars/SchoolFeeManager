"""
AcademicController — Centralized Controller for Course, Branch, Academic Year, and Semester Masters.
"""

from typing import List, Dict, Any, Optional
from config.database import get_db
from models.academic import Course, Branch, AcademicYear, Semester
from utils.logger import logger

class AcademicController:
    
    DEFAULT_COURSES = [
        {"code": "BPHARM", "name": "B. Pharmacy", "course_type": "UG", "duration_years": 4, "total_semesters": 8},
        {"code": "MPHARM", "name": "M. Pharmacy", "course_type": "PG", "duration_years": 2, "total_semesters": 4},
        {"code": "BTECH", "name": "B.Tech", "course_type": "UG", "duration_years": 4, "total_semesters": 8},
        {"code": "MBA", "name": "MBA", "course_type": "PG", "duration_years": 2, "total_semesters": 4},
        {"code": "BCA", "name": "BCA", "course_type": "UG", "duration_years": 3, "total_semesters": 6},
        {"code": "CLASS10", "name": "Class 10", "course_type": "School", "duration_years": 1, "total_semesters": 0},
    ]

    DEFAULT_BRANCHES = [
        {"code": "PHARM", "name": "Pharmacy", "course_code": "BPHARM"},
        {"code": "MPHARM_CEUTICS", "name": "Pharmaceutics", "course_code": "MPHARM"},
        {"code": "CSE", "name": "Computer Science", "course_code": "BTECH"},
        {"code": "GEN", "name": "General", "course_code": None},
    ]

    DEFAULT_YEARS = [
        {"code": "Y1", "name": "1st Year", "order_no": 1},
        {"code": "Y2", "name": "2nd Year", "order_no": 2},
        {"code": "Y3", "name": "3rd Year", "order_no": 3},
        {"code": "Y4", "name": "4th Year", "order_no": 4},
    ]

    DEFAULT_SEMESTERS = [
        {"code": "SEM1", "name": "1 Sem", "order_no": 1},
        {"code": "SEM2", "name": "2 Sem", "order_no": 2},
        {"code": "SEM3", "name": "3 Sem", "order_no": 3},
        {"code": "SEM4", "name": "4 Sem", "order_no": 4},
        {"code": "SEM5", "name": "5 Sem", "order_no": 5},
        {"code": "SEM6", "name": "6 Sem", "order_no": 6},
        {"code": "SEM7", "name": "7 Sem", "order_no": 7},
        {"code": "SEM8", "name": "8 Sem", "order_no": 8},
    ]

    @classmethod
    def seed_academic_masters_if_empty(cls):
        """Ensures default Courses, Branches, Academic Years, and Semesters are present."""
        db = get_db()
        try:
            # Seed Courses
            for c in cls.DEFAULT_COURSES:
                existing = db.query(Course).filter(Course.code == c["code"]).first()
                if not existing:
                    db.add(Course(**c))
            db.commit()

            # Seed Branches
            for b in cls.DEFAULT_BRANCHES:
                existing = db.query(Branch).filter(Branch.code == b["code"]).first()
                if not existing:
                    db.add(Branch(**b))
            db.commit()

            # Seed Years
            for y in cls.DEFAULT_YEARS:
                existing = db.query(AcademicYear).filter(AcademicYear.code == y["code"]).first()
                if not existing:
                    db.add(AcademicYear(**y))
                else:
                    existing.name = y["name"]
            db.commit()

            # Seed Semesters
            for s in cls.DEFAULT_SEMESTERS:
                existing = db.query(Semester).filter(Semester.code == s["code"]).first()
                if not existing:
                    db.add(Semester(**s))
                else:
                    existing.name = s["name"]
            db.commit()
            logger.info("Academic master tables initialized successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding academic masters: {e}")

    @classmethod
    def get_courses(cls, course_type: Optional[str] = None) -> List[str]:
        """Returns list of active course names."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            query = db.query(Course).filter(Course.is_active == True)
            if course_type and course_type != "All":
                query = query.filter(Course.course_type == course_type)
            courses = query.order_by(Course.id).all()
            return [c.name for c in courses]
        except Exception as e:
            logger.error(f"Error fetching courses: {e}")
            return [c["name"] for c in cls.DEFAULT_COURSES]

    @classmethod
    def get_courses_by_category(cls, category: str) -> List[str]:
        """Returns list of course names for a given category (UG / PG)."""
        return cls.get_courses(course_type=category)

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
    def get_years(cls, course_name: Optional[str] = None) -> List[str]:
        """Returns list of academic year names."""
        cls.seed_academic_masters_if_empty()
        if course_name in ("M. Pharmacy", "MPHARM", "PG", "MBA", "MCA"):
            return ["1st Year", "2nd Year"]
        if course_name in ("B. Pharmacy", "BPHARM", "B.Tech", "BTECH", "UG"):
            return ["1st Year", "2nd Year", "3rd Year", "4th Year"]

        db = get_db()
        try:
            years = db.query(AcademicYear).filter(AcademicYear.is_active == True).order_by(AcademicYear.order_no).all()
            return [y.name for y in years]
        except Exception as e:
            logger.error(f"Error fetching academic years: {e}")
            return [y["name"] for y in cls.DEFAULT_YEARS]

    @classmethod
    def get_semesters(cls, total_semesters: Optional[int] = None, course_name: Optional[str] = None) -> List[str]:
        """Returns list of semester names (e.g. 1 Sem to 8 Sem)."""
        cls.seed_academic_masters_if_empty()
        if course_name in ("M. Pharmacy", "MPHARM", "PG", "MBA"):
            total_semesters = 4
        elif course_name in ("B. Pharmacy", "BPHARM", "UG", "BTECH"):
            total_semesters = 8

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

    @classmethod
    def validate_course_structure(cls, course: str, year: str, semester: str) -> tuple[bool, str]:
        """Validates if year and semester combinations are valid for the selected course."""
        if not course:
            return True, ""
            
        c_upper = course.upper()
        is_pg = "M. PHARMACY" in c_upper or "MPHARM" in c_upper or "PG" in c_upper or "MBA" in c_upper
        
        if is_pg:
            if year in ("3rd Year", "4th Year", "5th Year"):
                return False, f"Course '{course}' (PG) is a 2-Year program. '{year}' is invalid."
            if semester in ("Semester 5", "Semester 6", "Semester 7", "Semester 8", "5th Sem", "6th Sem", "7th Sem", "8th Sem", "5 Sem", "6 Sem", "7 Sem", "8 Sem"):
                return False, f"Course '{course}' (PG) has maximum 4 Semesters. '{semester}' is invalid."
                
        return True, ""
