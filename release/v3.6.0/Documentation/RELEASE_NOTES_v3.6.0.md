# EduLedger ERP — Release Notes v3.6.0

## Release Summary
Version **v3.6.0** resolves the issue where deleted default courses and branches were immediately resurrected by background master table re-seeding. It also introduces student dependency safeguards on course/branch deletion, row-level `🗑 Delete` buttons across Course and Branch Master tables, and a direct `🗑 Delete Program` button in the Course Details view.

---

## Key Fixes & Improvements in v3.6.0

### 1. Permanent Course & Branch Deletion Fix
- **Prevent Resurrection of Deleted Master Records**: Fixed `AcademicController.seed_academic_masters_if_empty()` so that default courses (`B. Pharmacy`, `B.Tech`, `MBA`, `BCA`, etc.) and branches are only seeded when master tables are completely empty on fresh database creation.
- **Persistent Deletion**: Once a course or branch is deleted by an admin, it remains permanently deleted and will no longer re-appear on page refresh.

### 2. Student Assignment Protection Safeguards
- **Enrolled Student Validation**: `AcademicController.delete_course()` and `delete_branch()` now verify if any active students are currently enrolled under the target course or branch.
- **Informative Error Messages**: If students are currently enrolled, deletion is safely blocked with a clear message: `"Cannot delete course 'X': N student(s) are currently enrolled in this course. Please reassign or delete those students first."`

### 3. Row-Level & Details Dialog Delete Actions
- **Direct Row Delete**: Added explicit `🗑 Delete` action buttons to each row in the **Course Programs Master** and **Specialization Branches** tables.
- **Details View Delete**: Added a `🗑 Delete Program` button directly inside the 1-click **Course Program Master Details** viewer dialog.

---
*EduLedger ERP v3.6.0 — Compiled & Packaged August 2026*
