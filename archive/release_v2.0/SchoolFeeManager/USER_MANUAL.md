# School Fee Management System v1.0 - User Manual

Welcome to the **School Fee Management System**. This user guide explains how to use all features of the application.

---

## 1. Logging In

1. Launch `SchoolFeeManager.exe` or `python main.py`.
2. Enter your credentials on the login screen:
   - **Administrator**: `admin` / `admin123`
   - **Fee Operator**: `operator` / `operator123`
3. Click **LOG IN TO ERP**.

---

## 2. Registering & Managing Students

1. Click **👨‍🎓 Student Master** in the left sidebar.
2. Click **+ Register New Student**.
3. Fill in the student information:
   - Admission Number (must be unique).
   - Roll Number.
   - Student Name, Father's Name, Mother's Name.
   - Class & Section.
   - 10-digit Indian Mobile Number.
   - Address.
4. Click **Save Student**.
5. Use the top search bar to instantly search for any student by name, admission number, father's name, or mobile.

---

## 3. Managing Fee Categories / Heads

1. Click **🏷️ Fee Heads** in the left sidebar.
2. Click **+ Add New Fee Category / Head** to create custom fee categories (e.g., Computer Fee, Transport Fee, Fine).
3. Set the default amount and active status.
4. Existing fee heads can be edited or disabled at any time.

---

## 4. Fee Collection & Receipt Generation

1. Click **💳 Collect Fee** in the left sidebar.
2. In the left panel (**1. Select Student**), type the student's name or admission number in the search box.
3. Select the student from the dropdown menu to load their profile.
4. In the right panel (**2. Fee Particulars**), check the fee heads to collect (e.g., Tuition Fee + Transport Fee).
5. Adjust amounts if necessary.
6. Enter discount (-) or fine (+) if applicable. The **Total Amount** and **Amount in Words** will update automatically in real-time.
7. Select payment mode (Cash, UPI, Cheque, DD, Net Banking) and enter reference/transaction details if any.
8. Click **GENERATE & PRINT RECEIPT**.
9. A receipt preview window will open. You can view the full commercial A4 PDF or print directly to any connected printer.

---

## 5. Receipt History & Searching

1. Click **📜 Receipt History** in the left sidebar.
2. View all generated receipts sorted by date.
3. Filter by date range or search by student name/admission number.
4. Click **View / Print** on any receipt row to view the receipt or reprint a copy.
5. Click **Export CSV** to download the ledger in CSV format.

---

## 6. Financial Reports & Analytics

1. Click **📈 Financial Reports** in the left sidebar.
2. Select your desired report type:
   - Daily Collection Report
   - Monthly Collection Report
   - Custom Date Range Report
   - Class-Wise Collection Summary
3. Click **Generate Report** to calculate metrics.
4. Click **Export Report PDF** to generate an A4 summary PDF report or **Export CSV** to open in Excel.

---

## 7. Database Backup & Restore

1. Click **⚙️ Settings & Backup** in the left sidebar.
2. Go to the **Backup & Restore** tab.
3. **Backup**: Click **Create Immediate Backup ZIP** to save a timestamped backup file of your entire database.
4. **Restore**: Click **Restore Database from ZIP**, select a previously created backup file, and confirm restore. The system automatically creates a pre-restore safety backup before restoring.
