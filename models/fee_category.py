"""
FeeCategory / Head ORM Model definition.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from models.base import Base

class FeeCategory(Base):
    __tablename__ = "fee_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    course = Column(String(20), nullable=False, default="UG", index=True) # UG / PG
    default_amount = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FeeCategory(name='{self.name}', course='{self.course}', amount={self.default_amount})>"
