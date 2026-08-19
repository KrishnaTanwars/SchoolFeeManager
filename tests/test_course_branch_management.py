"""
Unit and Integration Tests for Expanded Course Master and Branch Management.
"""

import pytest
import sys
from pathlib import Path

# Ensure root dir is in python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from controllers.academic_controller import AcademicController
from models.academic import Course, Branch
from config.database import get_db

def test_course_crud():
    # 1. Add course with full program details
    ok, msg = AcademicController.add_course(
        code="DPHARM_TEST",
        name="Diploma in Pharmacy Test",
        course_type="Diploma",
        duration_years=2,
        total_semesters=4,
        department="Dept of Pharmacy Test",
        degree_awarded="Diploma in Pharmacy (D.Pharm)",
        affiliation="PCI Approved",
        eligibility_criteria="10+2 with PCB/PCM min 45%",
        baseline_annual_fee=55000.0,
        description="Comprehensive 2-year diploma program in pharmacy practice."
    )
    assert ok is True
    assert "added successfully" in msg

    # Verify present in get_courses
    courses = AcademicController.get_courses()
    assert "Diploma in Pharmacy Test" in courses

    # Fetch full record
    full_courses = AcademicController.get_all_courses_full()
    target = next((c for c in full_courses if c.code == "DPHARM_TEST"), None)
    assert target is not None
    assert target.duration_years == 2
    assert target.total_semesters == 4
    assert target.department == "Dept of Pharmacy Test"
    assert target.degree_awarded == "Diploma in Pharmacy (D.Pharm)"
    assert target.affiliation == "PCI Approved"
    assert target.eligibility_criteria == "10+2 with PCB/PCM min 45%"
    assert target.baseline_annual_fee == 55000.0
    assert "2-year diploma" in target.description

    # 2. Update course with modified details
    ok_upd, msg_upd = AcademicController.update_course(
        target.id,
        code="DPHARM_TEST",
        name="Diploma in Pharmacy Updated",
        course_type="Diploma",
        duration_years=2,
        total_semesters=4,
        department="Dept of Pharmacy Updated",
        degree_awarded="Diploma in Pharmacy (D.Pharm)",
        affiliation="PCI & AICTE Approved",
        eligibility_criteria="10+2 with PCB/PCM min 50%",
        baseline_annual_fee=60000.0,
        description="Updated 2-year diploma program notes."
    )
    assert ok_upd is True

    courses_after_upd = AcademicController.get_courses()
    assert "Diploma in Pharmacy Updated" in courses_after_upd

    full_courses_upd = AcademicController.get_all_courses_full()
    target_upd = next((c for c in full_courses_upd if c.code == "DPHARM_TEST"), None)
    assert target_upd.baseline_annual_fee == 60000.0
    assert target_upd.affiliation == "PCI & AICTE Approved"

    # 3. Toggle status
    ok_tog, msg_tog = AcademicController.toggle_course_status(target.id)
    assert ok_tog is True
    assert "Inactive" in msg_tog

    # Inactive courses should not be returned in get_courses()
    courses_active_only = AcademicController.get_courses()
    assert "Diploma in Pharmacy Updated" not in courses_active_only

    # Toggle back to active
    AcademicController.toggle_course_status(target.id)

    # 4. Delete course
    ok_del, msg_del = AcademicController.delete_course(target.id)
    assert ok_del is True
    assert "deleted successfully" in msg_del

    courses_final = AcademicController.get_courses()
    assert "Diploma in Pharmacy Updated" not in courses_final

def test_branch_crud():
    # Pre-cleanup if leftover
    db = get_db()
    old_b = db.query(Branch).filter((Branch.code == "PHARM_TOX_TEST") | (Branch.name == "Pharmacology & Toxicology Test")).first()
    if old_b:
        db.delete(old_b)
        db.commit()

    # 1. Add branch
    ok, msg = AcademicController.add_branch(
        code="PHARM_TOX_TEST",
        name="Pharmacology & Toxicology Test",
        course_code="BPHARM"
    )
    assert ok is True
    assert "added successfully" in msg

    branches = AcademicController.get_branches()
    assert "Pharmacology & Toxicology Test" in branches

    full_branches = AcademicController.get_all_branches_full()
    target = next((b for b in full_branches if b.code == "PHARM_TOX_TEST"), None)
    assert target is not None
    assert target.course_code == "BPHARM"

    # 2. Update branch
    ok_upd, msg_upd = AcademicController.update_branch(
        target.id,
        code="PHARM_TOX_TEST",
        name="Pharmacology & Toxicology Updated",
        course_code="BPHARM"
    )
    assert ok_upd is True

    # 3. Toggle status
    ok_tog, msg_tog = AcademicController.toggle_branch_status(target.id)
    assert ok_tog is True
    assert "Inactive" in msg_tog

    # 4. Delete branch
    ok_del, msg_del = AcademicController.delete_branch(target.id)
    assert ok_del is True

def test_auto_ensure_course_and_branch():
    c_name = "Automated AI Course Test"
    b_name = "Automated AI Branch Test"

    AcademicController.auto_ensure_course_and_branch(c_name, b_name)

    # Verify both exist now
    courses = AcademicController.get_courses()
    branches = AcademicController.get_branches()

    assert c_name in courses
    assert b_name in branches

    # Clean up test data
    db = get_db()
    c_rec = db.query(Course).filter(Course.name == c_name).first()
    b_rec = db.query(Branch).filter(Branch.name == b_name).first()
    if c_rec:
        db.delete(c_rec)
    if b_rec:
        db.delete(b_rec)
    db.commit()
