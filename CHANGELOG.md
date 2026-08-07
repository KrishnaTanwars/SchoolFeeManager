# Changelog - School Fee Management System

All notable changes, bug fixes, database optimizations, and build updates for the **School Fee Management System**.

## [2.0.3] - Fee Table Layout, Auto-Collapse Sidebar & Demo Data Seeding

### 💳 Fee Collection Table Layout & Amount Column Visibility
- **Fixed Amount Column Width**: Set Column 3 ("Amount (₹)") minimum width to **165px** and Column 1 ("Fee Head Description") to `QHeaderView.Stretch`.
- **Zero Text Clipping**: Guaranteed full visibility for large figures (e.g. `₹ 1,25,000.00`) and spinbox controls across all screen resolutions (`1366x768`, `1600x900`, `1920x1080`) and sidebar states (expanded/collapsed).

### 📐 Sidebar Ergonomics
- **Startup Auto-Collapse**: Sidebar now always starts in the **collapsed** (`False`) state on application startup.

### 📊 Demo Data Population
- **100 Realistic Students**: Populated database with 100 students across UG (B.Pharmacy FY/SY/TY/Final Year, B.Sc, B.Com) and PG (M.Pharmacy 1st/2nd Year, M.Sc, M.Com) with unique admission numbers, roll numbers, Indian names, 10-digit mobile numbers, and addresses.
- **Complete Fee Heads**: Seeded comprehensive UG and PG fee heads (Tuition, Admission, Exam, Lab, Transport, Library, Sports, Fine).
- **350 Realistic Receipts**: Populated 350 fee receipts spread over 90 days across Cash, UPI, Card, Cheque, Demand Draft, and Net Banking payment modes with discounts, fines, and Indian number-to-words.

---

## [2.0.2] - Status Bar User Info Relocation

### 📌 ERP Layout & Status Bar Ergonomics
- **Relocated Logged-In User Label**: Moved active user information (`Logged in as: System Administrator (Admin)`) from the top header bar to the bottom-right corner of the `QStatusBar` (`addPermanentWidget`).
- **Clean Header Space**: Reserved top header bar exclusively for School Name, Academic Session, and the Global Search widget (`Search everywhere... (Ctrl+K)`), eliminating header clutter.
- **Dynamic Status Updates**: User label clears on logout and updates automatically on login with current full name and capitalized role in brackets.
- **Responsive Status Bar Typography**: Styled status bar label with subtle typography (11px, slate text, normal weight, right padding).

---

## [2.0.1] - UI Cleanup & Login Security Polish

### 🎨 Login UI Cleanup & Security Header Focus
- **Removed Pre-Authentication Global Search**: Completely removed the Global Search button (`Search everywhere... (Ctrl+K)`) and top header bar from the login screen to keep authentication clean, focused, and secure.
- **Top Margin & Spacing Optimization**: Eliminated top reserved header space on the login view, ensuring the login form card is centered in the viewport without layout shifts or blank areas.
- **Post-Login Search Visibility**: Ensured Global Search (`Ctrl+K`) and top header automatically reappear across all authenticated screens (Dashboard, Student Master, Fee Collection, Reports, Settings) post-login.
- **Keyboard Shortcut Guard**: Added authentication status check to `open_global_search()` to prevent shortcut triggering prior to user login.

---

## [2.0.0] - Phase 10 Production Ready & Final Client Release

### 🚀 Production Polish & Final Client Delivery
- **Production Versioning**: Promoted system to final semantic release version `v2.0.0` across application title bars, About software dialogs, configuration files, and documentation suite.
- **Full UI & Ergonomic Verification**: Verified consistent font scaling, zero text clipping, input heights, button dimensions, and responsive layout performance at 1366×768, 1600×900, and 1920×1080 display resolutions.
- **UX & Loading Indicators**: Added visual wait cursors (`Qt.WaitCursor`) during background PDF generation, data exports, and report compilation.
- **Global Error Handling & Logging**: Global exception hook (`sys.excepthook`) catching uncaught exceptions, writing critical traceback logs, and displaying user-friendly crash prevention dialogs.
- **Production Documentation Deliverables**: Generated `PROJECT_COMPLETION_REPORT.md`, `CLIENT_HANDOVER.md`, `KNOWN_LIMITATIONS.md`, and `RELEASE_NOTES_v2.0.0.md`.
- **Client Packaging**: Created production release bundle `release/v2.0.0/SchoolFeeManager_v2.0.0.zip` and source package `release/v2.0.0/SchoolFeeManager_Source_v2.0.0.zip`, while preserving all prior release folders (`v1.0.0` through `v1.9.0`).

---

## [1.9.0] - Phase 09 Data Management, Import/Export & Productivity Tools Release

### 📥 Bulk Student Import & Data Validation Suite
- **Interactive 3-Step Import Wizard**: Built `StudentImportDialog` supporting CSV and Excel (`.xlsx`) student file imports with drag & drop support, sample template downloads, and step-by-step progress guidance.
- **Strict Row Validation**: Pre-import validation engine checking required fields (Admission No, Student Name, Father Name, Class, Mobile Number), 10-digit mobile regex, date formatting, and session checks.
- **Duplicate Record Prevention**: Automatic duplicate detection for Admission Numbers, Roll Numbers, and Mobile Numbers against active database records and within the import file.
- **Pre-Import Preview & Row Skipping**: Interactive QTableWidget displaying row status (`Valid`, `Duplicate`, `Invalid`), issue reasons, status filter toggles, and individual row import checkboxes.
- **Downloadable Error Log**: 1-Click export of detailed CSV error logs (`Row Number`, `Column / Field`, `Reason`, `Suggested Fix`).

### 📤 Multi-Format Export Engine & Data Management
- **Student Master Exports**: Multi-format export options (`Current Filter`, `Selected Students`, `Entire Database`) to CSV, Excel (`.xlsx`), and PDF.
- **Fee Head Exports**: 1-Click export of configured Fee Category Heads to CSV, Excel (`.xlsx`), and PDF.
- **Receipt Ledger Exports**: Extended export selections (`Current Page`, `Current Filter`, `Selected Receipts`, `Entire Database`) to CSV, Excel (`.xlsx`), and PDF.

### 📦 Enhanced Backup, Pre-Restore Inspection & Auto-Backup
- **Comprehensive ZIP Backup**: Backup archives bundle database `school_fee.db`, school settings, application preferences, and system logs.
- **Pre-Restore Backup Preview**: Restoration modal inspecting backup zip contents (timestamp, file size, database presence, settings presence) before prompting for user confirmation.
- **Auto-Backup Scheduling & Retention**: Configurable auto-backup background service (Daily, Weekly, Monthly) with automated retention policy (keeping 5, 10, 20, or Unlimited backups).
- **Automatic Pre-Restore Safety Snapshot**: Automatically creates a safety backup of the active database before completing any restore operation.

### 🛠️ Database Maintenance & Diagnostic Tools
- **⚡ Database Optimization**: SQLite `VACUUM` and `ANALYZE` execution to reclaim disk space and optimize index statistics.
- **🔧 Database Repair**: SQLite `REINDEX` command to rebuild corrupted or stale database table indexes.
- **🔍 Integrity Verification**: SQLite `PRAGMA integrity_check` execution displaying complete structural diagnostic results.

### 🔍 Central Global Search & Productivity Widgets
- **Global Search Overlay (`Ctrl+K`)**: Instant search bar and `Ctrl+K` shortcut searching across Students, Receipts, Fee Heads, Reports, Admission Nos, Receipt Nos, and Mobile Nos with 1-click navigation.
- **Recent System Activity Widget**: Dashboard widget displaying the last 20 audit events with action type, timestamp, user, and description details.
- **Recently Opened Items Tracker**: Dashboard widget tracking recently viewed Students, Receipts, and Reports for 1-click quick access.

---

## [1.8.0] - Phase 08 Professional Financial Reports & Analytics Release

### 📊 Management Information System (MIS) Reports Center
- **Interactive 10-Report Dashboard Grid**: Transformed Reports module into an MIS executive reporting center featuring visual cards for 10 specialized financial and operational reports (`Daily Collection`, `Monthly Collection`, `Date Range Collection`, `Class-wise Collection`, `Course-wise Collection`, `Outstanding Fee Report`, `Student Ledger Report`, `Receipt Register Log`, `Fee Head Collection`, `Payment Mode Report`).
- **Universal Multi-Criteria Filter Panel**: Common filter panel supporting Academic Session, Course (UG/PG), Class, Section, Payment Mode, Fee Head, Date From/To, Student Admission No/Name, Receipt Number, with instant `Generate Report` and `Reset Filters` capabilities.
- **Real-Time Summary KPI Metric Panels**: Summary cards on every report displaying Total Collection, Receipt Count, Total Discounts, Total Fines, Average Receipt Amount, and Total Outstanding Dues.
- **Class-wise & Course-wise Financial Analytics**: Class-wise collection and due summaries with sorting options (`Highest Collection`, `Lowest Collection`, `Class Name`) and comparative UG vs PG course summaries.
- **Outstanding Fee & Student Ledger Engine**: Student outstanding fee balances report with status filtering (`All`, `Only Outstanding`, `Only Fully Paid`) and individual student ledger history with running balance calculation.
- **Fee Head & Payment Method Breakdown**: Collection revenue grouped by fee category heads (Tuition, Development, Laboratory, Sports, etc.) and transaction mode breakdown (Cash, UPI, Cheque, Card, Net Banking, Demand Draft).
- **Report Viewer Ergonomics**: High-performance QTableWidget views with content-aware column width auto-sizing (`resizeColumnsToContents()`), column sorting enabled, rows per page pagination (25, 50, 100, All rows per page with page controls `⏮ ◀ Page X of Y ▶ ⏭`), and live table search box.
- **Multi-Format Export & Printing Engine**: `📄 Export PDF` (ReportLab formatted report with headers and footers), `📥 Export CSV`, `📊 Export Excel`, and `🖨 Print Report` for currently filtered report datasets.

---

### ⚙️ Central Administration Panel & Category Dashboard
- **Admin Password Protection**: Enforced password authorization on Settings access (`AdminAuthDialog`), automatically logging successful and denied access attempts to system audit entries.
- **Interactive 8-Category Dashboard Grid**: Transformed Settings into a modern category dashboard with interactive visual cards (`School Information`, `User Management`, `Academic Settings`, `Database Management`, `Backup & Restore`, `Audit Log Viewer`, `Application Preferences`, `About Software`).
- **School Information & Branding**: Full profile manager for School Name, Address, City, State, PIN Code, Contact Phone(s), Email, Website, Principal Name, Logo Image selector, Academic Session, and Receipt Footer note.
- **User Management Engine**: Complete user account CRUD supporting Administrator, Operator, and Viewer roles; Active/Disabled account toggling; Admin password resets; user password changes; last login tracking; and failed login attempt counter.
- **Academic Session Settings**: Dynamic academic year manager with active session switching and new session creation.
- **Database Management Tools & Statistics**: Real-time database statistics (Path, File Size, Total Students, Receipts, Fee Heads, Users, Audit Entries); SQLite `VACUUM` and `ANALYZE` database optimization; SQLite `PRAGMA integrity_check` validation.
- **Disaster Recovery Backup & Restore**: Immediate 1-Click ZIP database backups, database restoration with automatic pre-restore safety snapshot, and backup history tracking with file sizes and author details.
- **Comprehensive Audit Log Viewer**: Interactive audit trail viewer featuring Module/Action/User/Date filtering, live text search, CSV & Excel export, and ReportLab PDF/Print report generation.
- **Application Preferences**: Configurable application defaults for Window Size, Sidebar State, Visual Themes, Auto Backup, Printers, Export/Backup folders, Currency Symbol, Date/Time Formats, and Auto-Logout timer.
- **Commercial About Software Dialog**: Enterprise system metadata page displaying Software Name, Version v1.7.0, Build Number, Python version, PySide6 GUI version, SQLite engine version, Developer credits, License terms, and dynamic Git Commit hash.

---

### 🎨 Commercial ERP Table Optimization & Preview Actions Integration
- **Actions Column Simplification**: Table row actions column simplified to contain ONLY the `👁 View` button for maximum table readability and zero row crowding.
- **Integrated Receipt Preview Dialog**: `ReceiptPreviewDialog` expanded with `🖨 Print Receipt`, `📄 Export PDF`, and `🚫 Delete Receipt (Admin Protected)` buttons.
- **Dynamic Content-Aware Table Column Sizing**: Automatic column width strategy calculating optimal widths based on longest cell value plus header label and padding (`resizeColumnsToContents()` with `Stretch` on Student Name column).
- **Bulk Action Convenience Buttons**: Dedicated `☑ Select All` and `☐ Deselect All` buttons added to top action toolbar for instant page-level row checking/unchecking.
- **High-Contrast Export Menu Styling**: Fixed dark-on-dark contrast issues in the Export dropdown menu with explicit QSS styling (`#ffffff` background, `#0f172a` text, `#e0f2fe` hover).
- **100% Filter Control Text Visibility**: Combobox popup views automatically expand (`view().setMinimumWidth(180)`) for full visibility of long items ("Net Banking / NEFT", "Demand Draft (DD)", etc.).
- **Intelligent Auto Column Width Calculation (Fee Heads Particulars Table)**: Dynamically calculates exact column widths based on `MAX(Header Width, Longest Cell Width) + 22px Padding` without stretching or distributing unallocated space. Auto-recalculates on load, record changes, course filtering, and student selection.
- **Icon-Only Pagination Controls (Receipt History)**: Replaced text pagination buttons with modern square icon buttons (`⏮`, `◀`, `▶`, `⏭`) with 38x32px dimensions, clear tooltips ("First Page", "Previous Page", "Next Page", "Last Page"), flat ERP hover styling, and disabled state opacities.

---

## [1.6.1] - Phase 06.1 Receipt History Complete UI Redesign & Responsive Layout Fix Release

### 🎨 Receipt History Commercial ERP Layout Polish & 1366x768 Responsiveness
- **1366x768 Primary Resolution Optimization**: Complete elimination of horizontal scrollbars, text clipping, control overlapping, and cropped buttons across all desktop screen sizes.
- **4 Equal Summary KPI Cards**: Re-architected KPI cards for equal width (`Today's Collection`, `Monthly Collection`, `Receipts Today`, `Filtered Total`) with zero text truncation.
- **Clean Action Toolbar**: Consolidated `Delete Selected`, `Export Ledger ▾`, and `Refresh` into a clean right-aligned top header toolbar with uniform 34px height.
- **Clean 2-Row Filter Toolbar**: Removed empty box placeholders. Expanded live search box to 380px, increased dropdown widths (Session 130px, Course 110px, Mode 140px, Status 110px) to show full values ("Net Banking", "Demand Draft", etc.).
- **Redesigned Receipt Table Columns**: Explicit column section widths (Checkbox 40px, Receipt No 140px, Date 110px, Adm No 150px, Student Name Stretch, Course 70px, Class 120px, Mode 140px, Amount 120px, Status 90px, Actions 250px).
- **Uniform 4 Inline Action Buttons**: Formatted `👁 View`, `🖨 Print`, `📄 PDF`, `🚫 Del` with equal 28px height, 4px spacing, and clean hover states inside the 250px Actions column.
- **3-Zone Bottom Footer Toolbar**: Aligned selection counter on Left, Rows per page combo & Page info in Center, and navigation controls on Right without overlapping.

---

## [1.6.0] - Phase 06 Receipt History Professionalization Release

### 💳 Commercial ERP Searchable Receipt Ledger
- **High-Performance SQL Pagination**: Sub-second responsiveness over 10,000+ receipts supporting 25, 50, 100, 200 rows per page with page navigation controls (`First`, `Prev`, `Next`, `Last`).
- **9-Field Live Multi-Criteria Search**: Instant live search while typing matching Receipt No, Admission No, Student Name, Father Name, Mobile No, Course, Class, Payment Mode, and Remarks.
- **Advanced Multi-Filter Toolbar**: Session, Course, Class, Payment Mode, Status, Date From, Date To, plus quick date presets (`Today`, `Yesterday`, `Last 7 Days`, `This Month`, `This Year`, `Reset Filters`).
- **Zero-Clipping Professional Receipt Table**: Clean column layout with explicit width allocations (`[ ] Checkbox`, `Receipt No`, `Date`, `Adm No`, `Student Name`, `Course`, `Class`, `Payment Mode`, `Amount`, `Status`, `Actions`).
- **Inline Row Actions**: Instant access to `👁 View` (ReceiptPreviewDialog), `🖨 Print` (Direct Print), `📄 PDF` (Export PDF), and `🚫 Del` (Secure Cancel/Delete).
- **Bulk Selection & Actions**: Select All checkbox, individual row checkboxes, bulk delete, bulk print, and bulk export capabilities.
- **Delete Security & Audit Logging**: Single and Bulk deletes mandate Administrator Password authorization (`AdminAuthDialog`), confirmation modal, deletion reason prompt, and log full audit entries (`SecurityService.log_audit`).
- **Multi-Format Export Engine**: Multi-format export to CSV, Excel (`.xlsx`), and ReportLab PDF Ledger reports.

---

## [1.5.4] - Phase 05.4 Professional Auto-Collapsible Navigation Sidebar Release

### 🎨 Commercial Auto-Collapsible Sidebar Navigation Shell
- **Collapsed by Default**: Application launches with navigation sidebar in collapsed state (width 60px) to maximize screen working area for tables and forms.
- **Centered Icons & Hover Tooltips**: Displays clean, centered icons (`🏠`, `💰`, `📜`, `👨‍🎓`, `🏷️`, `📊`, `⚙️`, `🔒`) with descriptive hover tooltips when collapsed.
- **Icons + Text When Expanded**: Expands to 220px displaying app title header and full item labels.
- **Smooth `QPropertyAnimation`**: 200 ms smooth transition with `QEasingCurve.InOutQuad` on Hamburger button (`☰`) click or `Ctrl+B` keyboard shortcut.
- **User Preference Storage (`QSettings`)**: Automatically persists user sidebar preference across application launches (`QSettings("SmartSchool", "SchoolFeeManager")`).
- **Workspace Auto-Expansion**: Main content view dynamically expands to occupy all gained screen width without layout clipping or horizontal scrollbars.

---

## [1.5.3] - Phase 05.3 Complete Fee Collection Layout Redesign Release

### 🎨 2-Column Commercial ERP Layout Architecture
- **LEFT COLUMN (65% Width)**: Dedicated full-height **Fee Heads Particulars** panel. The Fee Table (`table_fees`) auto-expands vertically (`stretch=1`) with Description stretching to maximum width and fixed Amount/Course columns.
- **RIGHT COLUMN (35% Width)**: Split vertically into two structured panels:
  - **Top Panel (~55% Height)**: `Student Search & Profile Summary` (Search line edit, clear button, non-activating autocomplete suggestions list, and selected student summary card).
  - **Bottom Panel (~45% Height)**: Side-by-side split (`QHBoxLayout`) containing `Real-Time Calculation Summary` on Left and `Payment Details & Actions` on Right.

### ⚙️ Usability & Component Refinements
- **Expanding Bank Dropdown**: Bank combobox width auto-expands with 260px popup view width (`State Bank of India (SBI)`, `Punjab National Bank (PNB)`, `Bank of Maharashtra`, etc. visible without truncation).
- **Single-Result Autocomplete Popup**: Minimum popup height of **72px** for 1-item search results without text clipping.
- **Responsive 1366x768 Display**: Verified 100% responsive display with zero horizontal scrollbar across 1366x768, 1600x900, and 1920x1080.

---

## [1.5.2] - Phase 05.2 Fee Collection Layout Refinement Release

### 📐 Layout Restructuring & Sidebar Alignment
- **Screen Layout Swap**: Reorganized Fee Collection screen to place Fee Particulars Table, Real-Time Calculations, and Payment Details on the **LEFT column** (stretch=6.5) and Student Search & Summary Sidebar on the **RIGHT column** (stretch=3.5) extending full vertical height without empty white space.
- **Single Result Autocomplete Popup Fix**: Enforced minimum popup height of **72px** for single matching results to prevent text truncation, clipping, or partial line visibility.
- **Popup Width Alignment**: Dynamic popup width aligned to search input width (`max(width, 450)`) with disabled horizontal scrollbar (`ScrollBarAlwaysOff`).

### 🏦 Bank Name & Payment Form Standardization
- **Bank Name Dropdown Expansion**: Configured `cmb_bank_name` with expanding size policy and popup minimum width (260px), preventing text truncation for long bank names (e.g. `State Bank of India (SBI)`, `Punjab National Bank (PNB)`, `Bank of Maharashtra`, `Central Bank of India`).
- **Payment Mode Field Toggling**: Standardized field visibility for Cash, UPI/QR, Cheque, DD, Card, and Net Banking with fixed panel stability and consistent label alignments.
- **Fixed Generate Receipt Button**: Fixed full-width high-contrast green button (`setFixedHeight(40)`) at bottom of payment panel.
- **Responsive 1366x768 Display**: Verified zero horizontal scrolling and zero vertical clipping across 1366x768, 1600x900, and 1920x1080 resolutions.

---

## [1.5.1] - Phase 05 UI/UX Fixes & Live Search Release

### ⚡ Student Search Autocomplete & Focus Fixes
- **Non-Focus-Stealing Live Autocomplete**: Reconfigured search popup window flags (`Qt.ToolTip | Qt.FramelessWindowHint` + `WA_ShowWithoutActivating`) so search input box (`txt_student_search`) **permanently retains active keyboard focus**. Users can type `R`, `Ra`, `Rah`, `Rahu`, `Rahul` naturally without focus stealing or extra clicks.
- **8-Field Comprehensive Matching**: Expanded instant search filtering across Admission Number, Student Name, Father Name, Mother Name, Mobile Number, Roll Number, Course, and Class.
- **Popup Placement & Dimensioning**: Aligned popup width **exactly** to search box width, positioned directly below search box, with height capped at ~8 visible items with vertical scrollbar.
- **Keyboard Navigation**: Smooth `Key_Down`, `Key_Up`, `Key_Enter`, `Key_Escape`, and mouse selection without stealing focus. Auto-hides popup when search text becomes empty.

### 🎨 Table & Panel UI/UX Formatting
- **Zero Amount Cropping**: Configured fixed width (150px) for Amount column with custom spinbox padding (`padding: 2px 4px`), guaranteeing values up to `₹1,50,000.00` and spinner arrows are 100% visible without overlap.
- **Redesigned Payment Details Panel**: Standardized FormLayout alignment with 105px label widths, 32px input heights, 8px spacing, and full-width `Generate & Print Receipt` button.
- **Real-Time Calculation Spacing**: Improved alignment for Subtotal, Discount, Fine, Total Payable, Actual Paid, Remaining Due, and auto-wrapping Amount in Words.
- **1366x768 Target Resolution Responsiveness**: Verified 100% responsive display with zero horizontal scrolling or clipped labels across 1366x768, 1600x900, and 1920x1080 resolutions.

---

## [1.5.0] - Phase 05 Fee Collection Professionalization Release

### 💳 Fee Collection & ERP Workflow Professionalization
- **Instant Keyboard-Navigable Autocomplete Search**: Redesigned student search using an instant floating popup suggestions list (`QListWidget` popup attached to search input) matching across Admission Number, Student Name, Father Name, Mobile Number, and Roll Number (case-insensitive). Implemented keyboard arrow navigation (Up/Down), Enter selection, and Escape dismissal.
- **Zero-Clipping Student Summary Card**: Built a full student summary card displaying Admission No, Student Name, Course, Class, Section, Father Name, Mobile, Academic Session, Status, Total Paid Till Date, and Outstanding Due with clean column widths and word wrapping to guarantee zero label clipping across 1366x768, 1600x900, and 1920x1080 resolutions.
- **Course-Based Auto Fee Filtering**: Automatically filters fee heads table according to selected student's course level (`UG` vs `PG` vs `All`). Included quick "Select All" and "Deselect All" master buttons.
- **Real-Time Calculation Engine**: Instant real-time updates for Subtotal, Discount, Fine, Total Fee Payable, Actual Paid Amount, Remaining Due Amount, and Amount in Words (Indian numbering system format) without needing calculation buttons.
- **Dynamic Payment Mode Fields & Optional Remarks**: Dynamic input fields for Cash, UPI/QR (UTR No), Cheque/DD (Cheque No, Cheque Date, Bank Name), Net Banking/NEFT/Card (Txn/Ref No), and optional Remarks.
- **Keyboard Shortcut Ergonomics**: Integrated global focus shortcut (`Alt+S` for Student Search) and save shortcut (`Ctrl+S` for Receipt Generation).
- **Automated Unit & Integration Testing**: Created `tests/test_phase5_fee_collection.py` bringing total test suite count to 47 / 47 passing (100% pass rate).

---

## [1.4.0] - Phase 04 Fee Heads Master Professionalization Release

### 🏷️ Fee Heads Master ERP Enhancements
- **Short Code Complete Removal**: Removed `code` column from database schema (`fee_categories`), forms, table displays, controllers, and exports.
- **Course Level Categorization (`UG` & `PG`)**: Added `course` classification dropdown (`UG` / `PG`) to separate Undergraduate and Postgraduate fee heads.
- **Default Seed Fee Heads**: Auto-seeds 14 UG Fee Heads (Admission Form Fee, UG Tuition Fee, UG Development Fee, Social Gathering Fee, Sports Fee, Eligibility Fee, Identity Card Fee, SRTMU Exam Fee, SRTMU GRM / Photocopy Fee, UG Laboratory Deposit, UG Club Fee, UG Laboratory Charges, Caution Money, Other Fine) and 3 PG Fee Heads (PG Tuition Fee, PG Development Fee, PG Laboratory Usage Fee).
- **Duplicate Validation Within Course**: Prevents duplicate fee head descriptions under the same course level (`UG` vs `PG`).
- **Fee Collection Course Filtering**: Integrated automatic course filtering in Receipt Collection View so selecting a student filters available Fee Heads to match the student's course level (`UG` vs `PG`).
- **6 Clean Table Columns & Instant Search**: Rendered 6 clean columns (`Description / Fee Head`, `Course`, `Default Amount`, `Status`, `Created Date`, `Actions`) with instant search and course/status dropdown filters.
- **Automated Unit Testing**: Created `tests/test_phase4_fee_heads.py` bringing test suite count to 42 / 42 passed (100% pass rate).

---

## [1.3.0] - Phase 03 Student Master Professionalization Release

### 👨‍🎓 Student Master ERP Enhancements
- **Full-Width Responsive Student Table**: Rebuilt `StudentView` table layout to occupy 100% available horizontal content space with intelligent column stretch allocation and zero text clipping across resolutions (1366x768, 1600x900, 1920x1080).
- **Side Balance Panel Removal**: Eliminated cramped side balance cards to maximize visible table columns and data rows.
- **12 Comprehensive Columns Layout**: Configured 12 structured columns in logical order: `Adm. No.`, `Roll No.`, `Student Name`, `Course / Session`, `Class`, `Sec`, `Father's Name`, `Mother's Name`, `Mobile No.`, `Status`, `Adm. Date`, and `Actions`.
- **Multi-Field Instant Filter Toolbar**: Expanded search input to perform instant case-insensitive filtering across Name, Admission No, Roll No, Father Name, Mother Name, Mobile, Course, Class, and Section. Added dedicated `Section` filter dropdown alongside `Class`, `Session`, and `Status` filters.
- **Enhanced Data Validation**: Verified unique admission number checks, 10-digit Indian mobile number format validation, required fields, and clear error banners.
- **Automated Unit Testing**: Updated `tests/test_student.py` to test multi-field search and section filtering (37 total tests passing).

---

## [1.2.0] - Phase 02 Administrator Security & Permission System Release

### 🔒 Administrator Security & Audit System
- **Central Auth Service Facade**: Created `services/admin_auth.py` providing clean facade functions (`verify_admin_password`, `show_admin_dialog`, `authenticate`) for all modules.
- **Mandatory Admin Authorization for Deletions**: Enforced `AdminAuthDialog` modal prior to deletion across Student Master, Receipt History, Fee Heads, and Fee Categories. No bypass allowed even for logged-in Admin accounts.
- **Two-Factor Delete Confirmation**: Integrated secondary explicit confirmation dialogs ("Delete [Record]? This action cannot be undone. Yes/No") immediately following password authentication.
- **Settings Access Guard**: Intercepted Settings tab navigation in `MainWindow.navigate_to()` requiring administrator password verification before rendering settings content.
- **Failed Attempt & Action Audit Persistence**: Automatically records `Failed Attempt` audit entries on wrong/empty password attempts and detailed deletion audit entries (`Student Deleted`, `Receipt Cancelled`, `Fee Category Deleted`) in the `audit_logs` SQLite table.
- **Security Debouncing & Signal Protection**: Disabled authorization action buttons during authentication processing to prevent double-clicks, rapid clicks, or signal bypasses.
- **Automated Unit Testing**: Added `tests/test_phase2_security.py` with 5 new security unit tests (36 total tests passing).

---

## [1.0.1] - Executable Repair & Critical Hotfix Release

### 🛠️ Executable & Runtime Hotfixes
- **PySide6 & Shiboken6 Dependency Bundling**: Updated `SchoolFeeManager.spec` to dynamically collect all submodules and data files for `PySide6`, `shiboken6`, `reportlab`, and `sqlalchemy` resolving PySide6 `_util` DLL loading failures.
- **Writable Directory Fallback**: Enhanced `config/app_config.py` with `_get_writable_base()` fallback logic so database, logs, exports, and backup directories fall back to `%LOCALAPPDATA%\SchoolFeeManager` if the executable installation directory is read-only.
- **Startup Crash Logging**: Added early crash logging and exception handling to prevent silent application exits during executable startup.
- **Fresh PyInstaller Compilation**: Rebuilt clean executable `dist/SchoolFeeManager/SchoolFeeManager.exe` with zero build warnings affecting runtime.

---

## [1.1.0] - Security & Administration Hardening Release (Phase 1)

### 🔒 Security & Protection Framework
- **Universal Administrator Authorization Dialog**: Created reusable modal `AdminAuthDialog` (`dialogs/admin_auth_dialog.py`) with password validation, show/hide toggle, Enter submit, Escape cancel, and error banners.
- **Delete Protection Framework**: Protected Student Delete, Fee Head Delete, Receipt Delete, and Bulk Receipt Delete operations behind Admin password authorization.
- **Settings Protection Framework**: Protected Settings view navigation behind Admin password authorization.
- **Central Security Service**: Created `SecurityService` (`services/security_service.py`) for admin password validation and audit logging.
- **Extended Audit Logging Schema**: Expanded `audit_logs` table schema via dynamic non-destructive migration to capture `module`, `status`, and `machine_name` (`socket.gethostname()`).
- **Security Unit Testing Suite**: Added `tests/test_security_phase1.py` testing admin password verification, delete protection, settings protection, and audit log persistence (100% test pass rate across 24 tests).

---

## [1.0.0] - Production Stabilization Release

### 🚀 Added
- **MVC + Service Layer Architecture**: Complete separation of models, views, controllers, and services.
- **Student Master Management**: Full CRUD operations, admission number duplicate prevention, 10-digit Indian mobile regex validation, and instant multi-field search.
- **Unlimited Fee Categories / Heads**: Dynamic fee heads management (Tuition, Admission, Transport, Computer, Lab, Hostel, Fine, Miscellaneous).
- **Fee Collection & Receipt Generator**: Real-time subtotal, discount (-), fine (+), and grand total calculation.
- **Indian Currency Number-to-Words Engine**: Handles Lakhs and Crores (e.g., *"One Lakh Fifty Thousand Rupees Only"*).
- **Commercial A4 PDF Engine**: Built with ReportLab featuring school branding header, logo, student profile grid, itemized fee table, and signatory footer.
- **Windows Direct Printing**: Native Windows Shell print routing (`os.startfile(pdf_path, 'print')`) and `QDesktopServices` PDF previewing.
- **Financial Reports**: Daily collection, monthly collection, custom date range, and class-wise collection summary with PDF and CSV export options.
- **System Settings & User Management**: Admin and Operator roles, PBKDF2 SHA-256 password hashing, school profile customization, and academic session manager.
- **Disaster Recovery**: Timestamped ZIP database backup and safety-checked restore engine.

### 🐛 Fixed & Optimized
- **SQLAlchemy Expire-on-Commit**: Set `expire_on_commit=False` and implemented relation eager loading (`joinedload`) across all controllers to resolve `DetachedInstanceError` when accessing model properties outside active DB sessions.
- **Zero-Dependency PDF Printing**: Replaced `QPdfDocument` module requirement with Windows native shell print and preview routing to run seamlessly on standard Windows installations.
- **Type Annotations & Imports**: Audited typing imports (`Optional`, `List`, `Dict`, `Tuple`, `Any`) across 43 source modules.
- **Headless E2E Test Suite**: Built automated test runner `tests/test_ui_views.py` testing 100% of workflows, views, and dialogs in offscreen mode.
