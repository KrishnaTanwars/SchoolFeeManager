# Release Status — EduLedger ERP

## Current Release Summary
- **Current System Version**: `v2.3.0`
- **Release Phase**: Phase X — Academic Structure Refactor (Semester & Year Based ERP)
- **Target OS Platform**: Windows 10 / Windows 11 (64-bit)
- **Deployment Status**: **PRODUCTION READY**

---

## Active Phase Accomplishments
- **Dual Mode Academic ERP Engine**: Unified architecture for both **School Mode** (Class, Section, Session) and **College Mode** (Course, Branch, Academic Year, Semester, Session) across all modules.
- **Academic Masters & Controller**: Added Course, Branch, Academic Year, and Semester database models and controllers with automated seeding for B.Tech, MBA, BCA, BBA, MCA, and Class 10.
- **Reusable `AcademicFilterWidget`**: Created single-line filter component with synchronized dropdowns for Course, Branch, Academic Year, Semester, and Academic Session.
- **Student Master & Profile Cards**: Updated Student directory table, add/edit form dialogs, profile details dialog, and search filters.
- **Fee Heads & Applicable Matching Engine**: Fee category targeting by Course, Branch, Year, Semester, and Session with wildcard fallbacks.
- **Receipt Snapshots & Printable PDFs**: Receipts capture student Course, Branch, Academic Year, and Semester; printable PDF receipts display complete academic metadata.
- **Receipt History & Bulk Import/Export**: Integrated `AcademicFilterWidget` into Receipt History, updated CSV sample generation, and student import parser.
- **Seeded Demo Data & Testing**: Seeded 100 students and 350 fee receipts; passed 7/7 automated unit tests in `tests/test_phase_x_academic_structure.py` and 100% full project regression suite.
- **Standalone Build & Packaging**: Compiled executable (`dist/SchoolFeeManager/SchoolFeeManager.exe`) and created release package (`release/v2.3.0/`).

---

## Deliverables & Preservation Status
- **Release Folder Preservation**: All previous release folders (`release/v1.0.0`, `release/v1.0.1`, `release/v1.1.0`, `release/v1.2.0`, `release/v1.3.0`, `release/v1.4.0`, `release/v1.5.0`, `release/v1.6.0`, `release/v1.7.0`, `release/v1.8.0`, `release/v1.9.0`, `release/v2.0.0`, `release/v2.1.0`, `release/v2.2.0`) remain fully preserved.
- **Automated Suite**: Complete headless test suite passing cleanly.
