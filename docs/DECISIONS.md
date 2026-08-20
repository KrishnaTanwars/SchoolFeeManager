# EduLedger ERP - Architectural Decisions & Permanent Project Rules
**Baseline Version**: 1.0.0 Baseline (Semantic Versioning Standard)  
**Governance Scope**: Mandatory Rules for All Development Phases  

---

## 1. Architectural Decision Log (ADR)

### ADR-001: Model-View-Controller (MVC) + Service Layer Pattern
- **Status**: APPROVED
- **Context**: Desktop ERP requires clear separation between GUI event handling, business rules, document creation, and database persistence.
- **Decision**: All application code must adhere to PySide6 Views (`views/`, `dialogs/`), Controllers (`controllers/`), ORM Models (`models/`), Services (`services/`), and Utilities (`utils/`). Direct database queries from UI views are strictly forbidden.

### ADR-002: Offline-First SQLite Storage with Dynamic Schema Migration
- **Status**: APPROVED
- **Context**: Indian school environments often face unreliable internet connectivity; desktop ERP must function 100% offline.
- **Decision**: Store all operational data in local SQLite database (`database/college_fee.db`). Schema changes across releases must be executed via automated pragma table inspection (`run_migrations()`).

### ADR-003: Thread-Safe Scoped DB Sessions with `expire_on_commit=False`
- **Status**: APPROVED
- **Context**: PySide6 UI views access model properties after database transaction commits. Default SQLAlchemy behavior detaches instances, causing runtime `DetachedInstanceError`.
- **Decision**: Set `expire_on_commit=False` on session maker and use eager loading (`joinedload`) across all controllers.

### ADR-004: Zero-External-Dependency ReportLab A4 PDF Engine
- **Status**: APPROVED
- **Context**: Installing external PDF generation packages (like wkhtmltopdf or Chrome headless) increases distribution size and failure points on client Windows PCs.
- **Decision**: Generate commercial PDF fee receipts exclusively via ReportLab Platypus library (`reportlab.platypus`) and print using native Windows shell commands (`os.startfile(pdf_path, 'print')`).

---

## 2. Permanent Project Rules (Mandatory Governance)

> [!IMPORTANT]
> The following rules apply to EVERY development phase. No engineer or automated process may bypass these principles.

1. **One Phase at a Time**: Work MUST proceed strictly one phase at a time. Multi-phase bundling or simultaneous phase execution is prohibited.
2. **No Feature Leakage Across Phases**: Features specified for future phases MUST NOT be introduced early.
3. **Every Phase Must Compile Successfully**: The codebase must build cleanly and launch without syntax errors, missing dependencies, or crash exceptions at the end of every phase.
4. **Every Phase Must Update Documentation**: All baseline docs, API specifications, and phase reports MUST be updated to reflect changes made during that phase.
5. **Every Phase Must Generate a Report**: A formal `REPORT.md` and `CHECKLIST.md` MUST be generated inside the corresponding `phases/PHASE_XX/` directory before concluding a phase.
6. **Every Phase Must Be Tested Before the Next Phase Begins**: All automated unit tests (`python -m unittest discover tests`) MUST pass 100% before initiating the subsequent phase.
7. **Never Modify Unrelated Modules**: Code modifications MUST be strictly scoped to the target phase files.
8. **Always Preserve Backward Compatibility**: Database schema updates, user settings, and stored receipt data MUST maintain 100% backward compatibility.
9. **Always Keep Database Migrations Safe**: Never issue destructive `DROP TABLE` or `DROP COLUMN` commands without non-destructive migration scripts and backup verification.
10. **Always Maintain Audit Logs**: All user actions, fee adjustments, logins, and system configurations MUST write audit trail entries to the `audit_logs` table.
