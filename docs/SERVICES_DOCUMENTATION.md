# EduLedger ERP - Services Layer Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Service Layer Purpose**: Encapsulate complex non-GUI business operations and external subsystem integrations.  

---

## Service Inventory

### 1. `PDFService` ([services/pdf_service.py](file:///e:/Downloads/ERP/SchoolFeeManager/services/pdf_service.py))
- **Purpose**: Generates high-resolution commercial A4 PDF receipts and financial report documents using ReportLab.
- **Key Methods**:
  - `generate_receipt_pdf(receipt: Receipt, output_path: str = None) -> str`: Builds an A4 PDF fee receipt with school header logo, watermark ("PAID" or "DUAL / PARTIAL"), student details grid, itemized fee breakdown table, payment details block (UTR/Cheque/Bank info), and signatory footer.
  - `generate_collection_report_pdf(report_data: dict, report_title: str, output_path: str = None) -> str`: Generates financial report summary PDFs.
- **Dependencies**: `reportlab.platypus`, `reportlab.lib.pagesizes` (A4), `reportlab.lib.colors`.

### 2. `PrintService` ([services/print_service.py](file:///e:/Downloads/ERP/SchoolFeeManager/services/print_service.py))
- **Purpose**: Facilitates native Windows Direct Printing and document preview without requiring external PDF reader applications.
- **Key Methods**:
  - `print_pdf_direct(pdf_path: str) -> bool`: Invokes Windows native print command (`os.startfile(pdf_path, 'print')`).
  - `preview_pdf(pdf_path: str) -> bool`: Opens default Windows PDF previewer (`QDesktopServices.openUrl()`).
- **Dependencies**: `os`, `PySide6.QtGui.QDesktopServices`, `PySide6.QtCore.QUrl`.

### 3. `BackupService` ([services/backup_service.py](file:///e:/Downloads/ERP/SchoolFeeManager/services/backup_service.py))
- **Purpose**: Disaster recovery backup engine managing automated ZIP compression and database restoration.
- **Key Methods**:
  - `create_backup(backup_type: str = "Manual") -> Tuple[bool, str]`: Creates timestamped ZIP file containing `school_fee.db` in `backup/` directory and logs record into `backup_history`.
  - `restore_backup(backup_zip_path: str) -> Tuple[bool, str]`: Validates ZIP integrity, releases active SQLAlchemy SQLite database connections, extracts `school_fee.db` safely, and runs dynamic database migrations to ensure compatibility.
- **Dependencies**: `zipfile`, `shutil`, `datetime`, `config.database`.

### 4. `ExportService` ([services/export_service.py](file:///e:/Downloads/ERP/SchoolFeeManager/services/export_service.py))
- **Purpose**: Handles CSV and Excel tabular data exports.
- **Key Methods**:
  - `export_table_to_csv(data: List[dict], headers: List[str], output_path: str) -> Tuple[bool, str]`: Formats structured dictionary lists into clean UTF-8 CSV exports.
  - `generate_sample_student_csv(output_path: str) -> Tuple[bool, str]`: Generates standard CSV import template with sample student records for institution administrators.
- **Dependencies**: `csv`, `os`.

### 5. `DBSeedService` ([services/db_seed.py](file:///e:/Downloads/ERP/SchoolFeeManager/services/db_seed.py))
- **Purpose**: Populates system defaults upon clean application initialization.
- **Key Actions**:
  - Creates initial default Admin user (`admin` / `admin123`) and Fee Operator user (`operator` / `operator123`).
  - Creates default Fee Heads (`Admission Fee`, `Tuition Fee`, `Development Fee`, `Sports Fee`, `Computer Fee`, `Library Fee`, `Exam Fee`, `Fine`).
  - Creates default Academic Session (`2024-2025`) and School Information record.
- **Dependencies**: `config.database`, `models.*`, `utils.security`.
