# EduLedger ERP - Current Limitations & Architectural Boundary Audit
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Status**: Baseline Audit  

---

## 1. Concurrency & Multi-User Limitations

- **Single-Machine Offline Storage**: The current system relies on SQLite (`school_fee.db`). While SQLite supports high read throughput, concurrent network writes across multiple client PCs on a LAN share are constrained by file locking.
- **No Remote Cloud Sync**: The system operates 100% offline. There is currently no automated background synchronization with a central server or cloud database (e.g. PostgreSQL or MySQL).

---

## 2. UI & UX Limitations

- **Static Resolution Optimization**: Designed primarily for desktop screen resolutions of 1280x720 and higher. On lower resolution screens (<1024x768), table grids require horizontal scrolling.
- **Fixed Light/Dark Theme**: The visual styling is locked to a custom light theme with dark navigation defined in `theme.qss`. Dynamic OS theme switching (Light/Dark mode) is not currently implemented.
- **Single Window Interface**: The application operates inside a single main window frame. Opening multiple views simultaneously in separate windows or detached tabs is not supported.

---

## 3. Financial & Accounting Limitations

- **Cash/Bank Ledger Accounting**: Does not implement full double-entry debit/credit bookkeeping (General Ledger). It tracks fee collection income, receipts, discounts, fines, and dues, but does not track institutional expenditures or petty cash balance sheets.
- **Taxation (GST) Calculations**: Does not apply dynamic GST / tax calculations on fee receipts (educational services in India are generally tax-exempt under standard exemptions, but private coaching institutes may require GST configuration in future phases).

---

## 4. Hardware & Printing Limitations

- **Windows Shell Print Dependency**: Direct printing invokes `os.startfile(pdf_path, 'print')`, which relies on the Windows Default Printer configuration. It does not allow selecting target printers dynamically within the app interface prior to printing.
- **A4 Layout Only**: Receipt layouts are designed specifically for A4 standard paper size. Thermal receipt roll formats (3-inch / 80mm POS printers) are not natively supported in the current PDF service template.
