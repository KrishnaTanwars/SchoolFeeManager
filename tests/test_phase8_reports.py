"""
Unit tests for Phase 8 – Professional Financial Reports & Analytics (v1.8.0).
"""

import pytest
from datetime import date, datetime
from config.database import init_db, get_db
from models.user import User
from models.student import Student
from models.receipt import Receipt, ReceiptItem
from controllers.report_controller import ReportController


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database schema before running report tests."""
    init_db()


def test_daily_collection_report():
    """Verify daily collection report query and metric aggregation."""
    rep = ReportController.get_daily_collection_report(selected_date=date.today())
    assert isinstance(rep, dict)
    assert "receipts" in rep
    assert "receipt_count" in rep
    assert "total_collection" in rep
    assert "net_collection" in rep
    assert "mode_breakdown" in rep


def test_monthly_collection_report():
    """Verify monthly collection summary report structure."""
    rep = ReportController.get_monthly_collection_report(year=date.today().year)
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert len(rep["rows"]) == 12
    assert "total_collection" in rep
    assert "total_receipts" in rep


def test_date_range_report():
    """Verify date range collection report with custom filters."""
    rep = ReportController.get_date_range_report(
        date_from=date(2024, 1, 1),
        date_to=date.today(),
        session_filter="All",
        class_filter="All"
    )
    assert isinstance(rep, dict)
    assert "receipts" in rep
    assert "avg_receipt" in rep


def test_class_wise_report():
    """Verify class-wise revenue and outstanding summary report."""
    rep = ReportController.get_class_wise_report(sort_by="Highest Collection")
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert "total_classes" in rep
    assert "total_collection" in rep
    assert "total_outstanding" in rep


def test_course_wise_report():
    """Verify UG vs PG course-wise collection breakdown."""
    rep = ReportController.get_course_wise_report()
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert len(rep["rows"]) == 2
    assert any(r["course"] == "UG" for r in rep["rows"])
    assert any(r["course"] == "PG" for r in rep["rows"])


def test_outstanding_report():
    """Verify outstanding fee report query and status filtering."""
    rep_all = ReportController.get_outstanding_report(filter_type="All")
    assert isinstance(rep_all, dict)
    assert "rows" in rep_all
    assert "total_outstanding" in rep_all

    rep_out = ReportController.get_outstanding_report(filter_type="Only Outstanding")
    assert isinstance(rep_out, dict)
    assert all(r["outstanding"] > 0 for r in rep_out["rows"])


def test_student_ledger_report():
    """Verify student ledger query with running balance tracking."""
    db = get_db()
    try:
        student = db.query(Student).first()
        if student:
            rep = ReportController.get_student_ledger(student.admission_no)
            assert rep["success"] is True
            assert "rows" in rep
            assert "total_paid" in rep
            assert "current_due" in rep
    finally:
        db.close()


def test_receipt_register_report():
    """Verify receipt register log with operator tracking."""
    rep = ReportController.get_receipt_register()
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert "receipt_count" in rep
    assert "total_amount" in rep


def test_fee_head_report():
    """Verify collection grouping by fee head category."""
    rep = ReportController.get_fee_head_report()
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert "fee_head_count" in rep


def test_payment_mode_report():
    """Verify transaction totals grouped by payment mode."""
    rep = ReportController.get_payment_mode_report()
    assert isinstance(rep, dict)
    assert "rows" in rep
    assert len(rep["rows"]) == 6  # Cash, UPI, Cheque, Card, Net Banking, DD
    assert any(r["payment_mode"] == "Cash" for r in rep["rows"])
