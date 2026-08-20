# EduLedger ERP - Bug Tracker & Deprecation Log
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Audit Date**: August 2026  

---

## 1. Tracked Warnings & Deprecations

| Issue ID | Component | Severity | Description | Temporary Workaround / Mitigation |
|---|---|---|---|---|
| **BUG-001** | `models/student.py`, `models/user.py` | LOW | `datetime.utcnow()` is deprecated in Python 3.12+ and scheduled for removal in future versions. | Currently outputs standard Python `DeprecationWarning` during unit tests. Safe for execution; should be migrated to `datetime.now(timezone.utc)` in Phase 1. |
| **BUG-002** | `controllers/auth_controller.py` | LOW | `datetime.utcnow()` used in `user.last_login = datetime.utcnow()`. | Functions properly in Python 3.12. Needs `timezone.utc` update in Phase 1. |
| **BUG-003** | `config/database.py` | LOW | Deprecation warning in SQLAlchemy SQL schema `wrap_callable` when executing `datetime.utcnow()` lambda default. | Warning emitted during database initialization; does not affect runtime database operations. |

---

## 2. Potential Edge Cases Under Observation

| Issue ID | Component | Trigger Condition | Impact | Recommended Resolution Phase |
|---|---|---|---|---|
| **EDGE-001** | `services/backup_service.py` | Restoring a DB backup while another process has an open connection to `college_fee.db`. | SQLite file lock exception during `shutil.copy2()`. | `BackupService` disposes SQLAlchemy connection pool before replacing file, but external SQLite tools (like DB Browser) must be closed. |
| **EDGE-002** | `views/receipt_view.py` | Rapid double-clicking on the "Generate Receipt" button. | Risk of generating duplicate receipts with sequential receipt numbers if UI thread freezes. | Button should be temporarily disabled upon first click until transaction completes. |
| **EDGE-003** | `services/export_service.py` | Importing CSV files with non-UTF8 encoding (e.g. ANSI / Windows-1252 with special characters). | Potential `UnicodeDecodeError` during CSV line parsing. | Add multi-encoding fallback (`utf-8-sig`, `latin-1`) in CSV reader. |
