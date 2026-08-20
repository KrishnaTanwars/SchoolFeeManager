# Release Notes — EduLedger ERP v2.3.0

We are proud to release **EduLedger ERP Version v2.3.0 (Enterprise Client Delivery Phase)**. This landmark release transitions the software from a standalone folder executable into a **fully integrated, professional Windows desktop application** with a native setup installer, AppData hybrid storage architecture, version metadata, and a master automated build pipeline.

---

## 🚀 What's New in Version 2.3.0

### 💾 1. AppData Hybrid Data Architecture
- **Zero Administrative Restrictions**: Dynamic application data (database, logs, backups, exports, settings, reports, cache, temp) now defaults to `%APPDATA%\EduLedger\CollegeFeeERP` on Windows.
- **Program Files Support**: The software can now be safely installed into `C:\Program Files\EduLedger\CollegeFeeERP` without write permission crashes or UAC elevation failures.
- **First-Run Automatic Seeding**: On first startup, initial database tables, default admin/operator credentials, and UG/PG fee heads are automatically initialized.

### 📦 2. Commercial Windows Setup Installer (`CollegeFeeERP_Setup.exe`)
- **Native Setup Wizard**: Modern Inno Setup 6 installer wizard supporting 32-bit and 64-bit Windows 10 and 11.
- **Shortcuts & Branding**: Automatic creation of Desktop and Start Menu shortcuts using high-resolution application icons (`app_icon.ico`).
- **Control Panel Integration**: Registered in Windows Add/Remove Programs with full version, publisher ("EduLedger"), and uninstaller metadata.
- **Smart Uninstaller**: Includes an interactive prompt during uninstallation asking whether to keep or remove user database & logs in AppData.

### 🧰 3. Master Release & Build Pipeline (`build_release.py`)
- **One-Command Automation**: Running `python build_release.py` automates the full workflow:
  1. Synchronizes version numbers across all files (`Version.txt`, spec, Inno Setup, metadata).
  2. Compiles PyInstaller binary executable with Windows File Properties (`file_version_info.txt`).
  3. Validates executable integrity and assets.
  4. Compiles Inno Setup installer (`CollegeFeeERP_Setup.exe`).
  5. Packages Standalone Portable ZIP (`CollegeFeeERP_Portable.zip`) with `.portable` flag.
  6. Packages Developer Source ZIP (`CollegeFeeERP_Source.zip`).
  7. Generates commercial PDF documentation (`INSTALLATION_GUIDE.pdf`, `USER_MANUAL.pdf`).
  8. Computes SHA256 & MD5 checksum files.
  9. Structures the final release folder under `release/v2.3.0/` while preserving all previous release directories.

### 💼 4. Executable Metadata & Properties
- **Windows File Properties**: `CollegeFeeManager.exe` now displays official Windows File Properties:
  - Product Name: **College Fee ERP**
  - Company: **EduLedger**
  - File Description: **Enterprise College Fee Management System**
  - Copyright: **Copyright © 2026 EduLedger. All Rights Reserved.**

---

## 📦 Deliverables Structure in `release/v2.3.0/`

```
release/v2.3.0/
├── Installer/
│   └── CollegeFeeERP_Setup_v2.3.0.exe
├── Portable/
│   └── CollegeFeeERP_Portable_v2.3.0.zip
├── Developer/
│   └── CollegeFeeERP_Source_v2.3.0.zip
├── Checksums/
│   ├── SHA256.txt
│   └── MD5.txt
└── Documentation/
    ├── INSTALLATION_GUIDE.pdf
    ├── USER_MANUAL.pdf
    ├── RELEASE_NOTES_v2.3.0.md
    ├── CHANGELOG.md
    └── License.txt
```

---

## 🧪 Verification & Acceptance

- **Automated Build Validation**: Passed 100% build integrity verification.
- **AppData Multi-User Testing**: Verified clean startup on standard non-admin Windows user accounts.
- **Release Status**: **APPROVED FOR PRODUCTION CLIENT DEPLOYMENT** ✅
