"""
AcademicController — Centralized Controller for Course, Branch, Academic Year, and Semester Masters.
"""

from typing import List, Dict, Any, Optional
from config.database import get_db
from models.academic import Course, Branch, AcademicYear, Semester
from utils.logger import logger

class AcademicController:
    
    DEFAULT_COURSES = [
        {"code": "BPHARM", "name": "Bachelor of Pharmacy", "course_type": "UG", "duration_years": 4, "total_semesters": 8},
        {"code": "MPHARM", "name": "Master of Pharmacy", "course_type": "PG", "duration_years": 2, "total_semesters": 4},
    ]

    DEFAULT_BRANCHES = [
        {"code": "PHARM", "name": "Pharmacy", "course_code": None},
        {"code": "GEN", "name": "General", "course_code": None},
    ]

    DEFAULT_YEARS = [
        {"code": "Y1", "name": "1st", "order_no": 1},
        {"code": "Y2", "name": "2nd", "order_no": 2},
        {"code": "Y3", "name": "3rd", "order_no": 3},
        {"code": "Y4", "name": "4th", "order_no": 4},
    ]

    DEFAULT_SEMESTERS = [
        {"code": "SEM1", "name": "1st Sem", "order_no": 1},
        {"code": "SEM2", "name": "2nd Sem", "order_no": 2},
        {"code": "SEM3", "name": "3rd Sem", "order_no": 3},
        {"code": "SEM4", "name": "4th Sem", "order_no": 4},
        {"code": "SEM5", "name": "5th Sem", "order_no": 5},
        {"code": "SEM6", "name": "6th Sem", "order_no": 6},
        {"code": "SEM7", "name": "7th Sem", "order_no": 7},
        {"code": "SEM8", "name": "8th Sem", "order_no": 8},
    ]

    @classmethod
    def seed_academic_masters_if_empty(cls):
        """Ensures default Courses, Branches, Academic Years, and Semesters are present and updated."""
        db = get_db()
        try:
            # Seed or sync default courses (Bachelor of Pharmacy & Master of Pharmacy)
            for c in cls.DEFAULT_COURSES:
                existing = db.query(Course).filter(Course.name == c["name"]).first()
                if not existing:
                    db.add(Course(**c))
                else:
                    existing.duration_years = c["duration_years"]
                    existing.total_semesters = c["total_semesters"]
                    existing.course_type = c["course_type"]
            db.commit()

            # Seed Branches
            if db.query(Branch).count() == 0:
                for b in cls.DEFAULT_BRANCHES:
                    db.add(Branch(**b))
                db.commit()

            # Seed or Update Years to new ordinal format
            if db.query(AcademicYear).count() == 0:
                for y in cls.DEFAULT_YEARS:
                    db.add(AcademicYear(**y))
                db.commit()
            else:
                for y in cls.DEFAULT_YEARS:
                    ay = db.query(AcademicYear).filter(AcademicYear.code == y["code"]).first()
                    if ay and ay.name != y["name"]:
                        ay.name = y["name"]
                db.commit()

            # Seed or Update Semesters to new ordinal format
            if db.query(Semester).count() == 0:
                for s in cls.DEFAULT_SEMESTERS:
                    db.add(Semester(**s))
                db.commit()
            else:
                for s in cls.DEFAULT_SEMESTERS:
                    sem = db.query(Semester).filter(Semester.code == s["code"]).first()
                    if sem and sem.name != s["name"]:
                        sem.name = s["name"]
                db.commit()
            logger.info("Academic master tables initialized successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error seeding academic masters: {e}")

    @classmethod
    def get_course_categories(cls) -> List[str]:
        """Returns course categories: ['UG', 'PG']."""
        return ["UG", "PG"]

    @classmethod
    def get_courses_by_category(cls, category: str = "All") -> List[str]:
        """Returns list of active course names filtered by category ('UG' or 'PG')."""
        cls.seed_academic_masters_if_empty()
        cat = category.strip().upper()
        if cat in ("UG", "PG"):
            if cat == "UG":
                return ["Bachelor of Pharmacy"]
            elif cat == "PG":
                return ["Master of Pharmacy"]
        db = get_db()
        try:
            query = db.query(Course).filter(Course.is_active == True)
            if cat != "ALL":
                query = query.filter(Course.course_type == cat)
            courses = query.order_by(Course.id).all()
            if courses:
                return [c.name for c in courses]
            return ["Bachelor of Pharmacy"] if cat == "UG" else ["Master of Pharmacy"] if cat == "PG" else ["Bachelor of Pharmacy", "Master of Pharmacy"]
        except Exception as e:
            logger.error(f"Error fetching courses by category: {e}")
            return ["Bachelor of Pharmacy"] if cat == "UG" else ["Master of Pharmacy"] if cat == "PG" else ["Bachelor of Pharmacy", "Master of Pharmacy"]
        finally:
            db.close()

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
            return ["Bachelor of Pharmacy", "Master of Pharmacy"]
        finally:
            db.close()

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
        finally:
            db.close()

    @classmethod
    def get_years(cls, course_name: Optional[str] = None) -> List[str]:
        """Returns list of academic year names filtered by course duration."""
        cls.seed_academic_masters_if_empty()
        max_years = 4
        if course_name:
            cn = course_name.lower()
            if "master" in cn or "mpharm" in cn or "m.pharmacy" in cn or "pg" in cn:
                max_years = 2
            elif "bachelor" in cn or "bpharm" in cn or "b.pharmacy" in cn or "ug" in cn:
                max_years = 4

        db = get_db()
        try:
            years = db.query(AcademicYear).filter(
                AcademicYear.is_active == True,
                AcademicYear.order_no <= max_years
            ).order_by(AcademicYear.order_no).all()
            return [y.name for y in years]
        except Exception as e:
            logger.error(f"Error fetching academic years: {e}")
            return [y["name"] for y in cls.DEFAULT_YEARS if y["order_no"] <= max_years]
        finally:
            db.close()

    @classmethod
    def get_semesters(cls, total_semesters: Optional[int] = None, course_name: Optional[str] = None) -> List[str]:
        """Returns list of semester names filtered by course total semesters."""
        cls.seed_academic_masters_if_empty()
        max_sem = total_semesters
        if not max_sem and course_name:
            cn = course_name.lower()
            if "master" in cn or "mpharm" in cn or "m.pharmacy" in cn or "pg" in cn:
                max_sem = 4
            elif "bachelor" in cn or "bpharm" in cn or "b.pharmacy" in cn or "ug" in cn:
                max_sem = 8

        db = get_db()
        try:
            query = db.query(Semester).filter(Semester.is_active == True).order_by(Semester.order_no)
            if max_sem and max_sem > 0:
                query = query.filter(Semester.order_no <= max_sem)
            semesters = query.all()
            return [s.name for s in semesters]
        except Exception as e:
            logger.error(f"Error fetching semesters: {e}")
            return [s["name"] for s in cls.DEFAULT_SEMESTERS if not max_sem or s["order_no"] <= max_sem]
        finally:
            db.close()

