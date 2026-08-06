# Phase 04 Development Notes

## Architectural Decisions
1. **Course Level Classification (`UG` vs `PG`)**: Added `course` String(20) column to `fee_categories` to cleanly separate Undergraduate and Postgraduate fee heads.
2. **Database Schema Backward Compatibility**: Automated SQLite migration in `config/database.py` adds `course` and `created_at` columns gracefully to legacy databases without data loss.
3. **Fee Collection Integration**: `ReceiptView` dynamically inspects the selected student's `course` property and filters active fee heads to display only relevant heads (e.g. `UG` fee heads for UG students, `PG` fee heads for PG students).
4. **Release Preservation**: Preserved all previous release folders (`release/v1.0.0` through `v1.3.0`) and generated clean output under `release/v1.4.0/`.
