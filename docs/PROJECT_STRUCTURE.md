# EduLedger ERP - Project Structure & Directory Reference
**Baseline Version**: 2.0.0 (Enterprise Edition)  

---

## Complete Workspace Directory Tree

```
CollegeFeeManager/
├── .gitignore               # Git source exclusion rules
├── build.py                 # PyInstaller build orchestration script
├── package_release.py       # Release ZIP archive generator
├── main.py                  # Primary application entry point & QApplication lifecycle
├── CollegeFeeManager.spec    # PyInstaller packaging configuration
├── installer.iss            # Inno Setup Windows installer compiler script
├── seed_dummy_data.py       # Dummy data populator for testing
├── generate_pdf_docs.py     # PDF documentation generator script
├── Version.txt              # Release version information file
├── License.txt              # Software license file
├── README.md                # General introduction & quick start guide
├── CHANGELOG.md             # High-level version history changelog
├── DEVELOPER_GUIDE.md       # Basic developer setup instructions
├── INSTALLATION_GUIDE.md    # End-user installation guide
├── USER_MANUAL.md           # End-user user manual guide
├── CHANGES1.mp4             # Demonstration video artifact
│
├── assets/                  # UI Static Assets & Styling
│   ├── school_logo.png      # Default institution branding logo
│   └── styles/
│       └── theme.qss        # Custom PySide6 QSS stylesheet rules
│
├── config/                  # Application Configurations
│   ├── app_config.py        # Storage directory paths & runtime environment constants
│   └── database.py          # SQLAlchemy engine, session maker & SQLite pragmas
│
├── models/                  # Declarative SQLAlchemy ORM Models (8 Tables)
│   ├── base.py              # Declarative base class declaration
│   ├── user.py              # User authentication model
│   ├── student.py           # Student profile master model
│   ├── fee_category.py      # Fee category / head model
│   ├── receipt.py           # Receipt and itemized receipt items models
│   ├── settings.py          # Academic sessions and school information models
│   └── audit.py             # Audit log and backup history models
│
├── controllers/             # Business Logic & Controller Layer
│   ├── auth_controller.py   # Login authentication & credential hashing
│   ├── student_controller.py# Student CRUD, search queries & CSV import logic
│   ├── receipt_controller.py# Fee collection, due calculation & ledger queries
│   ├── fee_controller.py    # Fee heads CRUD operations
│   ├── report_controller.py # Financial metrics aggregation & breakdown calculations
│   └── settings_controller.py# School profile update & session management
│
├── views/                   # PySide6 GUI Widgets & Main Window Layouts
│   ├── main_window.py       # Main application frame & sidebar menu shell
│   ├── login_view.py        # Authentication login screen widget
│   ├── dashboard_view.py    # Executive KPI dashboard widget
│   ├── student_view.py      # Student master management grid widget
│   ├── receipt_view.py      # Fee collection & payment form widget
│   ├── receipt_history_view.py# Historic receipts ledger widget
│   ├── fee_category_view.py # Fee heads configuration grid widget
│   ├── report_view.py       # Collection reports & export panel widget
│   └── settings_view.py     # System administration & backup center widget
│
├── dialogs/                 # PySide6 Modal Input & Statement Dialogs
│   ├── student_dialog.py    # Add/Edit student profile modal form
│   ├── fee_category_dialog.py# Add/Edit fee head modal form
│   ├── receipt_preview_dialog.py# PDF receipt rendering & print preview modal
│   ├── student_ledger_dialog.py# Complete student fee statement modal
│   └── user_dialog.py       # User account creation/edit modal
│
├── services/                # Specialized Technical Services
│   ├── pdf_service.py       # ReportLab A4 PDF receipt generator
│   ├── print_service.py     # Direct Windows shell printer integration
│   ├── backup_service.py    # ZIP backup creation & database restoration engine
│   ├── export_service.py    # CSV export & sample CSV template generator
│   └── db_seed.py           # Initial database seeder for admin user & fee heads
│
├── utils/                   # Helper Libraries & Shared Utilities
│   ├── helpers.py           # Currency formatting & UI dialog helpers
│   ├── logger.py            # Rotating file logging setup
│   ├── number_to_words.py   # Indian Currency word converter (Lakhs & Crores)
│   ├── security.py          # PBKDF2 SHA-256 password hashing utility
│   └── workers.py           # PySide6 QThread background worker threads
│
├── tests/                   # Automated Unit & Integration Tests
│   ├── test_database.py     # Database engine & table creation tests
│   ├── test_number_to_words.py# Indian currency converter tests
│   ├── test_student.py      # Student controller unit tests
│   ├── test_ui_views.py     # Offscreen PySide6 UI rendering tests
│   └── test_v11_features.py # Partial fee collection, CSV & migration integration tests
│
├── database/                # SQLite Local Database Storage
│   └── college_fee.db        # Active SQLite database file
│
├── backup/                  # Disaster Recovery ZIP Backups Directory
├── exports/                 # PDF Receipts & CSV Reports Exports Output Directory
├── logs/                    # Application Log Output Directory (`app.log`)
│
├── docs/                    # Phase 0 System Baseline Documentation (20 Files)
└── phases/                  # Multi-Phase ERP Control Documentation
    └── PHASE_00/            # Phase 0 Phase Reports & Checklists (3 Files)
```
