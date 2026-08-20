"""
Settings and Academic Session ORM Model definitions.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date
from models.base import Base

class AcademicSession(Base):
    __tablename__ = "academic_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_name = Column(String(30), unique=True, nullable=False, index=True)
    is_current = Column(Boolean, default=False, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return f"<AcademicSession(name='{self.session_name}', is_current={self.is_current})>"

class SchoolInformation(Base):
    __tablename__ = "school_information"

    id = Column(Integer, primary_key=True, autoincrement=True)
    school_name = Column(String(150), default="EduLedger College", nullable=False)
    address = Column(Text, default="123 Knowledge Park, New Delhi, India", nullable=False)
    city = Column(String(100), default="New Delhi", nullable=True)
    state = Column(String(100), default="Delhi", nullable=True)
    pin_code = Column(String(20), default="110001", nullable=True)
    principal_name = Column(String(100), default="Dr. A. K. Sharma", nullable=True)
    phone = Column(String(50), default="+91 98765 43210", nullable=False)
    email = Column(String(100), default="info@eduledgercollege.edu.in", nullable=False)
    website = Column(String(100), default="www.eduledgercollege.edu.in", nullable=True)
    logo_path = Column(String(255), nullable=True)
    receipt_prefix = Column(String(20), default="REC/", nullable=False)
    receipt_footer = Column(Text, default="Thank you for your payment. Keep this receipt for future reference.", nullable=False)
    current_session = Column(String(20), default="2025-2026", nullable=False)

    def __repr__(self):
        return f"<SchoolInformation(school_name='{self.school_name}')>"
