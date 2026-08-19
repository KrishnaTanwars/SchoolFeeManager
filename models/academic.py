"""
Academic Structure Master Models for Courses, Branches, Academic Years, and Semesters.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from models.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    course_type = Column(String(30), default="College", nullable=False) # College / School / University / Institute
    duration_years = Column(Integer, default=3, nullable=False)
    total_semesters = Column(Integer, default=6, nullable=False)
    department = Column(String(100), default="General", nullable=True)
    degree_awarded = Column(String(100), default="", nullable=True)
    affiliation = Column(String(100), default="", nullable=True)
    eligibility_criteria = Column(String(255), default="", nullable=True)
    baseline_annual_fee = Column(Float, default=0.0, nullable=True)
    description = Column(Text, default="", nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Course(code='{self.code}', name='{self.name}')>"

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    course_code = Column(String(50), nullable=True, index=True) # Linked course or NULL for all
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Branch(code='{self.code}', name='{self.name}')>"

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False, index=True)
    order_no = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AcademicYear(code='{self.code}', name='{self.name}')>"

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False, index=True)
    order_no = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Semester(code='{self.code}', name='{self.name}')>"
