# EduLedger ERP - Version History
**Current Baseline**: v1.0.0 Baseline (Semantic Versioning Standard)  

---

## Semantic Version Release Progression

### v1.0.0 — Production Baseline Freeze (Phase 0 Baseline)
- **Release Date**: August 2026
- **Architecture**: Layered MVC + Service Architecture.
- **Features**:
  - Student Master Profile Management with 10-digit mobile regex validation.
  - Unlimited dynamic Fee Heads / Categories configuration.
  - Receipt Generation Engine with auto-sequenced receipt numbers (`REC/2024/00001`).
  - Indian Currency Number-to-Words converter (Lakhs & Crores).
  - ReportLab Commercial A4 PDF Receipt generator with school branding logo and signatures.
  - Native Windows Direct Printing and Print Preview (`QtPrintSupport`).
  - Flexible Partial Fee Collection & Due Tracking Engine (`paid_amount`, `due_amount`).
  - Mode-Specific Payment Details Persistence (UPI/UTR, Cheque, DD, Bank Transfer).
  - CSV Student Import Engine with sample template download tool.
  - System Security with Admin & Operator roles, PBKDF2 SHA-256 password hashing.
  - 1-Click ZIP Database Disaster Recovery Backup & Restore engine.
  - Full Audit Logging of all operational transactions.
  - Complete 26-document system baseline and 11-phase development roadmap.

### v1.6.0 — Receipt History Professionalization (Phase 6 Release)
- **Release Date**: August 2026
- **Ledger Features**:
  - Redesigned Receipt History into a commercial ERP searchable ledger.
  - SQL pagination (25, 50, 100, 200 rows per page) with page navigation controls.
  - 9-field live search matching Receipt No, Adm No, Student Name, Father Name, Mobile, Course, Class, Mode, Remarks.
  - Advanced multi-filter toolbar + quick date presets (`Today`, `Yesterday`, `Last 7 Days`, `This Month`, `This Year`, `Reset`).
  - Inline row actions: View, Print, PDF, Delete.
  - Bulk Selection, Bulk Delete, Bulk Export (CSV, Excel, PDF).
  - Admin Password protection + Deletion Reason prompt + Full Audit Logging.

### v1.5.4 — Professional Auto-Collapsible Navigation Sidebar (Phase 5.4 Release)
- **Release Date**: August 2026
- **Sidebar Features**:
  - Auto-collapsible navigation sidebar shell (width 60px collapsed / 220px expanded).
  - Collapsed by default on launch to maximize workspace area for office staff.
  - Centered icons (`🏠`, `💰`, `📜`, `👨‍🎓`, `🏷️`, `📊`, `⚙️`, `🔒`) with full hover tooltips.
  - Smooth 200ms `QPropertyAnimation` on Hamburger menu (`☰`) click or `Ctrl+B` shortcut.
  - State persistence across application restarts via `QSettings`.
  - Active screen button highlighting maintained in both collapsed and expanded states.

### v1.5.3 — Complete Fee Collection Layout Redesign (Phase 5.3 Release)
- **Release Date**: August 2026
- **Redesign Features**:
  - Restructured Fee Collection screen into a clean 2-column ERP layout matching reference design sketch.
  - Left Column (65% width): Full-height Fee Heads Particulars Table (`table_fees` stretch=1).
  - Right Column (35% width): Split vertically into Top Search/Profile Summary Panel (55% height) and Bottom Side-by-Side Calculation & Payment Details Panel (45% height).
  - Prevented long bank name clipping (`State Bank of India (SBI)`) with expanding size policy and 260px popup width.
  - Enforced 72px minimum autocomplete popup height for single-item results.
  - Verified 100% responsive display at 1366x768 resolution with zero horizontal scrolling.

### v1.5.2 — Fee Collection Layout & Usability Refinement (Phase 5.2 Release)
- **Release Date**: August 2026
- **Refinements**:
  - Layout swap: Fee Particulars & Payment Details on LEFT (stretch=6.5), Student Search & Summary Sidebar on RIGHT (stretch=3.5) consuming full vertical height without empty space.
  - Enforced minimum popup height of **72px** for single matching search results, eliminating text clipping.
  - Prevented Bank Name dropdown text truncation for long names (e.g. `State Bank of India (SBI)`) with expanding size policy and 260px popup width.
  - Standardized payment form input controls (30px height, 110px label alignment) and mode-specific field toggling.
  - Full-width fixed `Generate & Print Receipt` button at bottom of payment panel.
  - 100% responsive display at 1366x768 with zero horizontal scrollbar or vertical clipping.

### v1.5.1 — Fee Collection UI & Live Search Maintenance (Phase 5.1 Bug Fix Release)
- **Release Date**: August 2026
- **Fixes**:
  - Non-focus-stealing live student autocomplete (`Qt.ToolTip | Qt.FramelessWindowHint` + `WA_ShowWithoutActivating`). Search input permanently retains focus during typing (`R`, `Ra`, `Rah`, `Rahu`, `Rahul`).
  - 8-Field multi-criteria matching: Admission No, Student Name, Father Name, Mother Name, Mobile No, Roll No, Course, Class.
  - Popup width aligned **exactly** to search box, positioned directly below, capped at ~8 visible items with vertical scrollbar.
  - Fixed Amount column width (150px) and spinbox padding (`padding: 2px 4px`) to prevent text clipping and spinner overlap up to `₹1,50,000.00`.
  - Redesigned Payment Details panel with standardized label widths, input heights, and full-width Generate & Print Receipt button.
  - Responsive layout verified at 1366x768 with zero horizontal scrolling.

### v1.5.0 — Fee Collection Professionalization (Phase 5 Release)
- **Release Date**: August 2026
- **Features**:
  - Instant Keyboard-Navigable Autocomplete Search overlay widget matching Admission No, Name, Father Name, Mobile, and Roll No.
  - Zero-Clipping Student Summary Profile Card with word wrapping and clean layout for 1366x768, 1600x900, 1920x1080 resolutions.
  - Automatic Course-Based Fee Filtering (`UG` vs `PG` vs `All`) matching selected student.
  - Real-Time Calculation Engine instantly updating Subtotal, Discount, Fine, Total, Paid Amount, Due, and Amount in Words.
  - Dynamic Payment Mode Inputs (Cash, UPI UTR, Cheque/DD, Net Banking/NEFT/Card) & Optional Remarks.
  - High-Speed ERP Ergonomics with Keyboard Shortcuts (`Alt+S` Search, `Ctrl+S` Generate).

### v1.4.0 — Fee Heads Master Professionalization (Phase 4 Release)
- **Release Date**: August 2026
- **Features**:
  - Short Code Complete Removal across database schema, forms, table headers, and CSV exports.
  - Course Classification (`UG` & `PG`) separating Undergraduate and Postgraduate fee heads.
  - Default Seeding of 14 UG Fee Heads and 3 PG Fee Heads.
  - Duplicate Validation within course level (`UG` vs `PG`).
  - Fee Collection Course Filtering automatically matching student's course level (`UG` vs `PG`).
  - 6 Clean Table Columns (`Description`, `Course`, `Default Amount`, `Status`, `Created Date`, `Actions`) with instant multi-field search and filters.

### v1.3.0 — Student Master Professionalization (Phase 3 Release)
- **Release Date**: August 2026
- **Features**:
  - Full-Width Responsive Student Table with 100% space utilization across all desktop screen resolutions.
  - 12 Responsive Columns: Admission No, Roll No, Student Name, Course/Session, Class, Section, Father Name, Mother Name, Mobile, Status, Admission Date, Actions.
  - Side Balance Panel Removal for uncluttered data display.
  - Multi-Field Instant Filter (Name, Adm No, Roll No, Father/Mother Name, Mobile, Course, Class, Section).
  - Dedicated Section filter dropdown.
  - Enhanced Form Validation & Error Banners.
  - 37 / 37 Unit Tests Passing.

---

## Planned Semantic Releases

- **v1.1.0 (Phase 1)**: Code Modernization & Centralized Validation
- **v1.2.0 (Phase 2)**: Advanced Student Management & Photo Uploads
- **v1.3.0 (Phase 3)**: Fee Structure & Penalty Rules Engine
- **v1.4.0 (Phase 4)**: Digital Payment Gateway & QR Code Invoicing
- **v1.5.0 (Phase 5)**: Financial BI Analytics & Executive Dashboards
- **v1.6.0 (Phase 6)**: Granular Role-Based Access Control (RBAC)
- **v1.7.0 (Phase 7)**: Multi-Branch & Multi-Campus Enterprise Architecture
- **v1.8.0 (Phase 8)**: Staff Master, Payroll & Expense ERP Module
- **v1.9.0 (Phase 9)**: Cloud Sync & Hybrid Offline Engine
- **v2.0.0 (Phase 10)**: Mobile Companion App & Parent Portal (Major Production Release)
