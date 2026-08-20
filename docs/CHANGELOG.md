# EduLedger ERP - Baseline Changelog
All notable changes, features, optimizations, and bug fixes for **EduLedger ERP** (College Fee Management System).

---

## [2.0.0] - Phase 0 Frozen Baseline Release (2026-07-27)

### 🚀 Added
- **Flexible Partial Fee Collection Engine**: Added support for partial payments with dynamic due tracking (`paid_amount`, `due_amount`).
- **Dynamic Payment Details Database Fields**: Added persistence for `utr_number`, `cheque_number`, `cheque_date`, `bank_name`, and `payment_date` across database receipts and PDF layouts.
- **CSV Student Import & Template Generator**: Integrated bulk student CSV import with error logging and sample CSV template generator (`ExportService.generate_sample_student_csv()`).
- **Class & Course Analytics**: Added student distribution queries and charts on dashboard.
- **Dynamic Schema Migration Engine**: Automatic non-destructive column additions via SQLite pragma table inspection (`config/database.py`).
- **ReportLab Watermark Engine**: Conditional PDF watermark rendering based on receipt status (`PAID` vs `DUAL / PARTIAL`).

### 🐛 Fixed & Optimized
- **SQLAlchemy Session DetachedInstanceError**: Implemented `expire_on_commit=False` and eager loading (`joinedload`) across controllers.
- **Zero-Dependency PDF Printing**: Replaced `QPdfDocument` module requirement with Windows native shell print and preview routing (`os.startfile(pdf_path, 'print')`).
- **Headless Testing**: E2E automated test runner supporting Qt offscreen mode.
- **Packaging**: Created PyInstaller build orchestration script (`build.py`) and release packager (`package_release.py`).
