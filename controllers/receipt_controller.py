"""
Receipt Creation, Auto-Numbering, and Management Controller with Relation Eager Loading.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.receipt import Receipt, ReceiptItem
from models.student import Student
from models.settings import SchoolInformation
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from utils.number_to_words import number_to_words_indian
from utils.logger import logger

class ReceiptController:
    @staticmethod
    def generate_next_receipt_number() -> str:
        db = get_db()
        try:
            school_info = db.query(SchoolInformation).first()
            prefix = school_info.receipt_prefix if school_info else "REC/"
            
            count = db.query(func.count(Receipt.id)).scalar() or 0
            next_num = count + 1
            
            receipt_no = f"{prefix}{next_num:05d}"
            while db.query(Receipt).filter(Receipt.receipt_no == receipt_no).first():
                next_num += 1
                receipt_no = f"{prefix}{next_num:05d}"
                
            return receipt_no
        finally:
            db.close()

    @staticmethod
    def create_receipt(
        student_id: int,
        academic_session: str,
        items: List[Dict[str, Any]],
        discount_amount: float = 0.0,
        fine_amount: float = 0.0,
        payment_mode: str = "Cash",
        reference_no: str = "",
        remarks: str = "",
        receipt_date: Optional[date] = None
    ) -> Tuple[bool, str, Optional[Receipt]]:
        db = get_db()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Student not found.", None

            if not items:
                return False, "At least one fee head must be selected.", None

            subtotal = sum(item["amount"] for item in items)
            if subtotal <= 0:
                return False, "Subtotal must be greater than zero.", None

            discount_amount = max(0.0, discount_amount)
            fine_amount = max(0.0, fine_amount)
            total_amount = max(0.0, subtotal - discount_amount + fine_amount)

            amount_words = number_to_words_indian(total_amount)
            receipt_no = ReceiptController.generate_next_receipt_number()

            user = AuthController.get_current_user()
            user_id = user.id if user else None

            receipt = Receipt(
                receipt_no=receipt_no,
                receipt_date=receipt_date or date.today(),
                student_id=student_id,
                academic_session=academic_session,
                subtotal=subtotal,
                discount_amount=discount_amount,
                fine_amount=fine_amount,
                total_amount=total_amount,
                amount_in_words=amount_words,
                payment_mode=payment_mode,
                reference_no=reference_no.strip(),
                remarks=remarks.strip(),
                created_by_user_id=user_id,
                status="Paid"
            )
            db.add(receipt)
            db.flush()

            for item in items:
                ritem = ReceiptItem(
                    receipt_id=receipt.id,
                    fee_category_id=item.get("fee_category_id"),
                    category_name=item.get("category_name", "Fee Head"),
                    amount=item.get("amount", 0.0)
                )
                db.add(ritem)

            audit = AuditLog(
                user_id=user_id,
                action="CREATE_RECEIPT",
                details=f"Generated Receipt {receipt_no} for {student.name} - Total: ₹{total_amount:.2f}"
            )
            db.add(audit)

            # Eagerly load relationship attributes in memory BEFORE commit
            _ = student.name
            _ = receipt.student.name
            for r_item in receipt.items:
                _ = r_item.category_name

            db.commit()

            logger.info(f"Generated Receipt {receipt_no} (ID: {receipt.id})")
            return True, f"Receipt {receipt_no} generated successfully.", receipt
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating receipt: {e}", exc_info=True)
            return False, f"Database error: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def get_receipt_by_id(receipt_id: int) -> Optional[Receipt]:
        db = get_db()
        try:
            r = db.query(Receipt).options(joinedload(Receipt.student), joinedload(Receipt.items)).filter(Receipt.id == receipt_id).first()
            if r:
                _ = r.student.name
                for item in r.items:
                    _ = item.category_name
            return r
        finally:
            db.close()

    @staticmethod
    def get_all_receipts(
        search_query: str = "",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All"
    ) -> List[Receipt]:
        db = get_db()
        try:
            query = db.query(Receipt).options(joinedload(Receipt.student), joinedload(Receipt.items))

            if session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)

            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)

            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)

            if search_query:
                pattern = f"%{search_query.strip()}%"
                query = query.filter(
                    or_(
                        Receipt.receipt_no.ilike(pattern),
                        Student.name.ilike(pattern),
                        Student.admission_no.ilike(pattern),
                        Student.father_name.ilike(pattern),
                        Student.mobile.ilike(pattern)
                    )
                )

            receipts = query.order_by(Receipt.receipt_date.desc(), Receipt.id.desc()).all()
            for r in receipts:
                if r.student:
                    _ = r.student.name
                for item in r.items:
                    _ = item.category_name
            return receipts
        finally:
            db.close()
