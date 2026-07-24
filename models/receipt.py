"""
Receipt and ReceiptItem ORM Model definitions.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_no = Column(String(50), unique=True, nullable=False, index=True)
    receipt_date = Column(Date, default=date.today, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    academic_session = Column(String(20), nullable=False, index=True)
    subtotal = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    fine_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    amount_in_words = Column(Text, nullable=False)
    payment_mode = Column(String(30), default="Cash", nullable=False)
    reference_no = Column(String(100), nullable=True)
    remarks = Column(String(255), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="Paid", nullable=False)  # Paid / Cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("Student", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="receipts")

    def __repr__(self):
        return f"<Receipt(receipt_no='{self.receipt_no}', total={self.total_amount}, student_id={self.student_id})>"

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True)
    fee_category_id = Column(Integer, ForeignKey("fee_categories.id"), nullable=True)
    category_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)

    receipt = relationship("Receipt", back_populates="items")
    fee_category = relationship("FeeCategory")

    def __repr__(self):
        return f"<ReceiptItem(category='{self.category_name}', amount={self.amount})>"
