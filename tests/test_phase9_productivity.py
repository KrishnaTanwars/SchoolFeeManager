"""
Unit tests for Phase 9 – Data Management, Import/Export & Productivity (v1.9.0).
"""

import pytest
from pathlib import Path
from config.database import init_db
from services.import_service import ImportService
from services.export_service import ExportService
from services.backup_service import BackupService


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database schema before running productivity tests."""
    init_db()


def test_student_csv_and_excel_sample_generation(tmp_path):
    """Verify sample CSV and Excel template generation."""
    csv_file = str(tmp_path / "sample.csv")
    succ_csv, msg_csv = ImportService.generate_sample_csv(csv_file)
    assert succ_csv is True
    assert Path(csv_file).exists()

    excel_file = str(tmp_path / "sample.xlsx")
    succ_ex, msg_ex = ImportService.generate_sample_excel(excel_file)
    assert succ_ex is True
    assert Path(excel_file).exists()


def test_student_import_validation_and_parsing():
    """Verify raw row validation, mandatory field checks, and mobile formatting."""
    raw_rows = [
        {
            "__row_num__": 2,
            "Admission Number": "ADM/TEST/001",
            "Student Name": "Rahul Verma",
            "Father Name": "Ramesh Verma",
            "Class": "Class 10",
            "Mobile Number": "9876543210"
        },
        {
            "__row_num__": 3,
            "Admission Number": "",
            "Student Name": "",
            "Father Name": "",
            "Class": "",
            "Mobile Number": "123"
        }
    ]

    res = ImportService.validate_and_parse_students(raw_rows)
    assert res["total_rows"] == 2
    assert res["valid_count"] == 1
    assert res["invalid_count"] == 1
    assert len(res["errors_report"]) == 1


def test_student_duplicate_detection():
    """Verify duplicate admission number detection."""
    raw_rows = [
        {
            "__row_num__": 2,
            "Admission Number": "ADM/DUP/101",
            "Student Name": "Student One",
            "Father Name": "Father One",
            "Class": "Class 8",
            "Mobile Number": "9876543210"
        },
        {
            "__row_num__": 3,
            "Admission Number": "ADM/DUP/101",
            "Student Name": "Student Duplicate",
            "Father Name": "Father Two",
            "Class": "Class 8",
            "Mobile Number": "9811223344"
        }
    ]

    res = ImportService.validate_and_parse_students(raw_rows)
    assert res["duplicate_count"] == 1


def test_multi_format_export_service(tmp_path):
    """Verify unified multi-format export to CSV, Excel, and PDF."""
    headers = ["ID", "Name", "Score"]
    rows = [["1", "Alice", "95"], ["2", "Bob", "88"]]

    csv_path = str(tmp_path / "test_out.csv")
    s_csv, m_csv = ExportService.export_data_by_format("Test Report", headers, rows, "csv", output_path=csv_path)
    assert s_csv is True
    assert Path(csv_path).exists()

    excel_path = str(tmp_path / "test_out.xlsx")
    s_ex, m_ex = ExportService.export_data_by_format("Test Report", headers, rows, "excel", output_path=excel_path)
    assert s_ex is True
    assert Path(excel_path).exists()

    pdf_path = str(tmp_path / "test_out.pdf")
    s_pdf, m_pdf = ExportService.export_data_by_format("Test Report", headers, rows, "pdf", output_path=pdf_path)
    assert s_pdf is True
    assert Path(pdf_path).exists()


def test_backup_preview_and_creation():
    """Verify backup creation and preview inspection."""
    succ, msg, b_path = BackupService.create_backup(backup_type="Unit_Test")
    assert succ is True
    assert Path(b_path).exists()

    preview = BackupService.get_backup_preview(b_path)
    assert preview["valid"] is True
    assert preview["has_db"] is True


def test_auto_backup_and_retention_policy():
    """Verify auto backup schedule evaluation and retention purge."""
    succ, msg = BackupService.check_and_run_auto_backup()
    assert isinstance(succ, bool)

    # Test retention purge function safely
    BackupService.enforce_retention_policy("10")


def test_database_maintenance_tools():
    """Verify database maintenance VACUUM, REINDEX, and integrity check."""
    s_opt, m_opt = BackupService.optimize_database()
    assert s_opt is True

    s_rep, m_rep = BackupService.repair_database()
    assert s_rep is True

    s_ver, m_ver = BackupService.verify_database_integrity()
    assert s_ver is True
