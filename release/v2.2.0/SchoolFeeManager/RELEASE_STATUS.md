# Release Status — EduLedger ERP

## Current Release Summary
- **Current System Version**: `v2.2.0`
- **Release Phase**: Phase X — Professional Overlay Hover Sidebar (Enterprise ERP Navigation Redesign)
- **Target OS Platform**: Windows 10 / Windows 11 (64-bit)
- **Deployment Status**: **PRODUCTION READY**

---

## Active Phase Accomplishments
- **Floating Overlay Sidebar (`Layer 2`)**: Refactored left navigation sidebar into an overlay QFrame childed to `central_widget`.
- **Zero Central Content Shifting**: Main container `right_container` and stacked views (`DashboardView`, `ReceiptView`, `StudentView`, `ReceiptHistoryView`, `ReportView`, `SettingsView`) maintain fixed positions and widths (`x=60`, `width=window_width-60`), eliminating layout reflows, table resizing, and UI flicker.
- **Mouse Hover Tracking & Delays**: Implemented 200ms exit delay (`QTimer`) with mouse coordinate re-validation to prevent accidental collapse on brief cursor movements.
- **Pin Mode Toggle**: Added header pin button (`📌` / `📍`) allowing users to lock the sidebar in permanently expanded mode or return to hover mode.
- **Keyboard Support**: Full `ESC` key support to collapse unpinned sidebar, along with `Ctrl+B` toggle shortcut.
- **Windows 11 Elevation Aesthetics**: Applied `QGraphicsDropShadowEffect` (blur radius 20, offset (4, 0)) and rounded right border styling for modern enterprise UI appearance.
- **Automated Verification & Packaging**: Passed all automated headless unit tests (`100% success`), captured 7 visual verification screenshots, built standalone executable (`SchoolFeeManager.exe`), and generated clean release ZIP archives (`release/v2.2.0/`).

---

## Deliverables & Preservation Status
- **Release Folder Preservation**: All previous release folders (`release/v1.0.0`, `release/v1.0.1`, `release/v1.1.0`, `release/v1.2.0`, `release/v1.3.0`, `release/v1.4.0`, `release/v1.5.0`, `release/v1.6.0`, `release/v1.7.0`, `release/v1.8.0`, `release/v1.9.0`, `release/v2.0.0`, `release/v2.1.0`, `release/v2.2.0`) remain fully preserved.
- **Automated Suite**: Complete headless test suite passing cleanly.
