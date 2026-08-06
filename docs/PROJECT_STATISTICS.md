# EduLedger ERP - Project Statistics & Metrics
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Audit Date**: August 2026  

---

## 1. High-Level Summary Statistics

```
===============================================================================
PROJECT METRICS SUMMARY
===============================================================================
Project Name                      : EduLedger ERP (School Fee Management System)
Current Release Version           : v2.0.0 (Enterprise Edition)
Target Operating System           : Windows 10 / Windows 11 (64-bit Desktop)
Primary Programming Language      : Python 3.12.10
GUI Engine                        : PySide6 6.11.1 (Qt 6)
Database ORM & Engine             : SQLAlchemy 2.0.51 + SQLite 3.49.1
Document Generator                : ReportLab 5.0.0
Packaging & Installer             : PyInstaller 6.21.0 + Inno Setup 6.x

Directory / Folder Count          : 16 directories
Python File Count (.py)           : 49 source files
Markdown File Count (.md)         : 5 root docs + 23 baseline docs = 28 files
Total Lines of Python Code (LOC)  : 6,256 LOC
Primary UI Views / Screens        : 9 screens
Modal Input & Preview Dialogs     : 5 dialogs
Controller Modules                : 6 controllers
Services                          : 5 specialized services
Utility Modules                   : 5 utilities
Database Tables                   : 8 active ORM tables
Automated Unit Tests              : 18 passed tests (0 failures)
Compiled Executable Size          : 9.77 MB (dist/SchoolFeeManager/SchoolFeeManager.exe)
===============================================================================
```

---

## 2. Directory Breakdown & File Metrics

| Directory Path | File Count | Primary Responsibility |
|---|---|---|
| `.` (Project Root) | 18 files | Main entry, PyInstaller spec, build scripts, guides, icons |
| `config/` | 2 files | Application configurations & database connection management |
| `models/` | 7 files | SQLAlchemy ORM entity model definitions |
| `controllers/` | 6 files | Business logic, transaction orchestration & controllers |
| `views/` | 9 files | PySide6 UI view widgets and main window frame |
| `dialogs/` | 5 files | PySide6 modal dialog windows |
| `services/` | 5 files | PDF generation, printing, backups, CSV exports, seeding |
| `utils/` | 5 files | Currency conversion, security hashing, background workers, logging |
| `tests/` | 5 files | Automated unit & integration test runner files |
| `assets/` | 2 files | Style sheets (`theme.qss`) & institution branding logos |
| `docs/` | 20 files | Phase 0 baseline system documentation |
| `phases/PHASE_00/` | 3 files | Phase 0 phase control & audit summary reports |

---

## 3. Code Metrics Breakdown by Layer

| Component Layer | File Count | Approximate LOC | % of Total Codebase |
|---|---|---|---|
| **Views & Dialogs (UI Layer)** | 14 files | 2,750 LOC | 44.0 % |
| **Controllers (Business Layer)** | 6 files | 1,280 LOC | 20.5 % |
| **Services Layer** | 5 files | 950 LOC | 15.2 % |
| **Models & Config Layer** | 9 files | 420 LOC | 6.7 % |
| **Utilities & Helpers** | 5 files | 380 LOC | 6.0 % |
| **Unit & Integration Tests** | 5 files | 476 LOC | 7.6 % |
| **Total** | **49 files** | **6,256 LOC** | **100.0 %** |
