# Phase 01 Engineering Notes — Security & Administration Hardening
**Version Tag**: `v1.1.0`  

---

## Technical Design Notes

1. **Reusability of `AdminAuthDialog`**:
   The `AdminAuthDialog` class was engineered as a standalone, modal `QDialog` that can be instantiated by any view module with custom `action_title` and `action_context` strings.
2. **Decoupled Password Verification**:
   UI views never directly query `User` password hashes. All password verification is delegated to `SecurityService.verify_admin_password(password)`, which iterates active Admin accounts in DB using PBKDF2 HMAC SHA-256 comparison.
3. **Safe Schema Migration**:
   Dynamic SQLite migration checks existing `audit_logs` table columns via `PRAGMA table_info()` and executes `ALTER TABLE` for missing `module`, `status`, and `machine_name` columns without disrupting stored audit history.
4. **Audit Logging Hygiene**:
   `SecurityService.log_audit()` captures active logged-in user ID via `AuthController.get_current_user()` and current workstation hostname via `socket.gethostname()`. Exceptions are caught internally so logging never interrupts application workflow.
