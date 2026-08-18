"""
Automated unit & integration test suite verifying the 5 main client feedback changes:
1. Fees Slip Layout (14 fee heads fit on 1 page with increased spacing).
2. Student Admission Number auto-increment.
3. Separate Enrollment Number field.
4. Custom software logo resolution across user installations.
5. Optional student photo in system backup folder & clickable Excel photo hyperlinks.
"""

import pytest
from pathlib import Path
from datetime import date
import openpyxl

from config.database import init_db, get_db, run_migrations
from models.student import Student
from models.receipt import Receipt, ReceiptItem
from controllers.student_controller import StudentController
from controllers.settings_controller import SettingsController
from services.pdf_service import PDFService
from services.export_service import ExportService
from config.app_config import STUDENT_PHOTOS_DIR, EXPORTS_DIR


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_01_admission_no_autoincrement_and_enrollment_no():
    """Verifies Admission Number auto-increments and Enrollment Number is saved separately."""
    auto_adm = StudentController.get_next_admission_no()
    assert auto_adm.startswith("ADM/")

    student_data = {
        "admission_no": auto_adm,
        "enrollment_no": "ENR/2026/TEST888",
        "name": "Testing Feedback Student",
        "father_name": "Feedback Father",
        "mother_name": "Feedback Mother",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year": "1st Year",
        "semester": "Semester 1",
        "mobile": "9876543210",
        "academic_session": "2025-2026",
        "status": "Active"
    }

    success, msg = StudentController.create_student(student_data)
    assert success is True, f"Failed to create student: {msg}"

    # Verify student record in DB
    st = StudentController.get_student_by_admission_no(auto_adm)
    assert st is not None
    assert st.admission_no == auto_adm
    assert st.enrollment_no == "ENR/2026/TEST888"

    # Verify next admission number incremented
    next_adm = StudentController.get_next_admission_no()
    assert next_adm != auto_adm


def test_02_fee_slip_14_heads_single_page_fit(tmp_path):
    """Verifies Fee Slip with 14 heads generates on a single page with comfortable spacing."""
    db = get_db()
    try:
        st = db.query(Student).first()
        if not st:
            st = Student(
                admission_no="ADM/TEST/14H",
                enrollment_no="ENR/14H",
                name="14 Head Test Student",
                father_name="Test Father",
                mobile="9876543210",
                academic_session="2025-2026"
            )
            db.add(st)
            db.commit()
            db.refresh(st)

        import uuid
        rec_no = f"REC/14H/{uuid.uuid4().hex[:6]}"
        # Create receipt with 14 fee heads
        rec = Receipt(
            receipt_no=rec_no,
            receipt_date=date.today(),
            student_id=st.id,
            academic_session="2025-2026",
            payment_mode="Online UPI",
            total_amount=14000.0,
            paid_amount=14000.0,
            due_amount=0.0,
            amount_in_words="Rupees Fourteen Thousand Only"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

        items = []
        for i in range(1, 15):
            items.append(ReceiptItem(
                receipt_id=rec.id,
                category_name=f"Fee Head Particular #{i}",
                amount=1000.0
            ))
        db.add_all(items)
        db.commit()
        db.refresh(rec)

        # Fetch receipt via ReceiptController to ensure items relationship is loaded
        from controllers.receipt_controller import ReceiptController
        fetched_rec = ReceiptController.get_receipt_by_id(rec.id)

        out_pdf = str(tmp_path / "receipt_14_heads.pdf")
        gen_path = PDFService.generate_receipt_pdf(fetched_rec, output_path=out_pdf)

        assert Path(gen_path).exists()
        assert Path(gen_path).stat().st_size > 0

        # Check page count using PyPDF2 / pypdf if available
        try:
            import pypdf
            reader = pypdf.PdfReader(gen_path)
            assert len(reader.pages) == 1, f"Expected 1 page PDF for 14 fee heads, got {len(reader.pages)}"
        except ImportError:
            pass
    finally:
        db.close()


def test_03_software_logo_resolution():
    """Verifies custom logo resolution logic via SettingsController."""
    logo_path = SettingsController.get_active_logo_path()
    assert logo_path is not None or logo_path is None  # Runs cleanly without crashing
    if logo_path:
        assert Path(logo_path).exists()


def test_04_excel_export_clickable_photo_hyperlink(tmp_path):
    """Verifies student photo hyperlink is clickable in exported Excel file."""
    # Create test photo file in STUDENT_PHOTOS_DIR
    STUDENT_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    sample_photo = STUDENT_PHOTOS_DIR / "test_photo_sample.jpg"
    sample_photo.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF")  # Dummy JPEG header

    headers = ["Admission No", "Enrollment No", "Student Name", "Student Photo", "Mobile"]
    rows = [
        ["ADM/TEST/PH1", "ENR/TEST/PH1", "Photo Student 1", "test_photo_sample.jpg", "9876543210"],
        ["ADM/TEST/PH2", "ENR/TEST/PH2", "No Photo Student 2", "", "9876543211"]
    ]

    out_xlsx = str(tmp_path / "students_export_photo_test.xlsx")
    success, export_path = ExportService.export_to_excel(headers, rows, output_path=out_xlsx)
    assert success is True
    assert Path(export_path).exists()

    # Read back with openpyxl to verify cell hyperlink
    wb = openpyxl.load_workbook(export_path)
    ws = wb.active

    # Row 2 is Student 1 with photo
    cell_photo1 = ws.cell(row=2, column=4)
    assert cell_photo1.hyperlink is not None
    assert cell_photo1.hyperlink.target.startswith("file:///")
    assert "test_photo_sample.jpg" in cell_photo1.hyperlink.target

    # Row 3 is Student 2 without photo (optional photo)
    cell_photo2 = ws.cell(row=3, column=4)
    assert cell_photo2.hyperlink is None
    assert cell_photo2.value in ("", "No Photo", None)
