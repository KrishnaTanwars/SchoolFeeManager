# Changelog - School Fee Management System

All notable changes, bug fixes, database optimizations, and build updates for the **School Fee Management System**.

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
