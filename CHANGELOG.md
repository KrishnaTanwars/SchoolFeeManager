# Changelog - School Fee Management System

All notable changes, bug fixes, database optimizations, and build updates for the **School Fee Management System**.

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
