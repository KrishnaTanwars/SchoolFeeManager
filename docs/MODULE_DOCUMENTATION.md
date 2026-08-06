# EduLedger ERP - Module Inventory Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Total Business Modules**: 11 Core Functional Modules  

---

## Module Inventory Matrix

| Module Name | Purpose & Workflow | Primary Controller / Service | Primary DB Tables | Status |
|---|---|---|---|---|
| **1. Authentication** | Role-based user authentication (Admin & Fee Operator), PBKDF2 password verification, login audit logging, and session state holding. | `AuthController` | `users`, `audit_logs` | COMPLETE |
| **2. Dashboard Analytics** | Real-time financial KPI cards (Today's collection, Monthly total, Active students, Total receipts issued) and analytics summaries. | `ReportController` | `receipts`, `students` | COMPLETE |
| **3. Student Master** | Complete student profile CRUD, 10-digit Indian mobile regex validation, unique admission number enforcement, class/section tracking, and instant search. | `StudentController` | `students` | COMPLETE |
| **4. CSV Student Import** | Batch import students from CSV files with column mapping, error reporting, duplicate skip tracking, and sample CSV template generation. | `StudentController`, `ExportService` | `students` | COMPLETE |
| **5. Fee Heads Master** | Dynamic creation and management of unlimited fee categories (Tuition, Admission, Transport, Lab, Hostel, Exam, Fine, etc.). | `FeeController` | `fee_categories` | COMPLETE |
| **6. Collect Fee Engine** | Issue receipts, calculate Subtotal, Discount (-), Fine (+), Grand Total, Partial Payment (Paid vs. Due), and Indian currency word conversion. | `ReceiptController` | `receipts`, `receipt_items` | COMPLETE |
| **7. Receipt History** | Historical receipt transaction log with search filtering, reprint PDF receipt, view individual student ledgers, and cancel receipts. | `ReceiptController`, `PDFService` | `receipts`, `students` | COMPLETE |
| **8. Financial Reports** | Daily, Monthly, Custom Date Range, and Class-Wise Collection Breakdown reporting with A4 PDF and CSV/Excel exports. | `ReportController`, `ExportService` | `receipts`, `students` | COMPLETE |
| **9. System Settings** | School profile setup (Logo, Header, Address, Receipt Prefix), Academic Session Manager, User management, and Role permissions. | `SettingsController` | `school_information`, `academic_sessions`, `users` | COMPLETE |
| **10. Disaster Recovery** | 1-Click ZIP compressed database backups with history tracking and safety-checked restore engine. | `BackupService` | `backup_history` | COMPLETE |
| **11. A4 PDF & Printing** | ReportLab A4 PDF receipt generation featuring watermark, logo header, signatory block, and native Windows print routing. | `PDFService`, `PrintService` | `receipts`, `school_information` | COMPLETE |

---

## Detailed Breakdown of Key Workflows

### Module 6: Fee Collection & Receipt Engine
- **Input Parameters**: `student_id`, `academic_session`, itemized fee list (`category_name`, `amount`), `discount_amount`, `fine_amount`, `paid_amount`, `payment_mode`, `utr_number`, `cheque_number`, `cheque_date`, `bank_name`.
- **Validation Rules**:
  1. Student MUST exist and be active.
  2. At least 1 fee head item MUST be selected.
  3. `paid_amount` must be greater than zero and less than or equal to `total_amount`.
  4. If payment mode is `Cheque`, cheque number and bank name are validated.
  5. If payment mode is `UPI / QR`, UTR reference number is recorded.
- **Outputs**: Generated `Receipt` record with unique sequential `receipt_no` (e.g. `REC/2024/00001`), generated A4 PDF file in `exports/` folder, and printed receipt trigger.
