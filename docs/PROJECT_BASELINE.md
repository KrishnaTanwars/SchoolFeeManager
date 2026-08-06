# EduLedger ERP - Project Baseline Document
**Version**: 2.0.0 (Enterprise Edition - Phase 0 Baseline)  
**Target Platform**: Windows 10 / Windows 11 (64-bit Desktop)  
**Status**: Baseline Frozen (Phase 0 Complete)  
**Date**: August 2026  

---

## 1. Executive Summary

**EduLedger ERP** (internally structured as **SchoolFeeManager**) is a production-grade, offline-first commercial Windows Desktop ERP system engineered specifically for Indian Schools, Colleges, Coaching Institutes, and Educational Organizations. 

The software manages the entire student life-cycle within the institution, including student admission, student master profile maintenance, dynamic fee head configuration, multi-item fee collection, discount and fine application, partial payment due tracking, automated Indian currency word conversion (Lakhs & Crores), high-resolution ReportLab A4 PDF receipt generation, native Windows printing, financial summary reporting, multi-format export (CSV/Excel/PDF), user role-based access control, disaster recovery backup/restore, and detailed audit logging.

This document represents the official **Phase 0 System Baseline**. No further changes to source code will take place during Phase 0; this baseline serves as the immutable foundation for all future enhancement phases.

---

## 2. Core System Metadata

| Metric / Parameter | Value / Detail |
|---|---|
| **Product Name** | EduLedger ERP (School Fee Management System) |
| **Current Baseline Version** | `2.0.0` (Enterprise Release 2) |
| **System Architecture** | Layered Model-View-Controller (MVC) + Service Architecture |
| **Primary Programming Language** | Python 3.12.10 (64-bit) |
| **GUI Framework** | PySide6 6.11.1 (Qt 6 for Python) |
| **Database Engine & ORM** | SQLite 3.49.1 with SQLAlchemy 2.0.51 ORM |
| **Document Generation Engine** | ReportLab 5.0.0 |
| **Executable Compiler** | PyInstaller 6.21.0 |
| **Installer Compiler** | Inno Setup Compiler v6.x (`installer.iss`) |
| **Total Source Files (Python)** | 49 files |
| **Total Lines of Code (LOC)** | 6,256 lines |
| **Active DB Tables** | 8 tables (`students`, `receipts`, `receipt_items`, `fee_categories`, `users`, `school_information`, `academic_sessions`, `audit_logs`, `backup_history`) |
| **Main UI Views** | 9 screens |
| **Modal Dialogs** | 5 dialogs |
| **Automated Test Suite** | 18 unit & integration tests (100% pass rate) |
| **Standalone Executable** | `release_v2.0/SchoolFeeManager/SchoolFeeManager.exe` (9.77 MB) |

---

## 3. High-Level Architectural Overview

EduLedger ERP utilizes a strict separation of concerns through a layered architecture:

```
+-----------------------------------------------------------------------+
|                            PRESENTATION LAYER                         |
|  PySide6 Views (dashboard, student, receipt, fee_category, etc.)      |
|  PySide6 Dialogs (student_dialog, receipt_preview, student_ledger)    |
+-----------------------------------+-----------------------------------+
                                    | Signals / Slots / Events
                                    v
+-----------------------------------------------------------------------+
|                            CONTROLLER LAYER                           |
|  AuthController, StudentController, ReceiptController,                |
|  FeeController, ReportController, SettingsController                   |
+-----------------------------------+-----------------------------------+
                                    | Business Operations & Validation
                                    v
+-----------------------------------+-----------------------------------+
|     SERVICE & UTILITY LAYER       |          DATA MODEL LAYER         |
|  PDFService, PrintService,        |  SQLAlchemy ORM Models            |
|  BackupService, ExportService,    |  (Student, Receipt, User,         |
|  NumberToWords, Security, Logger  |   FeeCategory, Settings, etc.)    |
+-----------------------------------+-----------------------------------+
                                    | DB Sessions & Queries
                                    v
+-----------------------------------------------------------------------+
|                             DATABASE LAYER                            |
|        SQLite Database Engine (school_fee.db - WAL / Foreign Keys)    |
+-----------------------------------------------------------------------+
```

### Key Architectural Strengths:
1. **Thread-Safe DB Session Scoping**: Uses `scoped_session` with `expire_on_commit=False` to prevent `DetachedInstanceError` across UI threads.
2. **Dynamic Foreign Key Enforcement**: Executes `PRAGMA foreign_keys=ON;` on every connection establishing relational integrity in SQLite.
3. **Zero External Runtime Dependency**: ReportLab handles PDF creation directly without relying on external system tools (like Chrome or Acrobat), and printing routes via Windows Shell (`os.startfile(path, 'print')`).
4. **Headless Testing Capability**: Complete UI test coverage achievable using `QApplication` in offscreen mode.

---

## 4. Phase 0 Audit Verification Summary

| Component | Status | Verification Result |
|---|---|---|
| **Source Code Modification** | FROZEN | 0 files edited during Phase 0 audit |
| **Unit Test Suite** | PASSED | 18 / 18 tests executed cleanly in 1.24s |
| **Database Schema** | VERIFIED | 8 core tables with migration runner verified |
| **Standalone Packaging** | VERIFIED | `release_v2.0/SchoolFeeManager/SchoolFeeManager.exe` launch verified |
| **Documentation Baseline** | GENERATED | 23 comprehensive baseline documents generated |

---

## 5. Next Steps for Developer Handover

Any incoming engineer must review:
1. [PROJECT_HANDOVER.md](file:///e:/Downloads/ERP/SchoolFeeManager/docs/PROJECT_HANDOVER.md) for onboarding and execution steps.
2. [ARCHITECTURE.md](file:///e:/Downloads/ERP/SchoolFeeManager/docs/ARCHITECTURE.md) for structural patterns and database session lifecycle.
3. [ROADMAP.md](file:///e:/Downloads/ERP/SchoolFeeManager/docs/ROADMAP.md) for Phase 1 through Phase 10 execution sequence.
