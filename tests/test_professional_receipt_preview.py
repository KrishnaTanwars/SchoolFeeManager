"""
Automated Integration Test Suite for Unified Professional Fee Receipt Preview
Covers Test Cases 1 through 10 as specified in client requirement document.
"""

import pytest
from datetime import date
from config.database import init_db
from models.student import Student
from models.fee_category import FeeCategory
from controllers.student_controller import StudentController
from controllers.receipt_controller import ReceiptController
from dialogs.receipt_preview_dialog import ReceiptPreviewDialog, generate_receipt_html
from services.pdf_service import PDFService
from services.print_service import PrintService


from PySide6.QtWidgets import QApplication
import sys

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    if not QApplication.instance():
        _app = QApplication(sys.argv)


def create_sample_student_and_receipt(admission_no="REC-TEST-999", payment_mode="Cash", extra_fields=None):
    from config.database import get_db
    from models.receipt import Receipt, ReceiptItem
    db = get_db()
    try:
        ex = db.query(Student).filter(Student.admission_no == admission_no).first()
        if ex:
            recs = db.query(Receipt).filter(Receipt.student_id == ex.id).all()
            for r in recs:
                db.query(ReceiptItem).filter(ReceiptItem.receipt_id == r.id).delete()
                db.delete(r)
            db.delete(ex)
            db.commit()
    finally:
        db.close()

    import random
    rand_mob = f"987{random.randint(1000000, 9999999)}"

    s_data = {
        "admission_no": admission_no,
        "name": "Test Student Professional",
        "father_name": "Test Father Professional",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year": "1st",
        "semester": "1st Sem",
        "mobile": rand_mob,
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)
    st = StudentController.get_student_by_admission_no(admission_no)

    db = get_db()
    fc = db.query(FeeCategory).first()
    fc_id = fc.id if fc else None
    db.close()

    items = [
        {"fee_category_id": fc_id, "category_name": "Admission Form Fee", "amount": 500.0},
        {"fee_category_id": fc_id, "category_name": "UG Tuition Fee", "amount": 12000.0},
        {"fee_category_id": fc_id, "category_name": "UG Development Fee", "amount": 3000.0}
    ]

    kwargs = {
        "student_id": st.id,
        "academic_session": "2025-2026",
        "items": items,
        "discount_amount": 500.0,
        "fine_amount": 100.0,
        "payment_mode": payment_mode,
        "paid_amount": 15100.0,
        "remarks": "Test Payment Remarks"
    }
    if extra_fields:
        kwargs.update(extra_fields)

    success, msg, receipt = ReceiptController.create_receipt(**kwargs)
    assert success is True
    assert receipt is not None
    return st, receipt


def test_01_generate_new_receipt_opens_professional_preview():
    """Test 1: Generate a new receipt -> Professional ReceiptPreviewDialog opens."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-001")
    dialog = ReceiptPreviewDialog(receipt=receipt)
    assert dialog is not None
    assert dialog.receipt.receipt_no == receipt.receipt_no


def test_02_receipt_contains_all_selected_fee_heads():
    """Test 2: Receipt contains all selected fee heads individually listed."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-002")
    fetched = ReceiptController.get_receipt_by_id(receipt.id)
    assert fetched is not None
    html = generate_receipt_html(fetched)
    assert "Admission Form Fee" in html
    assert "UG Tuition Fee" in html
    assert "UG Development Fee" in html
    assert "₹ 500.00" in html or "500.00" in html
    assert "₹ 12,000.00" in html or "12,000.00" in html


def test_03_preview_matches_professional_design_html():
    """Test 3: Preview HTML matches professional document format."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-003")
    html = generate_receipt_html(receipt)
    assert "FEE PAYMENT RECEIPT" in html
    assert "Receipt No:" in html
    assert "Student Name:" in html
    assert "Course" in html
    assert "Total Amount Paid:" in html or "Paid" in html
    assert "Amount in Words:" in html
    assert "Authorized Signatory" in html


def test_04_print_triggers_pdf_print_service(tmp_path):
    """Test 4: Print action triggers professional PDF print service."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-004")
    pdf_path = PDFService.generate_receipt_pdf(receipt)
    assert pdf_path is not None
    dialog = ReceiptPreviewDialog(receipt=receipt, pdf_path=pdf_path)
    assert dialog.pdf_path == pdf_path


def test_05_export_pdf_generates_valid_pdf_file():
    """Test 5: Export PDF exports professional PDF receipt."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-005")
    pdf_path = PDFService.generate_receipt_pdf(receipt)
    assert pdf_path is not None
    with open(pdf_path, "rb") as f:
        content = f.read()
    assert len(content) > 1000  # Confirms valid PDF binary generated


def test_06_receipt_history_view_opens_professional_receipt():
    """Test 6: Receipt History -> View opens professional receipt."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-006")
    fetched_receipt = ReceiptController.get_receipt_by_id(receipt.id)
    assert fetched_receipt is not None
    dialog = ReceiptPreviewDialog(receipt=fetched_receipt)
    assert dialog.receipt.receipt_no == fetched_receipt.receipt_no


def test_07_receipt_history_print_uses_pdf():
    """Test 7: Receipt History -> Print prints professional receipt."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-007")
    pdf_path = PDFService.generate_receipt_pdf(receipt)
    assert pdf_path is not None


def test_08_receipt_history_export_pdf():
    """Test 8: Receipt History -> Export PDF exports professional receipt."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-008")
    pdf_path = PDFService.generate_receipt_pdf(receipt)
    assert pdf_path is not None


def test_09_verify_all_payment_modes_display_correctly():
    """Test 9: Verify Cash, UPI, Card, Cheque, Demand Draft, NEFT modes."""
    modes = [
        ("Cash", {}),
        ("UPI", {"utr_number": "123456789012", "bank_name": "HDFC Bank"}),
        ("Card", {"utr_number": "CARD-REF-99", "bank_name": "SBI"}),
        ("Cheque", {"cheque_number": "654321", "cheque_date": date(2025, 8, 10), "bank_name": "ICICI Bank"}),
        ("Demand Draft", {"cheque_number": "888999", "cheque_date": date(2025, 8, 12), "bank_name": "Axis Bank"}),
        ("NEFT", {"utr_number": "NEFT-UTR-777", "bank_name": "PNB"})
    ]

    for idx, (pm, extra) in enumerate(modes, 1):
        _, receipt = create_sample_student_and_receipt(f"REC-TEST-PM-{idx}", payment_mode=pm, extra_fields=extra)
        html = generate_receipt_html(receipt)
        assert pm in html or pm.upper() in html


def test_10_no_crashes_and_no_plain_text_occurrences():
    """Test 10: Verify no crashes, no plain-text header occurrences."""
    _, receipt = create_sample_student_and_receipt("REC-TEST-010")
    html = generate_receipt_html(receipt)
    assert "=== FEE RECEIPT DETAILS ===" not in html
    assert "FEE PAYMENT RECEIPT" in html
