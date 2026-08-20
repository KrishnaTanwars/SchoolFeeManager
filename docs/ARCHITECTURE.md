# EduLedger ERP - System Architecture Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Architectural Style**: Layered Model-View-Controller (MVC) with Service Pattern  

---

## 1. Architectural Blueprint

EduLedger ERP is designed as a clean 4-tier desktop application architecture:

```
[ PySide6 UI Views & Dialogs ]
           │
           ▼
[ Controller Layer (Business Logic & Validation) ]
      │             │
      ▼             ▼
[ Services ]   [ SQLAlchemy ORM Models ]
      │             │
      └──────┬──────┘
             ▼
[ SQLite Database Engine (college_fee.db) ]
```

---

## 2. Layer-by-Layer Architecture Analysis

### A. Presentation Layer (Views & Dialogs)
- **Technology**: PySide6 (`QtWidgets`, `QtGui`, `QtCore`, `QtPrintSupport`).
- **Core Container**: `MainWindow` ([views/main_window.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/main_window.py)) provides a desktop frame with a sidebar navigation layout (`QListWidget`), header bar showing logged-in user and current academic session, and a `QStackedWidget` central viewing area.
- **Views**: Each functional module is implemented as a standalone `QWidget` subclass (`DashboardView`, `StudentView`, `ReceiptView`, `ReceiptHistoryView`, `FeeCategoryView`, `ReportView`, `SettingsView`).
- **Dialogs**: Modal inputs and statement previews use `QDialog` subclasses (`StudentDialog`, `FeeCategoryDialog`, `ReceiptPreviewDialog`, `StudentLedgerDialog`, `UserDialog`).

### B. Controller Layer (Application Logic)
- **Controllers**: Stateless static class controllers (`StudentController`, `ReceiptController`, `FeeController`, `ReportController`, `SettingsController`, `AuthController`).
- **Responsibilities**:
  1. Receive event calls from PySide6 UI views.
  2. Validate user input (e.g. mobile Regex, duplicate admission numbers, positive fee amounts).
  3. Manage scoped SQLAlchemy DB sessions.
  4. Perform atomic transactions (`commit` / `rollback`).
  5. Format data structures into dictionaries/objects returned to UI views.
  6. Trigger audit log insertion via `AuditLog`.

### C. Service Layer (Specialized Utilities)
- `PDFService` ([services/pdf_service.py](file:///e:/Downloads/ERP/CollegeFeeManager/services/pdf_service.py)): Uses ReportLab (`SimpleDocTemplate`, `Table`, `Paragraph`, `Drawing`) to render A4 fee receipt PDFs with watermarking and payment breakdown.
- `PrintService` ([services/print_service.py](file:///e:/Downloads/ERP/CollegeFeeManager/services/print_service.py)): Integrates with native Windows Shell (`os.startfile(pdf_path, 'print')`) for direct thermal or desktop printer routing.
- `BackupService` ([services/backup_service.py](file:///e:/Downloads/ERP/CollegeFeeManager/services/backup_service.py)): Handles timestamped ZIP archive creation of `college_fee.db`, plus safe backup restore with DB connection release.
- `ExportService` ([services/export_service.py](file:///e:/Downloads/ERP/CollegeFeeManager/services/export_service.py)): Formats financial summaries and student records into CSV/Excel compatible outputs.
- `DBSeedService` ([services/db_seed.py](file:///e:/Downloads/ERP/CollegeFeeManager/services/db_seed.py)): Populates standard default fee heads, admin user credentials, and initial school configuration on first launch.

### D. Data Access Layer (ORM & DB Engine)
- **Engine**: SQLite 3 with `college_fee.db`.
- **ORM**: SQLAlchemy declarative models extending `models.base.Base`.
- **Pragmas**: Enables SQLite foreign key constraints (`PRAGMA foreign_keys=ON;`) and memory journal mode for optimal desktop performance.

---

## 3. Communication & Data Flow Sequence

### Example Transaction: Issuing Fee Receipt & PDF Generation

```
[ User Clicks "Issue Receipt" ]
         │
         ▼
[ ReceiptView.submit_receipt() ]
         │ (Gathers UI form inputs: student_id, items, payment_mode, paid_amount)
         ▼
[ ReceiptController.create_receipt() ]
         │ 1. Opens Scoped DB Session
         │ 2. Computes Subtotal, Discount, Fine, Total, Due
         │ 3. Converts Paid Amount to Words via number_to_words.py
         │ 4. Generates unique Receipt Number (e.g., REC/2024/00001)
         │ 5. Inserts Receipt + ReceiptItems into DB
         │ 6. Writes AuditLog entry
         │ 7. Commits DB Transaction
         ▼
[ PDFService.generate_receipt_pdf() ]
         │ Builds A4 PDF using ReportLab Platypus engine
         ▼
[ UI Preview / Print Trigger ]
         │ Displays ReceiptPreviewDialog with options to Print or Download PDF
```

---

## 4. Architectural Safeguards & Multi-Threading

1. **Qt UI Thread Separation**: All UI operations run on the main PySide6 GUI thread. Heavy export operations or backup compression can utilize `utils.workers.WorkerThread` (`QThread`) to prevent UI freezes.
2. **SQLite Single-Writer Model**: Concurrent writes are guarded by short-lived scoped sessions that immediately close after completing operations.
