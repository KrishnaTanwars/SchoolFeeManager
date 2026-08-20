# EduLedger ERP — Client Handover & Administrator Guide
**Software Version**: v2.0.0 (Production Release)  
**Target Audience**: School Administrators, Office Staff & IT Operations  

---

## 1. Quick Start Installation

1. Extract the client release ZIP `CollegeFeeManager_v2.0.0.zip` to your preferred folder (e.g., `C:\EduLedgerERP\`).
2. Double-click **`CollegeFeeManager.exe`** to launch the ERP.
3. On fresh installation, log in with default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. Go to **Settings → User Management** to change the default admin password immediately.

---

## 2. Core Operational Workflows

### 💳 Collecting Fees & Generating Receipts
1. Navigate to **Fee Collection** from the left sidebar or press `Ctrl+1`.
2. Type student name or admission number in the autocomplete search box.
3. Select active fee heads, enter payment mode (Cash/UPI/Cheque/Card/Net Banking), and enter paid amount.
4. Click **`💳 Generate Fee Receipt (Ctrl+S)`** to save transaction and open print/PDF preview.

### 📥 Bulk Student Import
1. Navigate to **Student Directory → 📤 Import CSV**.
2. Click **`📥 Sample CSV Template`** or **`📊 Sample Excel Template`** to download pre-formatted files.
3. Fill student records in Excel/CSV, select the file in the wizard, click **`Validate & Preview`**, review status, and click **`🚀 Import Valid Students`**.

### 📦 Backup & Disaster Recovery
1. Go to **Settings → Backup & Restore**.
2. Click **`📦 Create Immediate Backup ZIP`** to create a complete timestamped backup archive.
3. Configure **Auto-Backup Schedule** (Daily/Weekly/Monthly) and retention rules (5/10/20/Unlimited).

### 📈 MIS Financial Reports
1. Navigate to **Financial Reports** from the left sidebar or press `Ctrl+5`.
2. Select any report card (`Daily Collection`, `Monthly Collection`, `Class-wise`, `Outstanding Dues`, `Student Ledger`, etc.).
3. Set filter parameters and click **`Generate Report`**. Export to PDF, CSV, Excel, or print directly.

---

## 3. Maintenance & Support

- **Database Optimization**: Go to **Settings → Database Management → ⚡ Optimize Database (VACUUM)** once a month to compact database storage.
- **Audit Logs**: All sensitive operations (deletions, settings changes, logins) are recorded under **Settings → Audit Log Viewer**.
