# EduLedger ERP - Developer Handover Guide
**Target Audience**: Senior Software Engineers / Maintainers  
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**System OS**: Windows 10 / Windows 11 (64-bit)  

---

## 1. Welcome & Onboarding Overview

This document provides complete technical orientation for incoming software engineers inheriting the **EduLedger ERP** codebase. The primary design objective of this system is **offline stability, zero-runtime-crash operation, fast local transaction processing, and clean maintainability**.

As of **Phase 0**, the current codebase state is fully audited, functionally stable, and frozen.

---

## 2. Workspace Setup & Environment Guide

### Prerequisites
- **Operating System**: Windows 10 / Windows 11 (64-bit recommended)
- **Python**: Version `3.12.x` (64-bit)
- **C++ Compiler**: Microsoft Visual C++ Redistributable 2015-2022 (required by PySide6 binaries)
- **Inno Setup**: Version `6.x` (optional, for compiling standard Windows `.exe` installers)

### 1-Click Environment Setup Commands
Run the following commands in PowerShell from the project root:

```powershell
# 1. Verify Python Version
python --version
# Expected: Python 3.12.x

# 2. Create Virtual Environment (Optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install Core Production Dependencies
pip install PySide6==6.11.1 SQLAlchemy==2.0.51 reportlab==5.0.0 pyinstaller==6.21.0

# 4. Initialize Database & Launch Application
python main.py

# 5. Run Full Automated Test Suite
python -m unittest discover tests
```

---

## 3. Core Project Directory Structure

```
CollegeFeeManager/
├── main.py                  # Primary Application Entry Point & PySide6 App Lifecyle
├── build.py                 # PyInstaller Build Orchestration Script
├── package_release.py       # Release ZIP & Document Packaging Engine
├── CollegeFeeManager.spec    # PyInstaller Bundling Specification
├── installer.iss            # Inno Setup Windows Installer Script
│
├── config/                  # App Settings & DB Initialization
│   ├── app_config.py        # Environment Paths & Storage Directory Setup
│   └── database.py          # SQLAlchemy Engine, Session Maker & Pragma Hooks
│
├── models/                  # SQLAlchemy ORM Data Models (8 Tables)
│   ├── base.py              # Declarative Base
│   ├── user.py              # User authentication & roles
│   ├── student.py           # Student master profile
│   ├── fee_category.py      # Fee heads / categories
│   ├── receipt.py           # Receipts & Receipt items
│   ├── settings.py          # Academic sessions & School info
│   └── audit.py             # Audit logging & Backup tracking
│
├── controllers/             # Business Logic & DB Manipulation Layer
│   ├── auth_controller.py   # Login, Session & Role Validation
│   ├── student_controller.py# Student CRUD, Search & CSV Import
│   ├── receipt_controller.py# Fee Collection, Partial Payment & Ledger
│   ├── fee_controller.py    # Fee Category CRUD
│   ├── report_controller.py # Financial Aggregations & Summary Calculations
│   └── settings_controller.py# College Profile & Session Management
│
├── views/                   # PySide6 GUI Widgets & Main Window Layouts
│   ├── main_window.py       # Main Application Shell & Sidebar Navigation
│   ├── login_view.py        # Authentication Screen
│   ├── dashboard_view.py    # KPI Metrics & Today's Analytics
│   ├── student_view.py      # Student Management Grid
│   ├── receipt_view.py      # Fee Collection Form & Payment Input
│   ├── receipt_history_view.py# Issued Receipt Log & Reprint/Cancel
│   ├── fee_category_view.py # Fee Heads Management
│   ├── report_view.py       # Collection Reports & Export Buttons
│   └── settings_view.py     # System Configuration & Backup Center
│
├── dialogs/                 # Modal Popup Dialogs
│   ├── student_dialog.py    # Add/Edit Student Modal
│   ├── fee_category_dialog.py# Add/Edit Fee Category Modal
│   ├── receipt_preview_dialog.py# PDF Print Preview Dialog
│   ├── student_ledger_dialog.py# Complete Student Fee Statement Modal
│   └── user_dialog.py       # User Management Modal
│
├── services/                # Specialized Utility Services
│   ├── pdf_service.py       # ReportLab PDF Generation Engine
│   ├── print_service.py     # Direct Windows Shell Printing
│   ├── backup_service.py    # ZIP Backup & Restore Safety Engine
│   ├── export_service.py    # CSV Data Exporter & Sample Template Generator
│   └── db_seed.py           # Default Seed Data Generator (Admin user, default fee categories)
│
├── utils/                   # Helper Modules & Core Libraries
│   ├── helpers.py           # Currency formatting & UI utility functions
│   ├── logger.py            # Rotating file logging configuration
│   ├── number_to_words.py   # Indian Currency Word Converter (Lakhs & Crores)
│   ├── security.py          # PBKDF2 SHA-256 password hashing
│   └── workers.py           # Qt Threading Background Workers
│
├── tests/                   # Automated Unit & Integration Tests
│   ├── test_database.py     # DB Connection & ORM Tests
│   ├── test_number_to_words.py# Currency Word Conversion Tests
│   ├── test_student.py      # Student CRUD Logic Tests
│   ├── test_ui_views.py     # Offscreen PySide6 UI Rendering Tests
│   └── test_v11_features.py # Partial Payment, CSV & Migration Tests
│
├── docs/                    # Phase 0 Baseline System Documentation
└── phases/                  # Multi-Phase Project Development Control Documentation
```

---

## 4. Operational Handover Rules & Guidelines

1. **Do NOT break DB Threading Safety**: Always retrieve DB sessions via `get_db()` inside controller functions and close them in `finally:` blocks.
2. **Do NOT use `expire_on_commit=True`**: SQLAlchemy models are intentionally loaded with `expire_on_commit=False` and explicit eager loading (`joinedload`) to prevent UI thread detaching issues when Qt table views access properties after session closure.
3. **Preserve Indian Currency Conversion**: When updating receipts, ensure `amount_in_words` is computed using `utils.number_to_words.amount_in_words_indian()`.
4. **Follow Phase Roadmap**: Future updates MUST follow the roadmap in [ROADMAP.md](file:///e:/Downloads/ERP/CollegeFeeManager/docs/ROADMAP.md).
