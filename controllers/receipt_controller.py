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
        receipt_date: Optional[date] = None,
        paid_amount: Optional[float] = None,
        utr_number: str = "",
        cheque_number: str = "",
        cheque_date: Optional[date] = None,
        bank_name: str = "",
        payment_date: Optional[date] = None
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

            if paid_amount is None:
                calc_paid = total_amount
            else:
                calc_paid = max(0.0, min(total_amount, paid_amount))

            calc_due = max(0.0, total_amount - calc_paid)

            amount_words = number_to_words_indian(calc_paid)
            receipt_no = ReceiptController.generate_next_receipt_number()

            user = AuthController.get_current_user()
            user_id = user.id if user else None

            receipt = Receipt(
                receipt_no=receipt_no,
                receipt_date=receipt_date or date.today(),
                student_id=student_id,
                academic_session=academic_session,
                course=student.course,
                branch=getattr(student, "branch", None),
                academic_year=getattr(student, "year", None),
                semester=getattr(student, "semester", None),
                subtotal=subtotal,
                discount_amount=discount_amount,
                fine_amount=fine_amount,
                total_amount=total_amount,
                paid_amount=calc_paid,
                due_amount=calc_due,
                amount_in_words=amount_words,
                payment_mode=payment_mode,
                reference_no=reference_no.strip(),
                utr_number=utr_number.strip(),
                cheque_number=cheque_number.strip(),
                cheque_date=cheque_date,
                bank_name=bank_name.strip(),
                payment_date=payment_date or date.today(),
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
                details=f"Generated Receipt {receipt_no} for {student.name} - Total: Rs. {total_amount:.2f}, Paid: Rs. {calc_paid:.2f}, Due: Rs. {calc_due:.2f}"
            )
            db.add(audit)

            # Eagerly load relationship attributes in memory BEFORE commit
            _ = student.name
            _ = receipt.student.name
            for r_item in receipt.items:
                _ = r_item.category_name

            db.commit()

            logger.info(f"Generated Receipt {receipt_no} (ID: {receipt.id}) - Paid: Rs. {calc_paid}, Due: Rs. {calc_due}")
            return True, f"Receipt {receipt_no} generated successfully.", receipt
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating receipt: {e}", exc_info=True)
            return False, f"Database error: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def collect_fee(student_id: int, items: List[Dict[str, Any]], payment_mode: str = "Cash", **kwargs) -> Tuple[Optional[Receipt], str]:
        """Legacy helper alias for create_receipt used in Phase 2 test suite."""
        academic_session = kwargs.get("academic_session", "2024-2025")
        discount = kwargs.get("discount_amount", 0.0)
        fine = kwargs.get("fine_amount", 0.0)
        ok, msg, rec = ReceiptController.create_receipt(
            student_id=student_id,
            academic_session=academic_session,
            items=items,
            discount_amount=discount,
            fine_amount=fine,
            payment_mode=payment_mode
        )
        return rec, msg

    @staticmethod
    def get_student_outstanding_due(student_id: int) -> float:
        """Calculates total outstanding due amount across all active receipts for a student."""
        db = get_db()
        try:
            res = db.query(func.sum(Receipt.due_amount))\
                .filter(Receipt.student_id == student_id, Receipt.status == "Paid").scalar()
            return float(res or 0.0)
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
        session_filter: str = "All",
        course_filter: str = "All",
        class_filter: str = "All",
        pay_mode_filter: str = "All",
        status_filter: str = "All"
    ) -> List[Receipt]:
        db = get_db()
        try:
            query = db.query(Receipt).join(Receipt.student).options(joinedload(Receipt.student), joinedload(Receipt.items))

            if session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)

            if course_filter != "All":
                query = query.filter(Student.course == course_filter)

            if class_filter != "All":
                query = query.filter(Student.class_name == class_filter)

            if pay_mode_filter != "All":
                query = query.filter(Receipt.payment_mode == pay_mode_filter)

            if status_filter != "All":
                query = query.filter(Receipt.status == status_filter)

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
                        Student.mobile.ilike(pattern),
                        Student.course.ilike(pattern),
                        Student.class_name.ilike(pattern),
                        Receipt.payment_mode.ilike(pattern),
                        Receipt.remarks.ilike(pattern)
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

    @staticmethod
    def get_receipts_paginated(
        search_query: str = "",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All",
        course_filter: str = "All",
        class_filter: str = "All",
        pay_mode_filter: str = "All",
        status_filter: str = "All",
        page: int = 1,
        page_size: int = 25,
        branch_filter: str = "All",
        year_filter: str = "All",
        semester_filter: str = "All"
    ) -> Tuple[List[Receipt], int, int, Dict[str, float]]:
        """
        High-performance SQL paginated receipt ledger query.
        Returns: (receipts_page, total_records, total_pages, summary_totals)
        """
        db = get_db()
        try:
            query = db.query(Receipt).join(Receipt.student).options(joinedload(Receipt.student), joinedload(Receipt.items))

            if session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)

            if course_filter != "All":
                query = query.filter(or_(Receipt.course == course_filter, Student.course == course_filter))

            if branch_filter != "All":
                query = query.filter(or_(Receipt.branch == branch_filter, Student.branch == branch_filter))

            if year_filter != "All":
                query = query.filter(or_(Receipt.academic_year == year_filter, Student.year == year_filter))

            if semester_filter != "All":
                query = query.filter(or_(Receipt.semester == semester_filter, Student.semester == semester_filter))

            if class_filter != "All":
                query = query.filter(Student.class_name == class_filter)

            if pay_mode_filter != "All":
                query = query.filter(Receipt.payment_mode == pay_mode_filter)

            if status_filter != "All":
                query = query.filter(Receipt.status == status_filter)

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
                        Student.mobile.ilike(pattern),
                        Student.course.ilike(pattern),
                        Student.class_name.ilike(pattern),
                        Receipt.payment_mode.ilike(pattern),
                        Receipt.remarks.ilike(pattern)
                    )
                )

            total_records = query.count()
            page = max(1, page)
            page_size = max(1, page_size)
            total_pages = max(1, (total_records + page_size - 1) // page_size)

            offset = (page - 1) * page_size
            receipts = query.order_by(Receipt.receipt_date.desc(), Receipt.id.desc()).offset(offset).limit(page_size).all()

            for r in receipts:
                if r.student:
                    _ = r.student.name
                for item in r.items:
                    _ = item.category_name

            # Calculate total amount summary for filtered query set
            total_amt = sum(r.total_amount or 0.0 for r in receipts)
            total_paid = sum(r.paid_amount or 0.0 for r in receipts)
            total_due = sum(r.due_amount or 0.0 for r in receipts)

            summary = {
                "total_amount": total_amt,
                "total_paid": total_paid,
                "total_due": total_due
            }

            return receipts, total_records, total_pages, summary
        finally:
            db.close()

    @staticmethod
    def get_student_fee_summary(student_id: int) -> Dict[str, Any]:
        """Calculates total fee paid till date, latest due balance, and history for a student."""
        db = get_db()
        try:
            receipts = db.query(Receipt).filter(
                Receipt.student_id == student_id,
                Receipt.status == "Paid"
            ).order_by(Receipt.receipt_date.desc(), Receipt.id.desc()).all()

            total_paid = sum(r.paid_amount if r.paid_amount is not None else (r.total_amount or 0.0) for r in receipts)

            for r in receipts:
                if r.student:
                    _ = r.student.name
                for item in r.items:
                    _ = item.category_name

            latest_due = receipts[0].due_amount if (receipts and receipts[0].due_amount is not None) else 0.0

            return {
                "total_paid": total_paid,
                "latest_due": latest_due,
                "receipts_count": len(receipts),
                "receipts": receipts
            }
        finally:
            db.close()

    @staticmethod
    def cancel_receipt(receipt_id: int, reason: str = "") -> Tuple[bool, str]:
        """Cancels or deletes a receipt with Audit Logging and Delete Reason."""
        db = get_db()
        try:
            r = db.query(Receipt).filter(Receipt.id == receipt_id).first()
            if not r:
                return False, "Receipt record not found."

            r_no = r.receipt_no
            st_name = r.student.name if r.student else "Unknown"
            amt = r.total_amount or 0.0

            r.status = "Cancelled"
            db.commit()

            user = AuthController.get_current_user()
            uname = user.username if user else "Admin"

            from services.security_service import SecurityService
            audit_details = f"Cancelled receipt '{r_no}' (Student: {st_name}, Amount: Rs. {amt:.2f})"
            if reason:
                audit_details += f" - Reason: {reason}"

            SecurityService.log_audit(
                action="Receipt Deleted",
                module="Receipt History",
                details=audit_details,
                status="Success"
            )
            logger.info(f"Cancelled receipt ID {receipt_id} ({r_no}) by {uname}")
            return True, f"Receipt '{r_no}' cancelled successfully."
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling receipt {receipt_id}: {e}", exc_info=True)
            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Receipt Delete Failed",
                module="Receipt History",
                details=f"Failed to cancel receipt ID {receipt_id}: {str(e)}",
                status="Failed"
            )
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def bulk_delete_receipts(receipt_ids: Optional[List[int]] = None, reason: str = "") -> Tuple[bool, str, int]:
        """Bulk deletes or purges cancelled receipts with Audit Logging."""
        db = get_db()
        try:
            query = db.query(Receipt)
            if receipt_ids:
                query = query.filter(Receipt.id.in_(receipt_ids))
            else:
                query = query.filter(Receipt.status == "Cancelled")

            targets = query.all()
            deleted_count = len(targets)
            if deleted_count == 0:
                return True, "No target receipts found to delete.", 0

            rec_nos = [r.receipt_no for r in targets[:5]]
            sample_nos = ", ".join(rec_nos) + ("..." if deleted_count > 5 else "")

            for r in targets:
                db.delete(r)

            db.commit()

            user = AuthController.get_current_user()
            uname = user.username if user else "Admin"

            from services.security_service import SecurityService
            audit_details = f"Bulk deleted {deleted_count} receipts ({sample_nos})"
            if reason:
                audit_details += f" - Reason: {reason}"

            SecurityService.log_audit(
                action="Bulk Receipt Deleted",
                module="Receipt History",
                details=audit_details,
                status="Success"
            )
            logger.info(f"Bulk deleted {deleted_count} receipts by {uname}")
            return True, f"Successfully deleted {deleted_count} receipts.", deleted_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error in bulk receipt delete: {e}", exc_info=True)
            from services.security_service import SecurityService
            SecurityService.log_audit(
                action="Bulk Receipt Delete Failed",
                module="Receipt History",
                details=f"Bulk receipt delete failed: {str(e)}",
                status="Failed"
            )
            return False, f"Database error during bulk delete: {str(e)}", 0
        finally:
            db.close()

