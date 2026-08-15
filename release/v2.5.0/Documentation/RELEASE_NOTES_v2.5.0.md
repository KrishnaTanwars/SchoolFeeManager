# EduLedger ERP — Version 2.5.0 Release Notes

**Release Version**: v2.5.0  
**Release Date**: August 15, 2026  
**License**: Commercial ERP License  

---

## What's New in Version 2.5.0

### 1. Final College Fee Head Master Configuration
- **14 UG Fee Heads (`UG → B. Pharmacy`)**: Exact college spellings configured (`ADMISSION FORM FEE`, `UG TUTION FEE`, `UG DEVELOPMENT FEE`, `SOCIAL GATHERING FEE`, `SPORT FEE`, `ELIGIBILTY FEE`, `IDENTITY CARD FEE`, `SRTMU EXAM FEE`, `SRTMU GRM/PHOTOCOPY FEE`, `UG LABORATORY DEPOSIT`, `UG CLUB FEES`, `UG LABROTARY CHARGES`, `CAUTION MONEY`, `OTHER FINE`).
- **4 PG Fee Heads (`PG → M. Pharmacy`)**: Exact college spellings configured (`ADMISSION FORM FEE`, `PG TUTION FEE`, `PG DEVELOPMENT FEE`, `PG LABORATORY USAGES`).
- **Shared Fee Head (`ADMISSION FORM FEE`)**: Shared cleanly across UG and PG without duplicate entries.
- **Strict Fee Isolation**: UG fee collection displays strictly the 14 UG fee heads; PG fee collection displays strictly the 4 PG fee heads.

### 2. B. Pharmacy & M. Pharmacy Academic Structure
- **B. Pharmacy (UG)**: 4 Years duration with 8 Semesters (`1st Sem` to `8th Sem`).
- **M. Pharmacy (PG)**: 2 Years duration with 4 Semesters (`1st Sem` to `4th Sem`). Semesters 5+ are automatically blocked for PG courses.

### 3. Student Master Enhancements & Bulk Delete
- **Student Photo Export**: Added `Student Photo` column to CSV, Excel, and PDF student directory exports.
- **Bulk Student Delete with Admin Protection**: Added `🗑️ Delete Selected` button supporting permanent multi-student deletion protected by Administrator Password verification.
- **Action Column Cleanup**: Removed individual row delete icon button from Student Master table to prevent accidental single-row deletion. Retained View, Fee Ledger, and Edit actions.

### 4. Dashboard Clean UI
- Removed `Recent System Activity` widget from the Dashboard.
- Preserved and expanded `Recent Fee Receipt Ledger` displaying the top 25 recent fee receipts with zero text clipping.

---

## Release Verification & Checksums
- Fully verified via unit test suite `tests/test_bhaiya_feedback_v2_5.py` and 130+ integration test cases.
- All release artifacts, checksums (SHA256/MD5), portable packages, and Windows Installers are generated under `release/v2.5.0/`.
