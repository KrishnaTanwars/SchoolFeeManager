"""
Student ORM Model definition.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Index
from sqlalchemy.orm import relationship
from models.base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admission_no = Column(String(50), unique=True, nullable=False, index=True)
    roll_no = Column(String(20), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    father_name = Column(String(100), nullable=False)
    mother_name = Column(String(100), nullable=True)
    class_name = Column(String(50), nullable=False, index=True)
    section = Column(String(20), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    mobile = Column(String(15), nullable=False, index=True)
    address = Column(Text, nullable=True)
    admission_date = Column(Date, default=date.today, nullable=False)
    academic_session = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default="Active", nullable=False)  # Active / Inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    receipts = relationship("Receipt", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(admission_no='{self.admission_no}', name='{self.name}', class='{self.class_name}')>"
