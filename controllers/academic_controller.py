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
        from config.database import init_db
        init_db()
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

    @classmethod
    def get_all_courses_full(cls) -> List[Course]:
        """Returns all Course records from database."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            return db.query(Course).order_by(Course.id).all()
        except Exception as e:
            logger.error(f"Error fetching full course records: {e}")
            return []

    @classmethod
    def add_course(
        cls,
        code: str,
        name: str,
        course_type: str = "UG",
        duration_years: int = 3,
        total_semesters: int = 6,
        department: str = "General",
        degree_awarded: str = "",
        affiliation: str = "",
        eligibility_criteria: str = "",
        baseline_annual_fee: float = 0.0,
        description: str = ""
    ) -> tuple[bool, str]:
        """Adds a new Course record to DB."""
        db = get_db()
        try:
            code_clean = code.strip().upper()
            name_clean = name.strip()
            if not code_clean or not name_clean:
                return False, "Course Code and Name are required."
            
            existing = db.query(Course).filter((Course.code == code_clean) | (Course.name == name_clean)).first()
            if existing:
                return False, f"A course with code '{code_clean}' or name '{name_clean}' already exists."
            
            new_course = Course(
                code=code_clean,
                name=name_clean,
                course_type=course_type,
                duration_years=duration_years,
                total_semesters=total_semesters,
                department=department.strip() or "General",
                degree_awarded=degree_awarded.strip(),
                affiliation=affiliation.strip(),
                eligibility_criteria=eligibility_criteria.strip(),
                baseline_annual_fee=float(baseline_annual_fee or 0.0),
                description=description.strip(),
                is_active=True
            )
            db.add(new_course)
            db.commit()
            return True, f"Course '{name_clean}' added successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding course: {e}")
            return False, f"Failed to add course: {e}"

    @classmethod
    def update_course(
        cls,
        course_id: int,
        code: str,
        name: str,
        course_type: str,
        duration_years: int,
        total_semesters: int,
        department: str = "General",
        degree_awarded: str = "",
        affiliation: str = "",
        eligibility_criteria: str = "",
        baseline_annual_fee: float = 0.0,
        description: str = ""
    ) -> tuple[bool, str]:
        """Updates an existing Course record in DB."""
        db = get_db()
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False, "Course not found."
            
            code_clean = code.strip().upper()
            name_clean = name.strip()
            if not code_clean or not name_clean:
                return False, "Course Code and Name are required."

            existing = db.query(Course).filter(Course.id != course_id, (Course.code == code_clean) | (Course.name == name_clean)).first()
            if existing:
                return False, f"Another course with code '{code_clean}' or name '{name_clean}' already exists."
            
            course.code = code_clean
            course.name = name_clean
            course.course_type = course_type
            course.duration_years = duration_years
            course.total_semesters = total_semesters
            course.department = department.strip() or "General"
            course.degree_awarded = degree_awarded.strip()
            course.affiliation = affiliation.strip()
            course.eligibility_criteria = eligibility_criteria.strip()
            course.baseline_annual_fee = float(baseline_annual_fee or 0.0)
            course.description = description.strip()
            db.commit()
            return True, f"Course '{name_clean}' updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating course: {e}")
            return False, f"Failed to update course: {e}"

    @classmethod
    def toggle_course_status(cls, course_id: int) -> tuple[bool, str]:
        """Toggles active/inactive status of a course."""
        db = get_db()
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False, "Course not found."
            course.is_active = not course.is_active
            db.commit()
            status_str = "Active" if course.is_active else "Inactive"
            return True, f"Course '{course.name}' is now {status_str}."
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling course status: {e}")
            return False, f"Failed to update course status: {e}"

    @classmethod
    def delete_course(cls, course_id: int) -> tuple[bool, str]:
        """Deletes a course if not in use."""
        db = get_db()
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False, "Course not found."
            c_name = course.name
            db.delete(course)
            db.commit()
            return True, f"Course '{c_name}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting course: {e}")
            return False, f"Failed to delete course: {e}"

    @classmethod
    def get_all_branches_full(cls) -> List[Branch]:
        """Returns all Branch records from database."""
        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            return db.query(Branch).order_by(Branch.id).all()
        except Exception as e:
            logger.error(f"Error fetching full branch records: {e}")
            return []

    @classmethod
    def add_branch(cls, code: str, name: str, course_code: Optional[str] = None) -> tuple[bool, str]:
        """Adds a new Branch record to DB."""
        db = get_db()
        try:
            code_clean = code.strip().upper()
            name_clean = name.strip()
            if not code_clean or not name_clean:
                return False, "Branch Code and Name are required."
            
            existing = db.query(Branch).filter((Branch.code == code_clean) | (Branch.name == name_clean)).first()
            if existing:
                return False, f"A branch with code '{code_clean}' or name '{name_clean}' already exists."

            new_branch = Branch(
                code=code_clean,
                name=name_clean,
                course_code=course_code if course_code and course_code != "All" else None,
                is_active=True
            )
            db.add(new_branch)
            db.commit()
            return True, f"Branch '{name_clean}' added successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding branch: {e}")
            return False, f"Failed to add branch: {e}"

    @classmethod
    def update_branch(cls, branch_id: int, code: str, name: str, course_code: Optional[str] = None) -> tuple[bool, str]:
        """Updates an existing Branch record in DB."""
        db = get_db()
        try:
            branch = db.query(Branch).filter(Branch.id == branch_id).first()
            if not branch:
                return False, "Branch not found."
            
            code_clean = code.strip().upper()
            name_clean = name.strip()
            if not code_clean or not name_clean:
                return False, "Branch Code and Name are required."

            existing = db.query(Branch).filter(Branch.id != branch_id, (Branch.code == code_clean) | (Branch.name == name_clean)).first()
            if existing:
                return False, f"Another branch with code '{code_clean}' or name '{name_clean}' already exists."

            branch.code = code_clean
            branch.name = name_clean
            branch.course_code = course_code if course_code and course_code != "All" else None
            db.commit()
            return True, f"Branch '{name_clean}' updated successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating branch: {e}")
            return False, f"Failed to update branch: {e}"

    @classmethod
    def toggle_branch_status(cls, branch_id: int) -> tuple[bool, str]:
        """Toggles active/inactive status of a branch."""
        db = get_db()
        try:
            branch = db.query(Branch).filter(Branch.id == branch_id).first()
            if not branch:
                return False, "Branch not found."
            branch.is_active = not branch.is_active
            db.commit()
            status_str = "Active" if branch.is_active else "Inactive"
            return True, f"Branch '{branch.name}' is now {status_str}."
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling branch status: {e}")
            return False, f"Failed to update branch status: {e}"

    @classmethod
    def delete_branch(cls, branch_id: int) -> tuple[bool, str]:
        """Deletes a branch if not in use."""
        db = get_db()
        try:
            branch = db.query(Branch).filter(Branch.id == branch_id).first()
            if not branch:
                return False, "Branch not found."
            b_name = branch.name
            db.delete(branch)
            db.commit()
            return True, f"Branch '{b_name}' deleted successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting branch: {e}")
            return False, f"Failed to delete branch: {e}"

    @classmethod
    def auto_ensure_course_and_branch(cls, course_name: str, branch_name: str):
        """Automatically registers course_name and branch_name into master tables if they do not exist."""
        c_name = (course_name or "").strip()
        b_name = (branch_name or "").strip()

        if not c_name:
            return

        cls.seed_academic_masters_if_empty()
        db = get_db()
        try:
            # Check course
            existing_c = db.query(Course).filter(Course.name.ilike(c_name)).first()
            if not existing_c:
                c_upper = c_name.upper()
                c_type = "PG" if ("M." in c_upper or "PG" in c_upper or "MASTER" in c_upper or "MBA" in c_upper or "MCA" in c_upper) else "UG"
                c_code = "".join([ch for ch in c_upper if ch.isalnum()])[:15] or "COURSE"
                counter = 1
                base_code = c_code
                while db.query(Course).filter(Course.code == c_code).first():
                    c_code = f"{base_code}_{counter}"
                    counter += 1
                
                db.add(Course(
                    code=c_code,
                    name=c_name,
                    course_type=c_type,
                    duration_years=2 if c_type == "PG" else 3,
                    total_semesters=4 if c_type == "PG" else 6,
                    is_active=True
                ))
                db.commit()

            # Check branch
            if b_name:
                existing_b = db.query(Branch).filter(Branch.name.ilike(b_name)).first()
                if not existing_b:
                    b_upper = b_name.upper()
                    b_code = "".join([ch for ch in b_upper if ch.isalnum()])[:15] or "BRANCH"
                    counter = 1
                    base_code = b_code
                    while db.query(Branch).filter(Branch.code == b_code).first():
                        b_code = f"{base_code}_{counter}"
                        counter += 1
                    
                    db.add(Branch(
                        code=b_code,
                        name=b_name,
                        course_code=None,
                        is_active=True
                    ))
                    db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error auto-ensuring course '{c_name}' & branch '{b_name}': {e}")

