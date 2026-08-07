"""
Analytics and MIS Financial Reports Controller for EduLedger ERP v1.8.0.
Provides comprehensive queries for 10 specialized financial and operational reports.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from calendar import month_name
from sqlalchemy import func, extract, or_
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.receipt import Receipt, ReceiptItem
from models.student import Student
from models.fee_category import FeeCategory
from models.user import User
from utils.logger import logger

class ReportController:
    # ---------------- DASHBOARD SUMMARY METRICS ----------------
    @staticmethod
    def get_today_collection() -> float:
        db = get_db()
        try:
            today = date.today()
            res = db.query(func.sum(Receipt.paid_amount))\
                .filter(Receipt.receipt_date == today, Receipt.status == "Paid").scalar()
            return float(res or 0.0)
        finally:
            db.close()

    @staticmethod
    def get_monthly_collection() -> float:
        db = get_db()
        try:
            today = date.today()
            res = db.query(func.sum(Receipt.paid_amount))\
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
            return db.query(func.count(Receipt.id)).filter(Receipt.receipt_date == today, Receipt.status == "Paid").scalar() or 0
        finally:
            db.close()

    @staticmethod
    def get_course_default_total(db, course_name: str) -> float:
        """Returns sum of active fee category default amounts for a course."""
        c_name = course_name if course_name in ("UG", "PG") else "UG"
        res = db.query(func.sum(FeeCategory.default_amount)).filter(
            FeeCategory.course == c_name, FeeCategory.is_active == True
        ).scalar()
        return float(res or 0.0)

    # ---------------- 1. DAILY COLLECTION REPORT ----------------
    @staticmethod
    def get_daily_collection_report(
        selected_date: Optional[date] = None,
        session_filter: str = "All",
        class_filter: str = "All",
        course_filter: str = "All",
        mode_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            if not selected_date:
                selected_date = date.today()

            query = db.query(Receipt).options(joinedload(Receipt.student))\
                .join(Student, Receipt.student_id == Student.id)\
                .filter(Receipt.receipt_date == selected_date, Receipt.status == "Paid")

            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)
            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)
            if mode_filter and mode_filter != "All":
                query = query.filter(Receipt.payment_mode == mode_filter)

            receipts = query.order_by(Receipt.id.asc()).all()

            total_collection = sum(r.paid_amount or r.total_amount for r in receipts)
            total_discount = sum(r.discount_amount or 0.0 for r in receipts)
            total_fine = sum(r.fine_amount or 0.0 for r in receipts)
            net_collection = total_collection

            mode_breakdown = {}
            for r in receipts:
                pm = r.payment_mode or "Cash"
                if pm not in mode_breakdown:
                    mode_breakdown[pm] = {"count": 0, "amount": 0.0}
                mode_breakdown[pm]["count"] += 1
                mode_breakdown[pm]["amount"] += (r.paid_amount or r.total_amount)

            return {
                "date": selected_date,
                "receipts": receipts,
                "receipt_count": len(receipts),
                "total_collection": total_collection,
                "total_discount": total_discount,
                "total_fine": total_fine,
                "net_collection": net_collection,
                "mode_breakdown": mode_breakdown
            }
        finally:
            db.close()

    # ---------------- 2. MONTHLY COLLECTION REPORT ----------------
    @staticmethod
    def get_monthly_collection_report(
        year: Optional[int] = None,
        session_filter: str = "All",
        class_filter: str = "All",
        course_filter: str = "All",
        mode_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            if not year:
                year = date.today().year

            query = db.query(Receipt).options(joinedload(Receipt.student))\
                .join(Student, Receipt.student_id == Student.id)\
                .filter(extract('year', Receipt.receipt_date) == year, Receipt.status == "Paid")

            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)
            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)
            if mode_filter and mode_filter != "All":
                query = query.filter(Receipt.payment_mode == mode_filter)

            receipts = query.all()

            months_data = {m: {"receipt_count": 0, "collection": 0.0, "discount": 0.0, "fine": 0.0, "net_total": 0.0} for m in range(1, 13)}

            for r in receipts:
                if r.receipt_date:
                    m = r.receipt_date.month
                    months_data[m]["receipt_count"] += 1
                    amt = r.paid_amount or r.total_amount
                    disc = r.discount_amount or 0.0
                    fn = r.fine_amount or 0.0
                    months_data[m]["collection"] += amt
                    months_data[m]["discount"] += disc
                    months_data[m]["fine"] += fn
                    months_data[m]["net_total"] += amt

            rows = []
            for m in range(1, 13):
                md = months_data[m]
                m_name = f"{month_name[m]} {year}"
                rows.append({
                    "month": m_name,
                    "receipt_count": md["receipt_count"],
                    "collection": md["collection"],
                    "discount": md["discount"],
                    "fine": md["fine"],
                    "net_total": md["net_total"]
                })

            total_coll = sum(r["collection"] for r in rows)
            total_cnt = sum(r["receipt_count"] for r in rows)
            total_disc = sum(r["discount"] for r in rows)
            total_fine = sum(r["fine"] for r in rows)

            return {
                "year": year,
                "rows": rows,
                "total_collection": total_coll,
                "total_receipts": total_cnt,
                "total_discount": total_disc,
                "total_fine": total_fine
            }
        finally:
            db.close()

    # ---------------- 3. DATE RANGE COLLECTION REPORT ----------------
    @staticmethod
    def get_date_range_report(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All",
        class_filter: str = "All",
        course_filter: str = "All",
        mode_filter: str = "All",
        fee_head_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            query = db.query(Receipt).options(joinedload(Receipt.student))\
                .join(Student, Receipt.student_id == Student.id)\
                .filter(Receipt.status == "Paid")

            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)
            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)
            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)
            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)
            if mode_filter and mode_filter != "All":
                query = query.filter(Receipt.payment_mode == mode_filter)

            if fee_head_filter and fee_head_filter != "All":
                query = query.join(ReceiptItem, Receipt.id == ReceiptItem.receipt_id)\
                    .filter(ReceiptItem.category_name == fee_head_filter)

            receipts = query.order_by(Receipt.receipt_date.asc()).all()

            tot_coll = sum(r.paid_amount or r.total_amount for r in receipts)
            tot_disc = sum(r.discount_amount or 0.0 for r in receipts)
            tot_fine = sum(r.fine_amount or 0.0 for r in receipts)
            avg_rcpt = tot_coll / len(receipts) if receipts else 0.0

            return {
                "receipts": receipts,
                "receipt_count": len(receipts),
                "total_collection": tot_coll,
                "total_discount": tot_disc,
                "total_fine": tot_fine,
                "avg_receipt": avg_rcpt
            }
        finally:
            db.close()

    # ---------------- 4. CLASS-WISE COLLECTION REPORT ----------------
    @staticmethod
    def get_class_wise_report(
        session_filter: str = "All",
        course_filter: str = "All",
        sort_by: str = "Highest Collection"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            classes_query = db.query(Student.class_name).distinct()
            if course_filter and course_filter != "All":
                classes_query = classes_query.filter(Student.course == course_filter)
            
            all_classes = [c[0] for c in classes_query.all() if c[0]]

            rows = []
            for cls_name in sorted(all_classes):
                students = db.query(Student).filter(Student.class_name == cls_name, Student.status == "Active").all()
                stud_count = len(students)

                rq = db.query(Receipt).join(Student, Receipt.student_id == Student.id)\
                    .filter(Student.class_name == cls_name, Receipt.status == "Paid")
                if session_filter and session_filter != "All":
                    rq = rq.filter(Receipt.academic_session == session_filter)

                receipts = rq.all()

                coll = sum(r.paid_amount or r.total_amount for r in receipts)
                disc = sum(r.discount_amount or 0.0 for r in receipts)
                fine = sum(r.fine_amount or 0.0 for r in receipts)
                
                # Calculate class outstanding dynamically
                tot_fee_demanded = sum(ReportController.get_course_default_total(db, s.course or "UG") for s in students)
                due_sum = max(0.0, tot_fee_demanded - coll)

                rows.append({
                    "class_name": cls_name,
                    "student_count": stud_count,
                    "receipt_count": len(receipts),
                    "collection": coll,
                    "outstanding": float(due_sum),
                    "discount": disc,
                    "fine": fine,
                    "grand_total": coll + fine - disc
                })

            if sort_by == "Highest Collection":
                rows.sort(key=lambda x: x["collection"], reverse=True)
            elif sort_by == "Lowest Collection":
                rows.sort(key=lambda x: x["collection"], reverse=False)

            tot_coll = sum(r["collection"] for r in rows)
            tot_due = sum(r["outstanding"] for r in rows)
            tot_disc = sum(r["discount"] for r in rows)
            tot_fine = sum(r["fine"] for r in rows)

            return {
                "rows": rows,
                "total_classes": len(rows),
                "total_collection": tot_coll,
                "total_outstanding": tot_due,
                "total_discount": tot_disc,
                "total_fine": tot_fine
            }
        finally:
            db.close()

    # ---------------- 5. COURSE-WISE COLLECTION REPORT ----------------
    @staticmethod
    def get_course_wise_report(session_filter: str = "All") -> Dict[str, Any]:
        db = get_db()
        try:
            courses = ["UG", "PG"]
            rows = []
            for crs in courses:
                students = db.query(Student).filter(Student.course == crs, Student.status == "Active").all()
                stud_count = len(students)
                
                rq = db.query(Receipt).join(Student, Receipt.student_id == Student.id)\
                    .filter(Student.course == crs, Receipt.status == "Paid")
                if session_filter and session_filter != "All":
                    rq = rq.filter(Receipt.academic_session == session_filter)

                receipts = rq.all()

                coll = sum(r.paid_amount or r.total_amount for r in receipts)
                disc = sum(r.discount_amount or 0.0 for r in receipts)
                fine = sum(r.fine_amount or 0.0 for r in receipts)
                
                course_fee_each = ReportController.get_course_default_total(db, crs)
                tot_fee_demanded = course_fee_each * stud_count
                due_sum = max(0.0, tot_fee_demanded - coll)

                rows.append({
                    "course": crs,
                    "student_count": stud_count,
                    "receipt_count": len(receipts),
                    "collection": coll,
                    "outstanding": float(due_sum),
                    "discount": disc,
                    "fine": fine,
                    "grand_total": coll
                })

            tot_coll = sum(r["collection"] for r in rows)
            tot_due = sum(r["outstanding"] for r in rows)

            return {
                "rows": rows,
                "total_collection": tot_coll,
                "total_outstanding": tot_due
            }
        finally:
            db.close()

    # ---------------- 6. OUTSTANDING FEE REPORT ----------------
    @staticmethod
    def get_outstanding_report(
        session_filter: str = "All",
        course_filter: str = "All",
        class_filter: str = "All",
        filter_type: str = "All"  # All / Only Outstanding / Only Fully Paid
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            query = db.query(Student).filter(Student.status == "Active")

            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)

            students = query.order_by(Student.class_name.asc(), Student.name.asc()).all()

            rows = []
            for s in students:
                crs = s.course or "UG"
                total_fee = ReportController.get_course_default_total(db, crs)
                
                paid_amt = db.query(func.sum(Receipt.paid_amount)).filter(
                    Receipt.student_id == s.id, Receipt.status == "Paid"
                ).scalar() or 0.0

                outstanding = max(0.0, total_fee - float(paid_amt))

                if filter_type == "Only Outstanding" and outstanding <= 0:
                    continue
                if filter_type == "Only Fully Paid" and outstanding > 0:
                    continue

                rows.append({
                    "admission_no": s.admission_no,
                    "student_name": s.name,
                    "course": crs,
                    "class_name": s.class_name or "",
                    "father_name": s.father_name or "",
                    "mobile": s.mobile or "",
                    "total_fee": total_fee,
                    "paid_amount": float(paid_amt),
                    "outstanding": outstanding
                })

            tot_demanded = sum(r["total_fee"] for r in rows)
            tot_paid = sum(r["paid_amount"] for r in rows)
            tot_due = sum(r["outstanding"] for r in rows)

            return {
                "rows": rows,
                "student_count": len(rows),
                "total_demanded": tot_demanded,
                "total_paid": tot_paid,
                "total_outstanding": tot_due
            }
        finally:
            db.close()

    # ---------------- 7. STUDENT LEDGER REPORT ----------------
    @staticmethod
    def get_student_ledger(student_id_or_adm: str) -> Dict[str, Any]:
        db = get_db()
        try:
            student = None
            if str(student_id_or_adm).isdigit():
                student = db.query(Student).filter(Student.id == int(student_id_or_adm)).first()
            if not student:
                student = db.query(Student).filter(
                    (Student.admission_no == str(student_id_or_adm)) |
                    (Student.name.ilike(f"%{student_id_or_adm}%"))
                ).first()

            if not student:
                return {"success": False, "message": f"Student '{student_id_or_adm}' not found."}

            crs = student.course or "UG"
            total_fee = ReportController.get_course_default_total(db, crs)

            receipts = db.query(Receipt).filter(Receipt.student_id == student.id, Receipt.status == "Paid")\
                .order_by(Receipt.receipt_date.asc(), Receipt.id.asc()).all()

            rows = []
            running_balance = total_fee

            for r in receipts:
                paid = r.paid_amount or r.total_amount
                disc = r.discount_amount or 0.0
                fine = r.fine_amount or 0.0
                running_balance = running_balance - paid - disc + fine

                rows.append({
                    "date": r.receipt_date.strftime("%Y-%m-%d") if r.receipt_date else "",
                    "receipt_no": r.receipt_no,
                    "payment_mode": r.payment_mode or "Cash",
                    "paid_amount": paid,
                    "discount": disc,
                    "fine": fine,
                    "outstanding": max(0.0, running_balance),
                    "remarks": r.remarks or ""
                })

            tot_paid = sum(r["paid_amount"] for r in rows)
            tot_disc = sum(r["discount"] for r in rows)
            tot_fine = sum(r["fine"] for r in rows)
            current_due = max(0.0, total_fee - tot_paid - tot_disc + tot_fine)

            return {
                "success": True,
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "admission_no": student.admission_no,
                    "class_name": student.class_name,
                    "course": crs,
                    "father_name": student.father_name,
                    "mobile": student.mobile,
                    "total_fee": total_fee,
                    "due_amount": current_due
                },
                "rows": rows,
                "receipt_count": len(rows),
                "total_paid": tot_paid,
                "total_discount": tot_disc,
                "total_fine": tot_fine,
                "current_due": current_due
            }
        finally:
            db.close()

    # ---------------- 8. RECEIPT REGISTER ----------------
    @staticmethod
    def get_receipt_register(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All",
        class_filter: str = "All",
        mode_filter: str = "All",
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            query = db.query(Receipt, User.username).options(joinedload(Receipt.student))\
                .outerjoin(User, Receipt.created_by_user_id == User.id)\
                .join(Student, Receipt.student_id == Student.id)\
                .filter(Receipt.status == "Paid")

            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)
            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)
            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)
            if class_filter and class_filter != "All":
                query = query.filter(Student.class_name == class_filter)
            if mode_filter and mode_filter != "All":
                query = query.filter(Receipt.payment_mode == mode_filter)
            if search_query and search_query.strip():
                sq = f"%{search_query.strip()}%"
                query = query.filter(
                    (Receipt.receipt_no.ilike(sq)) |
                    (Student.name.ilike(sq)) |
                    (Student.admission_no.ilike(sq)) |
                    (User.username.ilike(sq))
                )

            records = query.order_by(Receipt.receipt_date.desc(), Receipt.id.desc()).all()

            rows = []
            for r, uname in records:
                rows.append({
                    "receipt_no": r.receipt_no,
                    "date": r.receipt_date.strftime("%Y-%m-%d") if r.receipt_date else "",
                    "student_name": r.student.name if r.student else "N/A",
                    "admission_no": r.student.admission_no if r.student else "N/A",
                    "course": r.student.course if r.student else "UG",
                    "class_name": r.student.class_name if r.student else "N/A",
                    "amount": r.paid_amount or r.total_amount,
                    "payment_mode": r.payment_mode or "Cash",
                    "generated_by": uname or "System Admin"
                })

            tot_amt = sum(r["amount"] for r in rows)

            return {
                "rows": rows,
                "receipt_count": len(rows),
                "total_amount": tot_amt
            }
        finally:
            db.close()

    # ---------------- 9. FEE HEAD COLLECTION REPORT ----------------
    @staticmethod
    def get_fee_head_report(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All",
        course_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            query = db.query(
                ReceiptItem.category_name,
                func.count(ReceiptItem.id),
                func.sum(ReceiptItem.amount)
            ).join(Receipt, ReceiptItem.receipt_id == Receipt.id)\
             .join(Student, Receipt.student_id == Student.id)\
             .filter(Receipt.status == "Paid")

            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)
            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)
            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)
            if course_filter and course_filter != "All":
                query = query.filter(Student.course == course_filter)

            results = query.group_by(ReceiptItem.category_name).order_by(func.sum(ReceiptItem.amount).desc()).all()

            rows = []
            for r in results:
                rows.append({
                    "fee_head": r[0] or "General Fee",
                    "tx_count": r[1] or 0,
                    "collection": float(r[2] or 0.0)
                })

            tot_coll = sum(r["collection"] for r in rows)

            return {
                "rows": rows,
                "fee_head_count": len(rows),
                "total_collection": tot_coll
            }
        finally:
            db.close()

    # ---------------- 10. PAYMENT MODE REPORT ----------------
    @staticmethod
    def get_payment_mode_report(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        session_filter: str = "All"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            modes = ["Cash", "UPI", "Cheque", "Card", "Net Banking", "Demand Draft"]
            
            query = db.query(Receipt).filter(Receipt.status == "Paid")
            if date_from:
                query = query.filter(Receipt.receipt_date >= date_from)
            if date_to:
                query = query.filter(Receipt.receipt_date <= date_to)
            if session_filter and session_filter != "All":
                query = query.filter(Receipt.academic_session == session_filter)

            receipts = query.all()
            tot_coll = sum(r.paid_amount or r.total_amount for r in receipts)

            mode_counts = {m: {"tx_count": 0, "collection": 0.0} for m in modes}
            for r in receipts:
                pm = r.payment_mode or "Cash"
                if pm not in mode_counts:
                    mode_counts[pm] = {"tx_count": 0, "collection": 0.0}
                mode_counts[pm]["tx_count"] += 1
                mode_counts[pm]["collection"] += (r.paid_amount or r.total_amount)

            rows = []
            for pm in modes:
                mc = mode_counts[pm]
                pct = (mc["collection"] / tot_coll * 100) if tot_coll > 0 else 0.0
                rows.append({
                    "payment_mode": pm,
                    "tx_count": mc["tx_count"],
                    "collection": mc["collection"],
                    "percentage": round(pct, 1)
                })

            return {
                "rows": rows,
                "total_transactions": len(receipts),
                "total_collection": tot_coll
            }
        finally:
            db.close()
