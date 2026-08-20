# EduLedger ERP v2.0.0 (College Fee Management System)

A production-ready, offline-first Desktop ERP application designed specifically for Indian Schools, Colleges, Private Institutes, and Coaching Centers.

---

## Key Features

- **Student Master Management**:
  - Admission, Roll number, Class, Section, Father Name, Mother Name, 10-digit Indian Mobile validation.
  - Admission Number unique duplicate check.
  - Fast search across student name, admission number, father's name, or mobile number.
- **Unlimited Fee Categories / Heads**:
  - Admission Fee, Tuition Fee, Development Fee, Sports Fee, Library Fee, Lab Fee, Computer Fee, Transport Fee, Hostel Fee, Exam Fee, Fine, Miscellaneous.
  - Manage and create custom fee categories dynamically.
- **Fee Collection & Receipt Engine**:
  - Auto-generated receipt numbers with custom school prefix (e.g. `REC/2024/00001`).
  - Itemized fee breakdown.
  - Real-time Subtotal, Discount (-), Fine (+), and Grand Total calculation.
  - **Indian Currency Number-to-Words Converter** (Lakhs & Crores, e.g. *"One Lakh Fifty Thousand Rupees Only"*).
  - Multiple payment modes (Cash, UPI, Cheque, Demand Draft, Net Banking).
- **Commercial A4 PDF & Printing Engine**:
  - ReportLab-generated high-resolution A4 Fee Receipts with College Logo, Header, Student Details Grid, Fee Table, Signatures, and Footer.
  - Native Windows Direct Printing & Print Preview (`QtPrintSupport`).
- **Financial Reports & Analytics**:
  - Executive Dashboard with KPI cards (Today's Collection, Monthly Collection, Active Students, Receipts Issued).
  - Daily, Monthly, Custom Date Range, and Class-Wise Collection Breakdown Reports.
  - Export reports to A4 PDF and CSV/Excel formats.
- **System Administration & Disaster Recovery**:
  - Admin & Operator roles with PBKDF2 SHA-256 password hashing.
  - 1-Click ZIP Database Backup & Safety-Checked Restore Engine.
  - Full audit logging of all system actions.

---

## Default Login Credentials

| Role | Username | Password |
|---|---|---|
| **System Administrator** | `admin` | `admin123` |
| **Fee Operator** | `operator` | `operator123` |

---

## Running from Source

1. **Prerequisites**: Python 3.10+ on Windows 10/11.
2. **Install Dependencies**:
   ```powershell
   pip install PySide6 SQLAlchemy reportlab pyinstaller pytest
   ```
3. **Launch Application**:
   ```powershell
   python main.py
   ```
4. **Run Unit Test Suite**:
   ```powershell
   python -m unittest discover -s tests
   ```

---

## Building Executable (.EXE)

To compile the standalone Windows Desktop application:
```powershell
python build.py
```
The compiled output will be generated at: `dist/CollegeFeeManager/CollegeFeeManager.exe`.

---

## Technology Stack

- **GUI Framework**: PySide6 (Qt6 for Python)
- **Database Backend**: SQLite (`college_fee.db`)
- **ORM & Data Layer**: SQLAlchemy ORM with foreign key enforcement
- **PDF Generation**: ReportLab
- **Packaging**: PyInstaller
