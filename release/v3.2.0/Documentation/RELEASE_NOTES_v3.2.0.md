# Release Notes — EduLedger ERP v3.2.0

**Release Date**: August 17, 2026  
**Version**: `v3.2.0`  
**Platform**: Windows 10 / Windows 11 (64-bit)

---

## Key Highlights & Fixes

### 1. Database Schema Auto-Migration Guard (`course_category`)
- **Issue Resolved**: When upgrading an existing installation where a pre-existing SQLite database file (`school_fee.db`) was present, SQLAlchemy queries failed with `(sqlite3.OperationalError) no such column: students_1.course_category`.
- **Root Cause**: While SQLAlchemy's `Base.metadata.create_all()` creates missing tables for new installations, it does not alter pre-existing tables. The `run_migrations()` function in `config/database.py` handles runtime schema migrations, but was missing an explicit column check for `course_category`.
- **Fix Implemented**: Added column check and dynamic table alteration in `run_migrations()`:
  ```python
  if "course_category" not in student_cols:
      cursor.execute("ALTER TABLE students ADD COLUMN course_category VARCHAR(20) DEFAULT 'UG';")
  ```
- **Seamless Upgrade**: Client installations with existing data will automatically migrate the database schema upon launch without losing any student records or fee history.

---

## Deliverables & Distribution
- **Windows Installer Setup**: `release/v3.2.0/Installer/SchoolFeeERP_Setup_v3.2.0.exe`
- **Portable Distribution**: `release/v3.2.0/Portable/SchoolFeeERP_Portable_v3.2.0.zip`
- **Developer Source Package**: `release/v3.2.0/Developer/SchoolFeeERP_Source_v3.2.0.zip`
- **Checksums**: SHA256 & MD5 verification hashes in `release/v3.2.0/Checksums/`
