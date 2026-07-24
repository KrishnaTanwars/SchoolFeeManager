"""
Analytics and Financial Reports Controller with Eager Loading (joinedload).
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.receipt import Receipt, ReceiptItem
from models.student import Student
from models.fee_category import FeeCategory
from utils.logger import logger

class ReportController:
    @staticmethod
    def get_today_collection() -> float:
        db = get_db()
        try:
            today = date.today()
            res = db.query(func.sum(Receipt.total_amount))\
                .filter(Receipt.receipt_date == today, Receipt.status == "Paid").scalar()
            return float(res or 0.0)
        finally:
            db.close()

    @staticmethod
    def get_monthly_collection() -> float:
        db = get_db()
        try:
            today = date.today()
            res = db.query(func.sum(Receipt.total_amount))\
                .filter(
                    extract('year', Receipt.receipt_date) == today.year,
                    extract('month', Receipt.receipt_date) == today.month,
                    Receipt.status == "Paid"
                ).scalar()
            return float(res or 0.0)
        finally:
            db.close()

    @staticmethod
    def get_total_students_count() -> int:
        db = get_db()
        try:
            return db.query(func.count(Student.id)).filter(Student.status == "Active").scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_receipts_today_count() -> int:
        db = get_db()
        try:
            today = date.today()
            return db.query(func.count(Receipt.id)).filter(Receipt.receipt_date == today).scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_collection_report(
        date_from: date,
        date_to: date,
        class_filter: str = "All",
        session_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            query = db.query(Receipt).options(joinedload(Receipt.student)).filter(Receipt.status == "Paid")

            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)
            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)
            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)

            receipts = query.order_by(Receipt.receipt_date.asc()).all()

            total_collection = sum(r.total_amount for r in receipts)
            total_discount = sum(r.discount_amount for r in receipts)
            total_fine = sum(r.fine_amount for r in receipts)

            return {
                "receipts": receipts,
                "total_receipts": len(receipts),
                "total_collection": total_collection,
                "total_discount": total_discount,
                "total_fine": total_fine
            }
        finally:
            db.close()

    @staticmethod
    def get_class_wise_summary() -> List[Dict[str, Any]]:
        db = get_db()
        try:
            results = db.query(
                Student.class_name,
                func.count(Receipt.id),
                func.sum(Receipt.total_amount)
            ).join(Receipt, Student.id == Receipt.student_id)\
             .filter(Receipt.status == "Paid")\
             .group_by(Student.class_name).all()

            return [
                {
                    "class_name": r[0] or "N/A",
                    "receipt_count": r[1] or 0,
                    "total_collected": float(r[2] or 0.0)
                }
                for r in results
            ]
        finally:
            db.close()
