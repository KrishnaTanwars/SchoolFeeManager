"""
FeeCategory / Head ORM Model definition.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean
from models.base import Base

class FeeCategory(Base):
    __tablename__ = "fee_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), nullable=True)
    default_amount = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<FeeCategory(name='{self.name}', default_amount={self.default_amount})>"
