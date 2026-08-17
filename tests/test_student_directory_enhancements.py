"""
Automated Test Suite for Student Directory Enhancements:
- Default Active Session Filtering
- Session Filter beside Search Box
- Bulk Delete Operations with Checkboxes
- Multi-Filter Compatibility
- Real-time Session Sync
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from config.database import get_db
from controllers.student_controller import StudentController
from services.session_service import session_manager
from views.student_view import StudentView

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def sample_students_data():
    """Fixture providing clean student records across multiple sessions."""
    db = get_db()
    try:
        from models.receipt import Receipt, ReceiptItem
        from models.student import Student
        test_students = db.query(Student).filter(
            (Student.admission_no.like("TEST-%")) | (Student.admission_no.like("BULK-%"))
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

    # Ensure active session is 2025-2026 for test baseline
    session_manager.set_active_session("2025-2026")

    s1_data = {
        "admission_no": "TEST-2025-001",
        "name": "UniqueAarav Sharma",
        "course": "B.Tech",
        "branch": "CSE",
        "year": "1st Year",
        "semester": "Semester 1",
        "academic_session": "2025-2026",
        "father_name": "Rajesh Sharma",
        "mobile": "9876543210"
    }

    s2_data = {
        "admission_no": "TEST-2025-002",
        "name": "Bhavya Gupta",
        "course": "B.Tech",
        "branch": "ECE",
        "year": "1st Year",
        "semester": "Semester 1",
        "academic_session": "2025-2026",
        "father_name": "Suresh Gupta",
        "mobile": "9876543211"
    }

    s3_data = {
        "admission_no": "TEST-2024-001",
        "name": "Chirag Verma",
        "course": "B.Tech",
        "branch": "CSE",
        "year": "2nd Year",
        "semester": "Semester 3",
        "academic_session": "2024-2025",
        "father_name": "Ramesh Verma",
        "mobile": "9876543212"
    }

    s4_data = {
        "admission_no": "TEST-2026-001",
        "name": "Divya Singh",
        "course": "B.Tech",
        "branch": "ME",
        "year": "1st Year",
        "semester": "Semester 1",
        "academic_session": "2026-2027",
        "father_name": "Mahesh Singh",
        "mobile": "9876543213"
    }

    StudentController.create_student(s1_data)
    StudentController.create_student(s2_data)
    StudentController.create_student(s3_data)
    StudentController.create_student(s4_data)

    st1 = StudentController.get_student_by_admission_no("TEST-2025-001")
    st2 = StudentController.get_student_by_admission_no("TEST-2025-002")
    st3 = StudentController.get_student_by_admission_no("TEST-2024-001")
    st4 = StudentController.get_student_by_admission_no("TEST-2026-001")

    yield [st1, st2, st3, st4]

    # Teardown
    ids_to_del = []
    for adm in ["TEST-2025-001", "TEST-2025-002", "TEST-2024-001", "TEST-2026-001"]:
        st = StudentController.get_student_by_admission_no(adm)
        if st:
            ids_to_del.append(st.id)
    if ids_to_del:
        StudentController.delete_students_bulk(ids_to_del)


def test_01_default_active_session_filter(qapp, sample_students_data):
    """Test 1: Opening Student Directory defaults to active session (2025-2026)."""
    session_manager.set_active_session("2025-2026")
    view = StudentView()

    assert view.cmb_session.currentText() == "2025-2026"
    assert len(view.current_students) >= 2

    sessions_in_view = {s.academic_session for s in view.current_students}
    assert sessions_in_view == {"2025-2026"}


def test_02_session_dropdown_display(qapp, sample_students_data):
    """Test 2: Session dropdown displays active session as default and lists other sessions."""
    session_manager.set_active_session("2025-2026")
    view = StudentView()

    assert view.cmb_session.currentText() == "2025-2026"
    all_combo_items = [view.cmb_session.itemText(i) for i in range(view.cmb_session.count())]
    assert "2025-2026" in all_combo_items
    assert "2024-2025" in all_combo_items
    assert "All Sessions" in all_combo_items or "All" in all_combo_items


def test_03_switch_session_filter_to_2024_2025(qapp, sample_students_data):
    """Test 3: Changing session dropdown to 2024-2025 displays only 2024-2025 students."""
    view = StudentView()
    view.cmb_session.setCurrentText("2024-2025")

    assert len(view.current_students) >= 1
    sessions_in_view = {s.academic_session for s in view.current_students}
    assert sessions_in_view == {"2024-2025"}


def test_04_search_and_filter_compatibility(qapp, sample_students_data):
    """Test 4: Search query combined with Session filter returns matching record."""
    view = StudentView()
    view.cmb_session.setCurrentText("2025-2026")
    view.txt_search.setText("UniqueAarav")

    assert len(view.current_students) == 1
    assert view.current_students[0].name == "UniqueAarav Sharma"
    assert view.current_students[0].academic_session == "2025-2026"


def test_05_select_all_and_deselect_all(qapp, sample_students_data):
    """Tests 6 & 7: Select All and Deselect All buttons toggle check states."""
    view = StudentView()
    view.cmb_session.setCurrentText("2025-2026")

    # Select All
    view.select_all_students()
    row_count = view.table.rowCount()
    assert row_count >= 2
    for r in range(row_count):
        assert view.table.item(r, 0).checkState() == Qt.Checked
    assert view.lbl_selected_count.text() == f"Selected: {row_count}"

    # Deselect All
    view.deselect_all_students()
    for r in range(row_count):
        assert view.table.item(r, 0).checkState() == Qt.Unchecked
    assert view.lbl_selected_count.text() == "Selected: 0"


def test_06_bulk_delete_students():
    """Test 5: Bulk deletion of multiple selected student IDs in one operation."""
    StudentController.create_student({
        "admission_no": "BULK-DEL-01",
        "name": "Temp Student 1",
        "father_name": "Father 1",
        "mobile": "9876543210",
        "course": "B.Tech",
        "academic_session": "2025-2026"
    })
    StudentController.create_student({
        "admission_no": "BULK-DEL-02",
        "name": "Temp Student 2",
        "father_name": "Father 2",
        "mobile": "9876543211",
        "course": "B.Tech",
        "academic_session": "2025-2026"
    })

    st1 = StudentController.get_student_by_admission_no("BULK-DEL-01")
    st2 = StudentController.get_student_by_admission_no("BULK-DEL-02")
    assert st1 is not None and st2 is not None

    success, msg, deleted_count = StudentController.delete_students_bulk([st1.id, st2.id])
    assert success is True
    assert deleted_count == 2

    assert StudentController.get_student_by_admission_no("BULK-DEL-01") is None
    assert StudentController.get_student_by_admission_no("BULK-DEL-02") is None


def test_07_realtime_session_sync(qapp, sample_students_data):
    """Test 9: Changing global active session in SessionManager updates Student Directory."""
    view = StudentView()
    try:
        session_manager.set_active_session("2026-2027")

        assert view.cmb_session.currentText() == "2026-2027"
        sessions_in_view = {s.academic_session for s in view.current_students}
        assert sessions_in_view == {"2026-2027"}

        # Reset active session back to 2025-2026
        session_manager.set_active_session("2025-2026")
        assert view.cmb_session.currentText() == "2025-2026"
    finally:
        try:
            session_manager.session_changed.disconnect(view.on_active_session_changed)
        except Exception:
            pass
