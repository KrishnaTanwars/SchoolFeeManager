# EduLedger ERP - Version History
**Current Baseline**: v1.0.0 Baseline (Semantic Versioning Standard)  

---

## Semantic Version Release Progression

### v2.0.0 — Production Ready, Final Polish & Client Delivery (Phase 10 Release)
- **Release Date**: August 2026
- **Production Delivery Features**:
  - **Production Release Baseline**: Full promotion to semantic version `v2.0.0` across application UI, window titles, About metadata, configuration objects, build specifications, and documentation suite.
  - **Responsive & Ergonomic Verification**: Zero layout clipping, consistent 1366×768 desktop optimization, loading wait cursors (`Qt.WaitCursor`), and unified button/input heights.
  - **Uncaught Crash Prevention**: Global exception hook (`sys.excepthook`) catching uncaught exceptions, writing critical traceback logs, and displaying user-friendly error dialogs.
  - **Production Release Package**: Generated clean client binary package `release/v2.0.0/SchoolFeeManager_v2.0.0.zip` and developer source package `release/v2.0.0/SchoolFeeManager_Source_v2.0.0.zip`, while preserving all prior release folders (`v1.0.0` through `v1.9.0`).
  - **Client Documentation Suite**: Generated `PROJECT_COMPLETION_REPORT.md`, `CLIENT_HANDOVER.md`, `KNOWN_LIMITATIONS.md`, and `RELEASE_NOTES_v2.0.0.md`.

### v1.9.0 — Data Management, Import/Export & Productivity Tools (Phase 9 Release)
- **Release Date**: August 2026
- **Data Management & Productivity Features**:
  - **Student Bulk Import Wizard**: 3-step CSV and Excel (`.xlsx`) import wizard with sample templates, field validation, duplicate detection (admission no, roll no, mobile), row preview table, and downloadable CSV error logs.
  - **Multi-Format Export Engine**: Student, Fee Head, and Receipt exports across CSV, Excel (`.xlsx`), and PDF formats with selection scopes (`Current Filter / Page`, `Selected Records`, `Entire Database`).
  - **Enhanced Backup & Pre-Restore Validation**: Backup archives bundling DB, settings JSON, preferences, and logs; pre-restore zip inspection modal with timestamp, size, and validity preview; automatic pre-restore safety DB backup.
  - **Auto-Backup & Retention Policy**: Scheduled auto-backup engine (Daily/Weekly/Monthly) with automated retention purging (5, 10, 20, Unlimited).
  - **Database Maintenance Suite**: SQLite `VACUUM` & `ANALYZE` optimization, `REINDEX` database repair, and `PRAGMA integrity_check` verification.
  - **Central Global Search (`Ctrl+K`)**: Header search bar and `Ctrl+K` shortcut overlay searching Students, Receipts, Fee Heads, Reports, Admission Nos, Receipt Nos, and Mobile Nos with 1-click navigation.
  - **Dashboard Productivity Widgets**: Recent System Activity widget (last 20 audit events) and Recently Opened Items tracker.

### v1.8.0 — Professional Financial Reports & Analytics (Phase 8 Release)
- **Release Date**: August 2026
- **Financial Analytics & MIS Reporting Features**:
  - **10-Category Card Reports Dashboard**: Interactive MIS reports center with visual cards (`Daily Collection`, `Monthly Collection`, `Date Range Collection`, `Class-wise Collection`, `Course-wise Collection`, `Outstanding Fee Report`, `Student Ledger Report`, `Receipt Register Log`, `Fee Head Collection`, `Payment Mode Report`).
  - **Universal Common Filter Panel**: Multi-criteria filtering supporting Academic Session, Course (UG/PG), Class, Payment Mode, Fee Head, Date Range (From/To), Student Admission No/Name, with `Generate Report` and `Reset Filters`.
  - **Real-Time Summary KPI Panels**: Summary metric cards on every report displaying Total Collection, Receipt Count, Total Discounts, Total Fines, Average Receipt Amount, and Outstanding Balance.
  - **Class-wise & Course-wise Analytics**: Revenue breakdown by class with sorting options (Highest/Lowest Collection) and separate UG vs PG collection summaries.
  - **Student Outstanding & Ledger Engine**: Complete outstanding fee balances report with status filters ("Only Outstanding", "Only Fully Paid") and complete individual student payment ledgers with running balance tracking.
  - **Fee Head & Payment Mode Breakdown**: Revenue aggregation by fee category (Tuition, Development, Lab, Sports, etc.) and transaction mode breakdown (Cash, UPI, Cheque, Card, Net Banking, Demand Draft).
  - **Report Viewer Ergonomics**: High-performance QTableWidget views with automatic content-aware column width sizing (`resizeColumnsToContents()`), column sorting, pagination controls (25, 50, 100, All rows per page with page controls `⏮ ◀ Page X of Y ▶ ⏭`), and live text search box.
  - **Multi-Format Export & Printing Engine**: `📄 Export PDF` (ReportLab formatted report), `📥 Export CSV`, `📊 Export Excel`, and `🖨 Print Report` for filtered report views.

### v1.7.0 — Professional Settings & Administration Module (Phase 7 Release)
- **Release Date**: August 2026
- **Settings & Administration Features**:
  - **Administrator Password Security**: Protected Settings navigation with `AdminAuthDialog` modal authorization, logging failed attempts to audit trail.
  - **Interactive Category Cards Dashboard**: Central control panel featuring 8 sleek commercial category cards (`School Information`, `User Management`, `Academic Settings`, `Database Management`, `Backup & Restore`, `Audit Log Viewer`, `Application Preferences`, `About Software`).
  - **School Information & Branding**: Editable fields for School Name, Address, City, State, PIN Code, Contact Numbers, Email, Website, Principal Name, Logo selector, Academic Session, and Receipt Footer note.
  - **User Management & Accounts**: Full user CRUD supporting Administrator, Operator, and Viewer roles; Active/Disabled status toggling; Admin password resets; user password changes; and login tracking.
  - **Academic Session Settings**: Manage academic years/sessions, create new sessions, and switch active operational year.
  - **Database Management & Integrity**: View real-time database statistics (Path, Size, Students, Receipts, Fee Heads, Users, Audit entries); SQLite `VACUUM` and `ANALYZE` database optimization; `PRAGMA integrity_check` database verification.
  - **Database Backup & Disaster Recovery**: 1-Click ZIP database backup, restore with automatic pre-restore safety backup, backup history table with size and author details.
  - **Audit Log Viewer**: Interactive security & administration event log viewer with Module/Action/User/Date filtering, live search, CSV & Excel export, and ReportLab PDF/Print report generation.
  - **Application Preferences**: Configurable window sizes, default sidebar state, theme presets, printer selection, backup/export folder paths, currency symbol, date/time format, and auto-logout timers.
  - **Commercial About Software Page**: Software metadata, versioning, build number, Python/Qt/SQLite runtime specs, developer credits, commercial license terms, and dynamic Git commit hash.

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

### v1.6.2 — Receipt History Final UI Polish & Table Optimization (Phase 6.2 Release)
- **Release Date**: August 2026
- **UI & Layout Features**:
  - Simplified table row actions column to contain ONLY the `👁 View` button.
  - Integrated `🖨 Print Receipt`, `📄 Export PDF`, and `🚫 Delete Receipt (Admin)` buttons inside `ReceiptPreviewDialog`.
  - Dynamic content-aware column auto-sizing (`resizeColumnsToContents()` + `Stretch` on Student Name column).
  - Dedicated `☑ Select All` and `☐ Deselect All` buttons in top action toolbar.
  - High-contrast QSS styling on Export menu (`#ffffff` background, `#0f172a` text, `#e0f2fe` hover).
  - Expanded combobox popups (`view().setMinimumWidth(...)`) for 100% text visibility.

### v1.6.1 — Receipt History Complete UI Redesign & Responsive Layout Fix (Phase 6.1 Release)
- **Release Date**: August 2026
- **UI & Layout Fixes**:
  - Complete elimination of horizontal scrollbars, text clipping, and overlapping controls at 1366x768.
  - 4 equal-width KPI summary cards (`Today's Collection`, `Monthly Collection`, `Receipts Today`, `Filtered Total`).
  - Consolidated top action toolbar (`Delete Selected`, `Export Ledger ▾`, `Refresh`).
  - Clean 2-row filter panel: 380px live search box + expanded comboboxes showing full text ("Net Banking", "Demand Draft", etc.).
  - Explicit table column section widths: Checkbox 40px, Receipt No 140px, Date 110px, Adm No 150px, Student Name Stretch, Course 70px, Class 120px, Mode 140px, Amount 120px, Status 90px, Actions 250px.
  - Uniform 4 inline action buttons (`👁 View`, `🖨 Print`, `📄 PDF`, `🚫 Del`) inside 250px Actions column.
  - 3-Zone bottom footer toolbar (Left: Selection count, Center: Rows & Page info, Right: Navigation buttons).

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
