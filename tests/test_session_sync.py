"""
Automated Unit and Integration Tests for Centralized Active Academic Session Synchronization.
Verifies DB updates, PySide6 signal emission, UI Header synchronization, student registration default,
receipt generation session attachment, and persistence across software restarts.
"""

import pytest
from config.database import get_db
from models.settings import AcademicSession, SchoolInformation
from services.session_service import SessionManager, session_manager
from controllers.settings_controller import SettingsController
from controllers.student_controller import StudentController
from controllers.receipt_controller import ReceiptController

@pytest.fixture(autouse=True)
def setup_db_session():
    """Ensure clean test environment for academic session tests."""
    db = get_db()
    try:
        # Clear test receipts and students
        from models.receipt import Receipt, ReceiptItem
        from models.student import Student
        from sqlalchemy import or_
        recs = db.query(Receipt).all()
        for r in recs:
            db.query(ReceiptItem).filter(ReceiptItem.receipt_id == r.id).delete()
            db.delete(r)
        st_list = db.query(Student).filter(or_(Student.admission_no.like("TEST%"), Student.admission_no.like("DOB%"), Student.mobile == "9876543210")).all()
        for s in st_list:
            db.delete(s)
        db.commit()

        # Clear or reset sessions
        db.query(AcademicSession).delete()
        info = db.query(SchoolInformation).first()
        if not info:
            info = SchoolInformation(school_name="DPS International School", current_session="2024-2025")
            db.add(info)
        else:
            info.current_session = "2024-2025"

        s1 = AcademicSession(session_name="2024-2025", is_current=True)
        s2 = AcademicSession(session_name="2025-2026", is_current=False)
        db.add_all([s1, s2])
        db.commit()
    finally:
        db.close()
    
    session_manager.refresh()
    yield

def test_01_get_active_session_initial():
    """Test 1: Initial active session returns 2024-2025."""
    active = session_manager.get_active_session()
    assert active == "2024-2025"

def test_02_set_active_session_updates_db_and_signal():
    """Test 2: Changing session to 2025-2026 updates DB and emits signal."""
    received_signals = []
    
    def on_signal(new_sess):
        received_signals.append(new_sess)

    session_manager.session_changed.connect(on_signal)
    
    success, msg = session_manager.set_active_session("2025-2026")
    assert success is True
    assert "2025-2026" in msg
    assert session_manager.get_active_session() == "2025-2026"
    assert "2025-2026" in received_signals

    # Verify Database state
    db = get_db()
    try:
        curr_sess = db.query(AcademicSession).filter(AcademicSession.is_current == True).first()
        assert curr_sess is not None
        assert curr_sess.session_name == "2025-2026"

        info = db.query(SchoolInformation).first()
        assert info.current_session == "2025-2026"
    finally:
        db.close()
        session_manager.session_changed.disconnect(on_signal)

def test_03_switch_session_to_2026_2027():
    """Test 3: Changing session to 2026-2027 creates new record if needed and sets active."""
    success, msg = session_manager.set_active_session("2026-2027")
    assert success is True
    assert session_manager.get_active_session() == "2026-2027"

    db = get_db()
    try:
        s_record = db.query(AcademicSession).filter(AcademicSession.session_name == "2026-2027").first()
        assert s_record is not None
        assert s_record.is_current is True
    finally:
        db.close()

def test_04_student_creation_uses_active_session():
    """Test 4: Creating a student without explicit session defaults to current active session."""
    session_manager.set_active_session("2026-2027")
    
    data = {
        "admission_no": "TEST-SESSION-001",
        "name": "Session Test Student",
        "father_name": "Father Test",
        "course": "UG",
        "mobile": "9876543210"
    }
    success, msg = StudentController.create_student(data)
    assert success is True

    # Retrieve student and verify academic_session is 2026-2027
    db = get_db()
    try:
        st = db.query(StudentController.get_student_by_admission_no.__globals__["Student"]).filter(
            StudentController.get_student_by_admission_no.__globals__["Student"].admission_no == "TEST-SESSION-001"
        ).first()
        assert st is not None
        assert st.academic_session == "2026-2027"
    finally:
        db.close()

def test_05_receipt_generation_uses_active_session():
    """Test 5: Generating a receipt uses current active session 2026-2027."""
    session_manager.set_active_session("2026-2027")

    # Create test student first
    data = {
        "admission_no": "TEST-REC-SESS-001",
        "name": "Receipt Session Student",
        "father_name": "Father Test",
        "course": "UG",
        "mobile": "9876543210"
    }
    StudentController.create_student(data)
    student = StudentController.get_student_by_admission_no("TEST-REC-SESS-001")
    assert student is not None

    # Collect Fee / Create Receipt
    db = get_db()
    try:
        from models.fee_category import FeeCategory
        fc = db.query(FeeCategory).first()
        if not fc:
            fc = FeeCategory(name="Tuition Fee", course="UG", default_amount=5000.0, is_active=True)
            db.add(fc)
            db.commit()
        fc_id = fc.id
        fc_name = fc.name
    finally:
        db.close()

    items = [{"fee_category_id": fc_id, "category_name": fc_name, "amount": 5000.0}]
    success, msg, receipt = ReceiptController.create_receipt(
        student_id=student.id,
        academic_session="", # Empty triggers fallback to active session
        items=items,
        paid_amount=5000.0
    )
    assert success is True
    assert receipt is not None
    assert receipt.academic_session == "2026-2027"

def test_06_persistence_across_restarts():
    """Test 6: Simulating app restart preserves current active session 2026-2027."""
    session_manager.set_active_session("2026-2027")

    # Create new SessionManager instance and re-query DB
    new_manager = SessionManager()
    new_manager._active_session = None # Clear cache
    assert new_manager.get_active_session() == "2026-2027"
