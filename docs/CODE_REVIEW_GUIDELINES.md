# EduLedger ERP - Code Review Guidelines
**Baseline Version**: 1.0.0  

---

## 1. Code Review Checklist for Engineers & Maintainers

Before approving any code changes for a development phase, reviewers MUST verify the following:

### Architectural Compliance
- [ ] Code strictly follows MVC + Service layer separation.
- [ ] No database operations exist inside `views/` or `dialogs/`.
- [ ] New services are placed in `services/`, helpers in `utils/`.
- [ ] Phase scope is strictly maintained (no feature leakage).

### Database & Data Safety
- [ ] All database sessions are wrapped in `try...except...finally` blocks with `db.close()`.
- [ ] Schema changes include non-destructive dynamic migration updates in `config/database.py`.
- [ ] Foreign keys and relational constraints are preserved (`PRAGMA foreign_keys=ON;`).
- [ ] Operational actions write audit log entries to `audit_logs`.

### Code Quality & Standards
- [ ] Python code follows PEP 8 and project style guide in [CODING_STANDARDS.md](file:///e:/Downloads/ERP/SchoolFeeManager/docs/CODING_STANDARDS.md).
- [ ] Functions include explicit type annotations.
- [ ] No hardcoded passwords, secret keys, or local file system paths.
- [ ] Deprecation warnings are avoided or properly documented.

### Testing & Verification
- [ ] Automated unit test suite passes 100% (`python -m unittest discover tests`).
- [ ] New functionality includes corresponding unit test coverage in `tests/`.
- [ ] Offscreen Qt rendering operates headlessly without GUI display dependencies.

---

## 2. Review Sign-off Procedure

1. Reviewer executes automated unit test runner.
2. Reviewer inspects diffs for phase boundary compliance.
3. Reviewer confirms updated phase documentation (`phases/PHASE_XX/REPORT.md`).
4. Merge approval granted upon 100% pass rate.
