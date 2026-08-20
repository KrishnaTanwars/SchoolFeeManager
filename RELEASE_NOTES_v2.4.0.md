# Release Notes — EduLedger College Fee ERP (v2.4.0)

**Release Date:** August 14, 2026  
**Version:** `v2.4.0`  
**License:** Enterprise / License Key Protected  

---

## Executive Summary
Version **v2.4.0** represents the **Final Production Release** of EduLedger College Fee ERP. This landmark release introduces a **Mandatory License Key Activation Guard** integrated directly into the Windows Inno Setup installer, alongside a comprehensive **Responsive Layout & Adaptive Screen Scaling Overhaul** guaranteeing visual excellence across all desktop resolutions from `800×600` to `3840×2160` (4K UHD).

---

## Core Highlights & Innovations

### 1. Mandatory License Key Activation Installer Guard
- **Zero-Trust Pre-Installation Check**: File extraction, directory creation, AppData setup, and shortcut creation are strictly blocked until a valid license key is entered and validated.
- **Custom Inno Setup Wizard Page**: Positioned immediately after destination folder selection with a clear title ("License Activation"), input textbox (unmasked, paste supported), manual "Validate License" button, and color-coded status labels.
- **SHA-256 Hash & Modular Checksum Validation**: Implemented `ValidateLicenseKey` in Pascal Script using secure hash comparison and modular checksum verification. Plain-text license keys are **never** stored inside the installer script.
- **Supported Formats**:
  - `EDU-ABCD-1234-EFGH-5678`
  - `ERP-2026-XXXX-XXXX-XXXX`
- **Validation Messages**:
  - Empty Key: `"License Key cannot be empty."`
  - Invalid Key: `"Invalid License Key. Please contact the software provider."`
  - Valid Key: `"License verified successfully. Preparing installation..."`

### 2. Universal Resolution Scaling & Adaptive UI
- **Full Resolution Compatibility**: Complete responsiveness across `800×600`, `1024×768`, `1280×720`, `1366×768`, `1920×1080` (FHD), `2560×1440` (2K), and `3840×2160` (4K UHD).
- **Zero Ellipsis / Truncation**: Table cells automatically wrap text with dynamic vertical row height expansion (`QHeaderView.ResizeToContents`).
- **Window Geometry Persistence**: Remembers window size, position, and maximized state across application restarts (`QSettings`).
- **Scroll Container Protection**: All primary views and modal dialogs feature responsive `QScrollArea` viewports with protected minimum dimensions.

---

## Release Artifacts
The final release package structure is assembled under `release/v2.4.0/`:

```
release/v2.4.0/
├── Installer/
│   └── CollegeFeeERP_Setup_v2.4.0.exe
├── Portable/
│   └── CollegeFeeERP_Portable_v2.4.0.zip
├── Developer/
│   └── CollegeFeeERP_Source_v2.4.0.zip
├── Checksums/
│   ├── SHA256.txt
│   └── MD5.txt
└── Documentation/
    ├── Version.txt
    ├── License.txt
    ├── README.md
    ├── CHANGELOG.md
    ├── VERSION_HISTORY.md
    ├── RELEASE_NOTES_v2.4.0.md
    ├── INSTALLATION_GUIDE.pdf
    └── USER_MANUAL.pdf
```
