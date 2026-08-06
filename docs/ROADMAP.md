# EduLedger ERP - Long-Term Development Roadmap (Phases 1 - 10)
**Baseline Version**: v1.0.0 Baseline (Semantic Versioning Standard)  
**Strategy**: Systematic, phase-by-phase evolution. Each phase maps to a minor semantic version update (`v1.1.0` through `v2.0.0`).  

---

## Semantic Versioning Roadmap Matrix

| Phase # | Semantic Version | Target Phase Title | Objective Overview |
|---|---|---|---|
| **Phase 0** | `v1.0.0` | Baseline Freeze & Technical Audit | Freeze current baseline, complete technical audit, and standardize project structure. |
| **Phase 1** | `v1.1.0` | Code Modernization & Validation Centralization | Modernize type hints, replace `datetime.utcnow()`, centralize form regex validation, unify SQLAlchemy 2.0 select query syntax. |
| **Phase 2** | `v1.2.0` | Advanced Student Management & Academic Progression | Student photo uploads, class promotion/demotion workflows, sibling linking, profile export. |
| **Phase 3** | `v1.3.0` | Comprehensive Fee Structure & Discount Rule Engine | Recurring fee schedules (Monthly/Quarterly), fee structure templates, sibling discounts, late fee penalties, waiver approvals. |
| **Phase 4** | `v1.4.0` | Multi-Payment Gateway Integration & Digital Invoicing | Dynamic UPI QR code generation, SMS/WhatsApp receipt delivery integration, payment gateway webhooks. |
| **Phase 5** | `v1.5.0` | Advanced Financial Reporting & Executive Dashboards | Interactive financial charts, class-wise revenue comparisons, collection forecasting, due age analysis. |
| **Phase 6** | `v1.6.0` | Role-Based Access Control (RBAC) & Fine-Grained Permissions | Granular permission matrix, custom roles (Accountant, Principal, Auditor), feature toggles. |
| **Phase 7** | `v1.7.0` | Multi-Branch & Multi-Institution Support | Multi-tenant branch management, campus-level data isolation, consolidated corporate reporting. |
| **Phase 8** | `v1.8.0` | Staff, Payroll & Expense Management | Staff master profiles, teacher attendance, monthly salary generation, payslip PDF generation, petty cash expense tracking. |
| **Phase 9** | `v1.9.0` | Cloud Synchronization & Hybrid Offline-Online Mode | Background REST API / Cloud database sync service for offline-first operations. |
| **Phase 10**| `v2.0.0` | Mobile Companion App & Parent Portal (Production Release) | Parent mobile app (Flutter/React Native) and web portal for online fee payment, receipts, and notifications. |

---

## Detailed Phase Objectives

### Phase 1 — Code Modernization & Validation Centralization (`v1.1.0`)
Modernize Python type hints, resolve `datetime.utcnow()` deprecation warnings by replacing them with timezone-aware `datetime.now(timezone.utc)`, centralize form validation rules (mobile regex, duplicate admission checks) into `utils/validators.py`, and unify SQLAlchemy 2.0 query syntax across all controllers without introducing new features.

### Phase 2 — Advanced Student Management & Academic Progression (`v1.2.0`)
Enhance student lifecycle management by introducing student profile picture uploads, class promotion/demotion workflows, student sibling linking, custom profile fields, and detailed academic profile export features.

### Phase 3 — Comprehensive Fee Structure & Discount Rule Engine (`v1.3.0`)
Expand fee management capabilities with recurring fee scheduling (Monthly, Quarterly, Annual), class-wise fee structure templates, sibling discount rules, late fee penalty calculation rules, and fee waiver approval workflows.

### Phase 4 — Multi-Payment Gateway Integration & Digital Invoicing (`v1.4.0`)
Introduce digital payment workflows, including dynamic QR code generation (UPI Intent URLs) directly on receipt screens, SMS/WhatsApp receipt delivery integration, and optional payment gateway webhook reconciliation.

### Phase 5 — Advanced Financial Reporting & Executive Dashboards (`v1.5.0`)
Deliver deep financial business intelligence with interactive charts, class-wise revenue comparisons, fee collection forecasting, outstanding due age analysis reports, and automated daily email financial summaries for management.

### Phase 6 — Role-Based Access Control (RBAC) & Fine-Grained Permissions (`v1.6.0`)
Replace simple Admin/Operator role flags with a granular permission matrix, enabling custom role creation (Accountant, Principal, Receptionist, Auditor) with explicit read/write/delete permissions per module.

### Phase 7 — Multi-Branch & Multi-Institution Support (`v1.7.0`)
Enable multi-tenant architecture support, allowing educational groups to manage multiple branches, campuses, or institutes within a single ERP installation with branch-level data isolation and consolidated corporate reporting.

### Phase 8 — Staff, Payroll & Expense Management (`v1.8.0`)
Expand EduLedger from a Fee Manager into a complete institutional ERP by introducing Staff Master profiles, teacher attendance tracking, monthly salary generation, payslip PDF generation, and petty cash expense tracking.

### Phase 9 — Cloud Synchronization & Hybrid Offline-Online Mode (`v1.9.0`)
Implement an optional background synchronization service (using PostgreSQL / REST API) that syncs offline desktop data to a central cloud server when internet connectivity is available, supporting hybrid offline-first operations.

### Phase 10 — Mobile Companion App & Parent Self-Service Portal (`v2.0.0` Production Release)
Build a complementary mobile application and web portal for parents to view student fee receipts, pay outstanding dues online, download statement ledgers, and receive real-time institution notifications.
