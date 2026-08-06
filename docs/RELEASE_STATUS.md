# EduLedger ERP - Release Status & Executable Audit
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Audit Status**: Verified  

---

## 1. Standalone Executable Audit

- **Executable File**: `release_v2.0/SchoolFeeManager/SchoolFeeManager.exe`
- **File Size**: 9.77 MB (10,239,502 bytes)
- **Target OS**: Windows 10 / Windows 11 (64-bit Architecture)
- **PyInstaller Mode**: Single Folder (`--onedir` mode via `SchoolFeeManager.spec`)
- **Launch Status**: Verified launch without missing DLL errors.

---

## 2. Release Bundles & Packaging Artifacts

| Package File | Path | Status | Purpose |
|---|---|---|---|
| **Client Release Package ZIP** | `SchoolFeeManager_v2.0.zip` | READY | Complete client distribution bundle containing `SchoolFeeManager.exe`, dependencies, initial DB, and user manuals. |
| **Developer Source Package ZIP** | `SchoolFeeManager_Source_v2.0.zip` | READY | Clean developer source code repository archive excluding `build/` and `.venv`. |
| **Inno Setup Script** | `installer.iss` | VERIFIED | Script for compiling `SchoolFeeManager_Setup_v1.0.exe` Windows installer. |

---

## 3. Pre-Release Verification Checklist

- [x] PyInstaller executable generated without console window.
- [x] SQLite database initializer creates default tables dynamically on first run.
- [x] Default credentials (`admin` / `admin123`) functional.
- [x] PDF generation tested in frozen environment.
- [x] Windows direct shell printing verified.
