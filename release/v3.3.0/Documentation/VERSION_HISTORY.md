# Version History — School Fee Management System

| Version | Release Date | Release Name | Core Features / Enhancements | Status |
| :--- | :--- | :--- | :--- | :--- |
| **v3.2.0** | 2026-08-17 | Production Hotfix — Database Schema Auto-Migration Fix | Added missing `course_category` column auto-migration check in `run_migrations()` (`config/database.py`) to prevent `OperationalError: no such column: students_1.course_category` on existing database upgrades. | **Released** |
| **v2.4.0** | 2026-08-14 | Final Production Release — License Activation Guard | Mandatory Inno Setup License Key Activation Page, SHA-256 hash & modular checksum validation layer, complete responsive screen scaling across all desktop resolutions, full QA suite | **Released** |
| **v2.3.0** | 2026-08-13 | Phase X — Academic Structure Refactor | Semester & Year support for Colleges & Schools, Course/Branch/Semester Fee Heads, AcademicFilterWidget, PDF Receipt metadata, 350 seeded receipts | **Released** |
| **v2.2.0** | 2026-08-13 | Phase X — Enterprise Overlay Sidebar | Floating overlay navigation, zero main layout shifts, 200ms mouse leave delay, pin mode toggle, ESC key shortcut, Windows 11 elevation drop shadow | **Released** |
| **v2.1.1** | 2026-08-12 | Global Search & Sidebar Stability Patch | Global search crash fix, width lower-bound layout invariants, animation group safety | **Released** |
| **v2.1.0** | 2026-08-11 | Demo Data & Table Ergonomics Release | 100 realistic students, 350 fee receipts, fee table column stretch & minimum width polish | **Released** |
| **v2.0.3** | 2026-08-10 | Fee Table Layout & Auto-Collapse | Column width protection for amounts, startup collapsed sidebar state | **Released** |
| **v2.0.2** | 2026-08-09 | Status Bar User Info Relocation | Relocated user login tag to status bar, clean top header bar space | **Released** |
| **v2.0.1** | 2026-08-08 | Login UI Cleanup & Security Polish | Removed pre-login search button, header visibility guards | **Released** |
| **v2.0.0** | 2026-08-07 | Production Ready Release | Complete semantic versioning, client handover suite, user manual PDF | **Released** |
