# EduLedger ERP - UI Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**GUI Engine**: PySide6 (Qt 6.11.1)  
**Style Sheet**: [assets/styles/theme.qss](file:///e:/Downloads/ERP/CollegeFeeManager/assets/styles/theme.qss)  

---

## 1. Overview & UI Design Tokens

The user interface follows a modern, professional, high-contrast desktop aesthetic with a dark navy sidebar navigation (#1E293B), clean white data grids (#FFFFFF), primary accent blue buttons (#2563EB), and soft gray background framing (#F1F5F9).

---

## 2. Primary Application Views (9 Screens)

### 1. `LoginView` ([views/login_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/login_view.py))
- **Purpose**: Initial security gateway for authenticating system users.
- **Controls**: Username `QLineEdit`, Password `QLineEdit` (EchoMode: Password), Role indicator combo, Login `QPushButton`.
- **Validation**: Verifies PBKDF2 hashed credentials against `users` table via `AuthController`.
- **Error Handling**: Displays inline error messages for invalid credentials or inactive accounts.

### 2. `MainWindow` ([views/main_window.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/main_window.py))
- **Purpose**: Main application window frame and navigation container.
- **Layout**: 
  - **Header Bar**: Displays School Name, Logged-in User name, User Role badge, Active Academic Session switcher dropdown, and Logout button.
  - **Sidebar**: `QListWidget` navigation menu listing standard modules.
  - **Central Stack**: `QStackedWidget` switching between main views.

### 3. `DashboardView` ([views/dashboard_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/dashboard_view.py))
- **Purpose**: Executive overview dashboard presenting financial KPIs and recent transactions.
- **KPI Cards**:
  1. Today's Fee Collection (Rs.)
  2. Monthly Collection (Rs.)
  3. Total Active Students Count
  4. Receipts Issued Count
- **Analytics Widgets**:
  - Class-wise student distribution pie chart / summary grid.
  - Recent 10 Fee Receipts list.

### 4. `StudentView` ([views/student_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/student_view.py))
- **Purpose**: Comprehensive student master list, search engine, and student management grid.
- **Controls**: Search input field (filters across Admission No, Student Name, Father Name, Mobile), Class filter combo, Section filter combo, "Add Student" button, "Import CSV" button, "Download Sample CSV" button.
- **Data Table**: `QTableWidget` displaying student profiles with Action buttons ("Edit", "Ledger", "Delete").

### 5. `ReceiptView` ([views/receipt_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/receipt_view.py))
- **Purpose**: Interactive fee collection form and receipt generation engine.
- **Controls**:
  - **Student Selector**: Admission No autocomplete search dropdown displaying student details upon selection.
  - **Fee Heads Table**: Dynamic checklist / table allowing selection of fee categories and custom line-item amounts.
  - **Financial Computation Panel**: Subtotal, Discount (-), Fine (+), Grand Total, Paid Amount input, Outstanding Due calculation.
  - **Payment Mode Details**: Mode selector (Cash, UPI, Cheque, DD, Net Banking) dynamically showing UTR No, Cheque No, Cheque Date, and Bank Name fields.
- **Actions**: "Generate & Print Receipt", "Reset Form".

### 6. `ReceiptHistoryView` ([views/receipt_history_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/receipt_history_view.py))
- **Purpose**: Historical ledger of all issued receipts.
- **Controls**: Search bar (Receipt No, Student Name, Admission No), Date range picker (From Date / To Date), Payment Mode filter.
- **Table Columns**: Receipt No, Date, Student Name, Class, Total Amount, Paid Amount, Due Amount, Mode, Status.
- **Actions**: "View/Reprint PDF", "Cancel Receipt" (Admin only).

### 7. `FeeCategoryView` ([views/fee_category_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/fee_category_view.py))
- **Purpose**: Fee head configuration interface for managing dynamic fee structures.
- **Controls**: "Add Fee Category" button, active status toggle switch.
- **Table Columns**: Category Name, Code, Default Amount, Status, Actions ("Edit", "Toggle Active/Inactive").

### 8. `ReportView` ([views/report_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/report_view.py))
- **Purpose**: Financial collection reports and analytical summaries.
- **Report Types**:
  1. Daily Collection Summary
  2. Monthly Collection Breakdown
  3. Custom Date Range Report
  4. Class-wise Collection Summary
- **Actions**: "Export to PDF", "Export to CSV/Excel".

### 9. `SettingsView` ([views/settings_view.py](file:///e:/Downloads/ERP/CollegeFeeManager/views/settings_view.py))
- **Purpose**: Administration, Institution profile setup, session configuration, user manager, and disaster recovery backup center.
- **Tabs**:
  - **School Profile Tab**: School Name, Address, Phone, Email, Website, Logo path uploader, Receipt Prefix.
  - **Academic Session Tab**: Manage and activate session years (e.g. 2024-2025).
  - **User Management Tab**: Create/Manage Admin & Operator user accounts.
  - **Backup & Restore Tab**: "1-Click Database Backup", Backup History table, "Restore Database from ZIP".

---

## 3. Secondary Modal Dialogs (5 Dialogs)

1. **`StudentDialog`** ([dialogs/student_dialog.py](file:///e:/Downloads/ERP/CollegeFeeManager/dialogs/student_dialog.py)): Modal form for adding new student or editing student records. Enforces 10-digit mobile regex and unique admission numbers.
2. **`FeeCategoryDialog`** ([dialogs/fee_category_dialog.py](file:///e:/Downloads/ERP/CollegeFeeManager/dialogs/fee_category_dialog.py)): Modal form for creating/editing fee head parameters.
3. **`ReceiptPreviewDialog`** ([dialogs/receipt_preview_dialog.py](file:///e:/Downloads/ERP/CollegeFeeManager/dialogs/receipt_preview_dialog.py)): Modal window rendering generated PDF receipt image/preview with direct Windows print trigger.
4. **`StudentLedgerDialog`** ([dialogs/student_ledger_dialog.py](file:///e:/Downloads/ERP/CollegeFeeManager/dialogs/student_ledger_dialog.py)): Comprehensive individual student financial history showing lifetime receipts, total paid, and total outstanding due.
5. **`UserDialog`** ([dialogs/user_dialog.py](file:///e:/Downloads/ERP/CollegeFeeManager/dialogs/user_dialog.py)): Modal form for adding or updating user account passwords and roles.
