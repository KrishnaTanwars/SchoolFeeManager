# Changelog - School Fee Management System

All notable changes, bug fixes, database optimizations, and build updates for the **School Fee Management System**.

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
