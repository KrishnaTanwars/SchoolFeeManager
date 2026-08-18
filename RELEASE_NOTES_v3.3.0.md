# EduLedger ERP — Release Notes v3.3.0

## Release Summary
Version **v3.3.0** includes essential UI polish, data handling updates, and system architectural enhancements requested in client feedback.

---

## What's New in v3.3.0

### 1. Fees Slip Layout Polish
- **14 Fee Heads Single-Page Fit**: Updated receipt PDF renderer with dynamic cell padding, line heights, and font scaling. Up to 14 fee heads now fit on a single A4 page without spilling onto a second page.
- **Enhanced Legibility**: Increased inter-head spacing for smaller fee head counts (<8 heads) to prevent empty lower half pages.
- **HTML Preview Sync**: Real-time receipt HTML preview matching PDF spacing.

### 2. Student Admission Number Auto-Increment
- Uncoupled Admission Number into a separate input field.
- Implemented automatic sequence generation (`ADM/2026/0001`, `ADM/2026/0002`...).

### 3. Separate Enrollment Number Field
- Added manual entry `Enrollment Number` field.
- Persisted in DB model, updated in student directory, profile views, CSV imports, and receipt PDFs.

### 4. Portable Custom Logo Support
- Dynamic logo resolution via `SettingsController.get_active_logo_path()`.
- Custom logo uploads auto-copied to `assets/` directory for seamless multi-computer installation support.

### 5. Photo Handling & Clickable Excel Hyperlinks
- Student photo remains optional.
- Stored safely in local backup folder (`student_photos/`).
- Excel (`.xlsx`) exports include formatted clickable `file:///` photo hyperlinks opening student photos directly in web browser.

---
*EduLedger ERP v3.3.0 — Compiled & Packaged August 2026*
