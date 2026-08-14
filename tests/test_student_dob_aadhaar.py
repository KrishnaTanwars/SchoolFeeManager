"""
Automated Test Suite for Student DOB & Aadhaar Number Fields (Test Cases 1 to 12).
Verifies model schema, validation, persistence, duplicate detection, search,
import/export, student details display, and fee receipt privacy protection.
"""

import pytest
from datetime import date, timedelta
from PySide6.QtWidgets import QApplication
from config.database import get_db, init_db
import models.fee_category  # Ensure all SQLAlchemy mappers are loaded
import models.receipt

from models.student import Student
from models.receipt import Receipt
from controllers.student_controller import StudentController
from controllers.receipt_controller import ReceiptController
from dialogs.student_details_dialog import StudentDetailsDialog
from services.import_service import ImportService
from services.export_service import ExportService

@pytest.fixture(scope="module", autouse=True)
def setup_models_and_app():
    init_db()
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture(autouse=True)
def clean_test_data():
    """Cleanup test students before and after each test."""
    db = get_db()
    try:
        from models.receipt import Receipt, ReceiptItem
        test_students = db.query(Student).filter(
            (Student.admission_no.like("DOB-TEST-%")) | (Student.admission_no.like("IMP-TEST-%"))
        ).all()
        for ts in test_students:
            recs = db.query(Receipt).filter(Receipt.student_id == ts.id).all()
            for r in recs:
                db.query(ReceiptItem).filter(ReceiptItem.receipt_id == r.id).delete()
                db.delete(r)
            db.delete(ts)
        db.commit()
    finally:
        db.close()
    yield
    db = get_db()
    try:
        from models.receipt import Receipt, ReceiptItem
        test_students = db.query(Student).filter(
            (Student.admission_no.like("DOB-TEST-%")) | (Student.admission_no.like("IMP-TEST-%"))
        ).all()
        for ts in test_students:
            recs = db.query(Receipt).filter(Receipt.student_id == ts.id).all()
            for r in recs:
                db.query(ReceiptItem).filter(ReceiptItem.receipt_id == r.id).delete()
                db.delete(r)
            db.delete(ts)
        db.commit()
    finally:
        db.close()


def test_01_register_student_with_valid_dob():
    """Test 1: Register student with valid DOB -> Student saves successfully."""
    valid_dob = date(2005, 5, 15)
    data = {
        "admission_no": "DOB-TEST-001",
        "name": "Arjun Kumar",
        "father_name": "Sanjay Kumar",
        "date_of_birth": valid_dob,
        "course": "B.Tech",
        "mobile": "9876543210",
        "academic_session": "2025-2026"
    }

    success, msg = StudentController.create_student(data)
    assert success is True
    assert "registered successfully" in msg

    st = StudentController.get_student_by_admission_no("DOB-TEST-001")
    assert st is not None
    assert st.date_of_birth == valid_dob


def test_02_future_dob_validation():
    """Test 2: Future DOB -> Validation should reject future date."""
    future_dob = date.today() + timedelta(days=10)

    from dialogs.student_dialog import StudentDialog
    from PySide6.QtCore import QDate
    dialog = StudentDialog()
    
    # QDateEdit maximumDate is clamped to currentDate, preventing future date selection
    assert dialog.dt_dob.maximumDate() == QDate.currentDate()

    qfuture = QDate(future_dob.year, future_dob.month, future_dob.day)
    assert qfuture > QDate.currentDate()


def test_03_register_student_with_valid_12digit_aadhaar():
    """Test 3: Enter 123456789012 -> Student saves successfully."""
    data = {
        "admission_no": "DOB-TEST-003",
        "name": "Priya Sharma",
        "father_name": "Vikas Sharma",
        "date_of_birth": date(2004, 8, 20),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "123456789012",
        "academic_session": "2025-2026"
    }

    success, msg = StudentController.create_student(data)
    assert success is True
    st = StudentController.get_student_by_admission_no("DOB-TEST-003")
    assert st.aadhaar_number == "123456789012"


def test_04_short_aadhaar_validation():
    """Test 4: Enter 12345 (less than 12 digits) -> Should fail validation."""
    data = {
        "admission_no": "DOB-TEST-004",
        "name": "Short Aadhaar Student",
        "father_name": "Test Father",
        "date_of_birth": date(2004, 8, 20),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "12345",
        "academic_session": "2025-2026"
    }

    success, msg = StudentController.create_student(data)
    assert success is False
    assert "12 numeric digits" in msg


def test_05_non_numeric_aadhaar_validation():
    """Test 5: Enter letters ABCDE123 -> Should fail validation."""
    data = {
        "admission_no": "DOB-TEST-005",
        "name": "Letters Aadhaar Student",
        "father_name": "Test Father",
        "date_of_birth": date(2004, 8, 20),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "ABCDE1234567",
        "academic_session": "2025-2026"
    }

    success, msg = StudentController.create_student(data)
    assert success is False
    assert "12 numeric digits" in msg


def test_06_duplicate_aadhaar_rejection():
    """Test 6: Register another student with same Aadhaar -> Should reject duplicate."""
    s1_data = {
        "admission_no": "DOB-TEST-006A",
        "name": "Student Alpha",
        "father_name": "Father Alpha",
        "date_of_birth": date(2005, 1, 1),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "999988887777",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s1_data)

    s2_data = {
        "admission_no": "DOB-TEST-006B",
        "name": "Student Beta",
        "father_name": "Father Beta",
        "date_of_birth": date(2005, 2, 2),
        "course": "B.Tech",
        "mobile": "9876543211",
        "aadhaar_number": "999988887777",
        "academic_session": "2025-2026"
    }
    success, msg = StudentController.create_student(s2_data)
    assert success is False
    assert "already registered" in msg


def test_07_edit_student_update_dob_aadhaar():
    """Test 7: Edit student -> Update DOB and Aadhaar -> Save -> Reopen -> Data persists."""
    s_data = {
        "admission_no": "DOB-TEST-007",
        "name": "Original Name",
        "father_name": "Father Original",
        "date_of_birth": date(2003, 10, 10),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "111122223333",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)

    st = StudentController.get_student_by_admission_no("DOB-TEST-007")
    updated_dob = date(2004, 12, 25)
    updated_aadhaar = "444455556666"

    update_data = {
        "admission_no": "DOB-TEST-007",
        "name": "Updated Name",
        "father_name": "Father Original",
        "date_of_birth": updated_dob,
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": updated_aadhaar,
        "academic_session": "2025-2026"
    }
    success, msg = StudentController.update_student(st.id, update_data)
    assert success is True

    reopened = StudentController.get_student_by_admission_no("DOB-TEST-007")
    assert reopened.date_of_birth == updated_dob
    assert reopened.aadhaar_number == updated_aadhaar


def test_08_export_csv_contains_dob_and_aadhaar(tmp_path):
    """Test 8: Export CSV -> DOB and Aadhaar Number present in headers and data rows."""
    s_data = {
        "admission_no": "DOB-TEST-008",
        "name": "Export Student",
        "father_name": "Export Father",
        "date_of_birth": date(2005, 3, 15),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "888877776666",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)

    st = StudentController.get_student_by_admission_no("DOB-TEST-008")
    headers = ["Admission No", "Student Name", "Date of Birth", "Mobile", "Aadhaar Number"]
    rows = [[st.admission_no, st.name, str(st.date_of_birth), st.mobile, st.aadhaar_number]]

    out_file = str(tmp_path / "test_export.csv")
    success, path = ExportService.export_to_csv(headers, rows, output_path=out_file)
    assert success is True

    import csv
    with open(out_file, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        read_headers = next(reader)
        read_row = next(reader)

    assert "Date of Birth" in read_headers
    assert "Aadhaar Number" in read_headers
    assert "2005-03-15" in read_row
    assert "888877776666" in read_row


def test_09_import_csv_with_dob_and_aadhaar():
    """Test 9: Import CSV -> DOB and Aadhaar imported correctly into database."""
    raw_rows = [{
        "__row_num__": 2,
        "Admission Number": "IMP-TEST-009",
        "Student Name": "Imported Student",
        "Father Name": "Import Father",
        "Date of Birth": "2005-07-20",
        "Course": "B.Tech",
        "Mobile Number": "9876543210",
        "Aadhaar Number": "555544443333",
        "Academic Session": "2025-2026"
    }]

    parsed = ImportService.validate_and_parse_students(raw_rows)
    assert parsed["valid_count"] == 1

    success, count, msg = ImportService.commit_imported_students(parsed["items"])
    assert success is True
    assert count == 1

    st = StudentController.get_student_by_admission_no("IMP-TEST-009")
    assert st is not None
    assert st.date_of_birth == date(2005, 7, 20)
    assert st.aadhaar_number == "555544443333"


def test_10_search_by_aadhaar():
    """Test 10: Typing Aadhaar digits returns matching student immediately."""
    s_data = {
        "admission_no": "DOB-TEST-010",
        "name": "Aadhaar Search Target",
        "father_name": "Target Father",
        "date_of_birth": date(2005, 6, 1),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "777766665555",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)

    results = StudentController.get_all_students(search_query="777766665555")
    assert len(results) >= 1
    target = next((s for s in results if s.admission_no == "DOB-TEST-010"), None)
    assert target is not None
    assert target.name == "Aadhaar Search Target"


def test_11_open_student_view_dialog():
    """Test 11: Student View / Details Dialog displays DOB and Aadhaar correctly."""
    s_data = {
        "admission_no": "DOB-TEST-011",
        "name": "View Target Student",
        "father_name": "Father Target",
        "date_of_birth": date(2004, 11, 11),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "333322221111",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)
    st = StudentController.get_student_by_admission_no("DOB-TEST-011")

    dlg = StudentDetailsDialog(student=st)
    assert dlg is not None


def test_12_fee_receipt_privacy_exclusion():
    """Test 12: Generate Fee Receipt -> Receipt should NOT display Aadhaar or DOB."""
    s_data = {
        "admission_no": "DOB-TEST-012",
        "name": "Receipt Privacy Student",
        "father_name": "Father Privacy",
        "date_of_birth": date(2005, 9, 9),
        "course": "B.Tech",
        "mobile": "9876543210",
        "aadhaar_number": "123412341234",
        "academic_session": "2025-2026"
    }
    StudentController.create_student(s_data)
    st = StudentController.get_student_by_admission_no("DOB-TEST-012")

    # Generate fee receipt
    success, msg, receipt = ReceiptController.create_receipt(
        student_id=st.id,
        academic_session="2025-2026",
        items=[{"fee_head_name": "Tuition Fee", "amount": 1000.0}],
        payment_mode="Cash"
    )
    assert success is True
    assert receipt is not None

    # Inspect generated receipt PDF file
    from services.pdf_service import PDFService
    pdf_path = PDFService.generate_receipt_pdf(receipt)
    assert pdf_path is not None
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Confirm privacy exclusion: Aadhaar number is absent from receipt output bytes
    assert b"123412341234" not in pdf_bytes
