# EduLedger ERP - Client Customizations Inventory
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Purpose**: Document all client-requested customizations implemented prior to Phase 0.  

---

## Implemented Client Customizations Log

### Customization 1: Indian Currency Number-to-Words (Lakhs & Crores Format)
- **Original Behavior**: Fee receipts showed total numbers only (e.g. `Rs. 150000.00`).
- **New Behavior**: Automatically converts grand totals to Indian numerical words system (e.g., *"One Lakh Fifty Thousand Rupees Only"*).
- **Reason**: Client institutions required legal Indian currency wording compliance on printed A4 receipts.
- **Files Modified**: `utils/number_to_words.py`, `controllers/receipt_controller.py`, `services/pdf_service.py`.
- **Version Introduced**: v1.0.0

---

### Customization 2: Partial Fee Payment & Outstanding Due Tracking
- **Original Behavior**: Receipts required 100% full payment of total fee amounts upon issuance.
- **New Behavior**: Allows partial payment entry (`paid_amount`), calculates remaining balance (`due_amount`), and records cumulative outstanding student due balance.
- **Reason**: School clients needed ability to accept partial installments during mid-term admissions.
- **Files Modified**: `models/receipt.py`, `controllers/receipt_controller.py`, `views/receipt_view.py`, `services/pdf_service.py`.
- **Version Introduced**: v1.1.0

---

### Customization 3: Mode-Specific Payment Details Persistence (UPI, Cheque, Bank)
- **Original Behavior**: Only stored static string "Cash" or "Cheque".
- **New Behavior**: Dynamic UI inputs and DB columns for UTR Number (UPI/QR), Cheque Number, Cheque Date, and Bank Name.
- **Reason**: School accountants required exact audit details for bank reconciliation.
- **Files Modified**: `models/receipt.py`, `views/receipt_view.py`, `controllers/receipt_controller.py`, `services/pdf_service.py`.
- **Version Introduced**: v1.1.0

---

### Customization 4: CSV Student Bulk Import & Sample Template Download
- **Original Behavior**: Manual entry of students one-by-one in UI form.
- **New Behavior**: 1-Click download of sample CSV template and bulk student CSV import engine.
- **Reason**: Client schools onboarding hundreds of existing students at session start.
- **Files Modified**: `services/export_service.py`, `controllers/student_controller.py`, `views/student_view.py`.
- **Version Introduced**: v1.1.0

---

### Customization 5: Dual Status PDF Receipt Watermarking
- **Original Behavior**: Standard PDF receipt without status watermark.
- **New Behavior**: Renders soft green "PAID" watermark for fully settled receipts and amber "DUAL / PARTIAL" watermark for partial payments.
- **Reason**: Immediate visual verification for gatekeepers and accountants.
- **Files Modified**: `services/pdf_service.py`.
- **Version Introduced**: v1.0.0

---

### Customization 6: Administrator Password Authorization & Delete/Settings Protection
- **Original Behavior**: Delete operations (students, fee heads, receipts) and settings navigation executed without password challenge.
- **New Behavior**: Prompts reusable modal `AdminAuthDialog` requiring administrator password authorization for all delete operations and settings navigation.
- **Reason**: Client institution management requested strict authorization controls to prevent unauthorized record deletion or setting changes.
- **Files Modified**: `dialogs/admin_auth_dialog.py`, `services/security_service.py`, `models/audit.py`, `config/database.py`, `views/student_view.py`, `views/fee_category_view.py`, `views/receipt_history_view.py`, `views/main_window.py`.
- **Version Introduced**: v1.1.0 (Phase 1)
