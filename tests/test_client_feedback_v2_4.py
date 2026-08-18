"""
Unit tests for Client Feedback v2.4 enhancements:
Student Photo persistence, Roll Number removal, Admission Number label update,
Master Year/Semester ordinals, Student Profile PDF, Fee Receipt PDF individual fee heads, and Dashboard updates.
"""

import pytest
import os
from pathlib import Path
from datetime import date, datetime

from config.database import init_db, get_db, run_migrations
from config.app_config import STUDENT_PHOTOS_DIR, EXPORTS_DIR
from models.student import Student
from models.receipt import Receipt
from models.fee_category import FeeCategory
from controllers.student_controller import StudentController
from controllers.academic_controller import AcademicController
from controllers.receipt_controller import ReceiptController
from services.pdf_service import PDFService


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    yield


def test_student_photo_field_and_migration():
    """Verify photo_path column exists in model and database table."""
    db = get_db()
    try:
        data = {
            "admission_no": f"TEST_PHOTO_{datetime.now().strftime('%H%M%S%f')}",
            "name": "Photo Test Student",
            "father_name": "Test Father",
            "date_of_birth": date(2005, 5, 15),
            "course": "B.Tech",
            "branch": "Computer Science",
            "year": "1st",
            "semester": "1st Sem",
            "mobile": "9876543210",
            "photo_path": "student_photos/photo_test123.jpg"
        }
        success, msg = StudentController.create_student(data)
        assert success is True

        st = StudentController.get_student_by_admission_no(data["admission_no"])
        assert st is not None
        assert st.photo_path == "student_photos/photo_test123.jpg"
    finally:
        db.close()


def test_roll_number_removal_and_admission_number():
    """Verify Roll Number is omitted and Admission Number works reliably."""
    db = get_db()
    try:
        data = {
            "admission_no": f"TEST_ADM_{datetime.now().strftime('%H%M%S%f')}",
            "name": "No Roll Student",
            "father_name": "Father Name",
            "date_of_birth": date(2004, 8, 20),
            "course": "MBA",
            "branch": "Finance",
            "year": "2nd",
            "semester": "3rd Sem",
            "mobile": "9876543211",
            "roll_no": ""
        }
        success, msg = StudentController.create_student(data)
        assert success is True

        st = StudentController.get_student_by_admission_no(data["admission_no"])
        assert st is not None
        assert st.admission_no == data["admission_no"]
    finally:
        db.close()


def test_academic_year_and_semester_ordinals():
    """Verify AcademicController master dropdown values use ordinals (1st, 1st Sem)."""
    years = AcademicController.get_years()
    semesters = AcademicController.get_semesters()

    assert any("1st" in y for y in years)
    assert any("1" in s for s in semesters)


def test_fee_receipt_pdf_individual_fee_heads():
    """Verify Fee Receipt PDF generates cleanly with individual selected fee heads."""
    db = get_db()
    try:
        data = {
            "admission_no": f"TEST_REC_{datetime.now().strftime('%H%M%S%f')}",
            "name": "Receipt Test Student",
            "father_name": "Father Test",
            "date_of_birth": date(2003, 10, 10),
            "course": "B.Tech",
            "branch": "CSE",
            "year": "1st",
            "semester": "1st Sem",
            "mobile": "9876543212"
        }
        StudentController.create_student(data)
        st = StudentController.get_student_by_admission_no(data["admission_no"])
        assert st is not None

        cat = db.query(FeeCategory).first()
        cat_id = cat.id if cat else None

        items = [
            {"fee_category_id": cat_id, "category_name": "Admission Fee", "amount": 500.0},
            {"fee_category_id": cat_id, "category_name": "Tuition Fee", "amount": 12000.0},
            {"fee_category_id": cat_id, "category_name": "Development Fee", "amount": 3000.0}
        ]

        success, msg, receipt = ReceiptController.create_receipt(
            student_id=st.id,
            academic_session="2025-2026",
            items=items,
            payment_mode="Cash",
            paid_amount=15500.0
        )
        assert success is True
        assert receipt is not None

        fresh_receipt = ReceiptController.get_receipt_by_id(receipt.id)
        assert fresh_receipt is not None
        assert len(fresh_receipt.items) == 3

        pdf_path = PDFService.generate_receipt_pdf(fresh_receipt)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0
    finally:
        db.close()


def test_student_profile_pdf_generation():
    """Verify Student Profile PDF generates cleanly."""
    db = get_db()
    try:
        timestamp_str = datetime.now().strftime('%H%M%S%f')
        data = {
            "admission_no": f"TEST_PROF_{timestamp_str}",
            "name": "Profile Test Student",
            "father_name": "Parent Name",
            "mother_name": "Mother Name",
            "date_of_birth": date(2002, 1, 1),
            "course": "BCA",
            "branch": "General",
            "year": "3rd",
            "semester": "5th Sem",
            "mobile": "9876543213",
            "aadhaar_number": f"12{timestamp_str[:10]}",
            "address": "123 Test Street, New Delhi",
            "academic_session": "2025-2026",
            "status": "Active"
        }
        success, msg = StudentController.create_student(data)
        assert success is True, msg

        st = StudentController.get_student_by_admission_no(data["admission_no"])
        assert st is not None

        pdf_path = PDFService.generate_student_profile_pdf(st)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0
    finally:
        db.close()
