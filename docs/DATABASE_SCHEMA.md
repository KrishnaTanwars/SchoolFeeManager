# EduLedger ERP - Database Schema Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Database Backend**: SQLite 3 (`college_fee.db`)  
**ORM Framework**: SQLAlchemy 2.0.51  
**Total Tables**: 8 Tables  

---

## 1. Relational Entity Overview

```
 +---------------+         +-----------------+         +---------------------+
 |   students    | 1     * |    receipts     | *     1 |        users        |
 |---------------+---------|<----------------|-------->|---------------------|
 | id (PK)       |         | id (PK)         |         | id (PK)             |
 | admission_no  |         | student_id (FK) |         | username            |
 | name          |         | created_by (FK) |         | password_hash       |
 +---------------+         +--------+--------+         +----------+----------+
                                    | 1                           | 1
                                    |                             |
                                    | *                           | *
                           +--------v--------+         +----------v----------+
                           |  receipt_items  |         |     audit_logs      |
                           |-----------------|         |---------------------|
                           | id (PK)         |         | id (PK)             |
                           | receipt_id (FK) |         | user_id (FK)        |
                           | fee_cat_id (FK) |         | action, timestamp   |
                           +-----------------+         +---------------------+

 +--------------------+   +---------------------+   +---------------------+
 |   fee_categories   |   | school_information  |   |  academic_sessions  |
 |--------------------|   |---------------------|   |---------------------|
 | id (PK)            |   | id (PK)             |   | id (PK)             |
 | name, code         |   | school_name         |   | session_name        |
 | default_amount     |   | receipt_prefix      |   | is_current          |
 +--------------------+   +---------------------+   +---------------------+

                          +---------------------+
                          |   backup_history    |
                          |---------------------|
                          | id (PK), filename   |
                          | status, created_at  |
                          +---------------------+
```

---

## 2. Table Specifications

### 1. `users`
Stores system accounts for administrative and fee operator access.
- `id` (INTEGER, PK, AutoIncrement)
- `username` (VARCHAR(50), Unique, Not Null, Indexed)
- `password_hash` (VARCHAR(255), Not Null) - Stores PBKDF2 SHA-256 hash
- `full_name` (VARCHAR(100), Not Null)
- `role` (VARCHAR(30), Default 'Operator', Not Null) - Roles: `Admin`, `Operator`
- `status` (VARCHAR(20), Default 'Active', Not Null) - Status: `Active`, `Inactive`
- `last_login` (DATETIME, Nullable)
- `created_at` (DATETIME, Default UTC Now, Not Null)

### 2. `students`
Master profile registry for all admitted students.
- `id` (INTEGER, PK, AutoIncrement)
- `admission_no` (VARCHAR(50), Unique, Not Null, Indexed)
- `roll_no` (VARCHAR(20), Nullable)
- `name` (VARCHAR(100), Not Null, Indexed)
- `father_name` (VARCHAR(100), Not Null)
- `mother_name` (VARCHAR(100), Nullable)
- `class_name` (VARCHAR(50), Not Null, Indexed)
- `section` (VARCHAR(20), Nullable)
- `course` (VARCHAR(100), Nullable, Indexed)
- `mobile` (VARCHAR(15), Not Null, Indexed)
- `address` (TEXT, Nullable)
- `admission_date` (DATE, Default Today, Not Null)
- `academic_session` (VARCHAR(20), Not Null, Indexed)
- `status` (VARCHAR(20), Default 'Active', Not Null)
- `created_at` (DATETIME, Default UTC Now, Not Null)

### 3. `fee_categories`
Dynamic fee heads configured by system administrators.
- `id` (INTEGER, PK, AutoIncrement)
- `name` (VARCHAR(100), Unique, Not Null, Indexed) e.g., Tuition Fee, Admission Fee
- `code` (VARCHAR(20), Nullable)
- `default_amount` (FLOAT, Default 0.0, Not Null)
- `is_active` (BOOLEAN, Default True, Not Null)
- `description` (VARCHAR(255), Nullable)

### 4. `receipts`
Financial transactions and generated fee receipts.
- `id` (INTEGER, PK, AutoIncrement)
- `receipt_no` (VARCHAR(50), Unique, Not Null, Indexed) e.g., `REC/2024/00001`
- `receipt_date` (DATE, Default Today, Not Null, Indexed)
- `student_id` (INTEGER, FK -> `students.id`, Not Null, Indexed)
- `academic_session` (VARCHAR(20), Not Null, Indexed)
- `subtotal` (FLOAT, Default 0.0, Not Null)
- `discount_amount` (FLOAT, Default 0.0, Not Null)
- `fine_amount` (FLOAT, Default 0.0, Not Null)
- `total_amount` (FLOAT, Default 0.0, Not Null)
- `paid_amount` (FLOAT, Default 0.0, Not Null)
- `due_amount` (FLOAT, Default 0.0, Not Null)
- `amount_in_words` (TEXT, Not Null)
- `payment_mode` (VARCHAR(30), Default 'Cash', Not Null) e.g., Cash, UPI, Cheque, DD, Bank Transfer
- `reference_no` (VARCHAR(100), Nullable)
- `utr_number` (VARCHAR(100), Nullable)
- `cheque_number` (VARCHAR(50), Nullable)
- `cheque_date` (DATE, Nullable)
- `bank_name` (VARCHAR(100), Nullable)
- `payment_date` (DATE, Nullable)
- `remarks` (VARCHAR(255), Nullable)
- `created_by_user_id` (INTEGER, FK -> `users.id`, Nullable)
- `status` (VARCHAR(20), Default 'Paid', Not Null) - Status: `Paid`, `Cancelled`
- `created_at` (DATETIME, Default UTC Now, Not Null)

### 5. `receipt_items`
Itemized break down of fee heads associated with each receipt.
- `id` (INTEGER, PK, AutoIncrement)
- `receipt_id` (INTEGER, FK -> `receipts.id` [ON DELETE CASCADE], Not Null, Indexed)
- `fee_category_id` (INTEGER, FK -> `fee_categories.id`, Nullable)
- `category_name` (VARCHAR(100), Not Null)
- `amount` (FLOAT, Not Null)

### 6. `school_information`
Institution profile details printed on PDF receipt headers.
- `id` (INTEGER, PK, AutoIncrement)
- `school_name` (VARCHAR(150), Default 'EduLedger College', Not Null)
- `address` (TEXT, Default '123 Knowledge Park, New Delhi, India', Not Null)
- `phone` (VARCHAR(50), Default '+91 98765 43210', Not Null)
- `email` (VARCHAR(100), Default 'info@eduledgercollege.edu.in', Not Null)
- `website` (VARCHAR(100), Default 'www.eduledgercollege.edu.in', Nullable)
- `logo_path` (VARCHAR(255), Nullable)
- `receipt_prefix` (VARCHAR(20), Default 'REC/', Not Null)

### 7. `academic_sessions`
Active and historic school session years.
- `id` (INTEGER, PK, AutoIncrement)
- `session_name` (VARCHAR(30), Unique, Not Null, Indexed) e.g., `2024-2025`
- `is_current` (BOOLEAN, Default False, Not Null)
- `start_date` (DATE, Nullable)
- `end_date` (DATE, Nullable)

### 8. `audit_logs`
System operational audit trails for security tracking.
- `id` (INTEGER, PK, AutoIncrement)
- `user_id` (INTEGER, FK -> `users.id`, Nullable)
- `action` (VARCHAR(100), Not Null)
- `details` (TEXT, Nullable)
- `timestamp` (DATETIME, Default UTC Now, Not Null, Indexed)

### 9. `backup_history`
Log of ZIP backup operations.
- `id` (INTEGER, PK, AutoIncrement)
- `filename` (VARCHAR(255), Not Null)
- `file_size` (VARCHAR(50), Not Null)
- `backup_type` (VARCHAR(30), Default 'Manual', Not Null)
- `status` (VARCHAR(30), Default 'Success', Not Null)
- `created_at` (DATETIME, Default UTC Now, Not Null)

---

## 3. Schema Migration Mechanism

Schema updates are managed dynamically in `config/database.py` via `run_migrations()`. On application launch, SQLite inspects table columns via `PRAGMA table_info()` and issues `ALTER TABLE` statements for any missing columns, ensuring backward compatibility across releases without raw SQL script intervention.
