# EduLedger ERP - Technical Debt & Architectural Assessment
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Audit Purpose**: Identify areas requiring cleanup, refactoring, or modernization in future phases.  

---

## 1. Code Duplication & Hardcoded Values

1. **Hardcoded Fallback Paths**:
   - `services/export_service.py` contains hardcoded export directory references (`e:/Downloads/FREELANCING/exports/`) in unit tests.
   - Recommended Fix: Standardize export output paths exclusively using `config.app_config.EXPORTS_DIR`.
2. **Duplicate Validation Logic**:
   - Student mobile number validation (Regex `^[6-9]\d{9}$`) is repeated in both `StudentDialog` and `StudentController`.
   - Recommended Fix: Consolidate input validation into a centralized `utils/validators.py` module.
3. **Hardcoded Default Logo Path**:
   - `PDFService` falls back to `assets/school_logo.png`.
   - Recommended Fix: Dynamically load logo from `SchoolInformation` table record or render institution initials if logo file is missing.

---

## 2. Architectural Debt & Modernization Targets

1. **SQLAlchemy 2.0 Syntax Modernization**:
   - Controllers currently use a mix of legacy `session.query(Model)` and SQLAlchemy 2.0 `session.execute(select(Model))`.
   - Recommended Fix: Standardize 100% of queries to `select()` syntax across all controllers.
2. **`datetime.utcnow()` Deprecation Replacement**:
   - Modernize all UTC timestamp initializations across ORM models (`Student`, `User`, `AuditLog`, `Receipt`) to `datetime.now(timezone.utc)`.
3. **PySide6 Table Model Separation**:
   - Views directly populate `QTableWidget` items cell-by-cell in loop logic.
   - Recommended Fix: Transition complex grids (Student grid, Receipt History grid) to custom `QAbstractTableModel` architectures for faster sorting and filtering performance.

---

## 3. Prioritized Debt Reduction Plan

| Debt Item | Impact | Complexity | Target Phase |
|---|---|---|---|
| Centralize Regex & Form Validators | Lowers duplication | LOW | Phase 1 |
| Update `datetime.utcnow()` to `timezone.utc` | Eliminates deprecation warnings | LOW | Phase 1 |
| Unify Query Syntax to SQLAlchemy 2.0 `select()` | Improves maintainability | MEDIUM | Phase 2 |
| Adopt `QAbstractTableModel` for Large Tables | Improves grid rendering speed | MEDIUM | Phase 3 |
