# EduLedger ERP - Build & Distribution Documentation
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Compiler Tools**: PyInstaller 6.21.0 & Inno Setup 6.x  
**Target Output**: Windows 10 / 11 64-Bit Portable Folder & Setup Installer  

---

## 1. PyInstaller Build Architecture

The application build process is orchestrated using `build.py` ([build.py](file:///e:/Downloads/ERP/CollegeFeeManager/build.py)) and the PyInstaller specification file `CollegeFeeManager.spec` ([CollegeFeeManager.spec](file:///e:/Downloads/ERP/CollegeFeeManager/CollegeFeeManager.spec)).

### Key `CollegeFeeManager.spec` Configurations:
1. **Bundled Asset Directories**:
   - `assets/` folder is explicitly bundled into the runtime directory.
2. **Explicit Hidden Imports**:
   - `PySide6.QtCore`, `PySide6.QtGui`, `PySide6.QtWidgets`, `PySide6.QtPrintSupport`
   - `sqlalchemy.ext.baked`, `sqlalchemy.engine.interfaces`, `sqlalchemy.dialects.sqlite`
   - `reportlab.lib.pagesizes`, `reportlab.platypus`, `reportlab.lib.colors`
3. **Excluded Modules**:
   - Excludes heavy unused modules (`tkinter`, `matplotlib`, `PIL._tkinter_finder`) to minimize bundle size.
4. **Execution Mode**:
   - `console=False` (Windowed app mode without command prompt window popping up).

---

## 2. Step-by-Step Compilation Commands

### Step 1: Compile Standalone Executable Directory
Run the build script from the project root:

```powershell
python build.py
```

- **Output Path**: `dist/CollegeFeeManager/`
- **Main Executable**: `dist/CollegeFeeManager/CollegeFeeManager.exe`
- **Executable File Size**: ~9.77 MB

### Step 2: Package Release Archive & Source Packages
Run the release packager script:

```powershell
python package_release.py
```

- **Actions**:
  1. Copies `dist/CollegeFeeManager/` to `release_v2.0/CollegeFeeManager/`.
  2. Ensures required directories exist: `database/`, `backup/`, `exports/`, `logs/`.
  3. Bundles documentation PDFs (`INSTALLATION_GUIDE.pdf`, `USER_MANUAL.pdf`, `Version.txt`, `License.txt`).
  4. Generates ZIP packages: `CollegeFeeManager_v2.0.zip` and `CollegeFeeManager_Source_v2.0.zip`.

### Step 3: Generate Inno Setup Installation Wizard (.EXE)
Compile `installer.iss` using Inno Setup Compiler:

```powershell
iscc installer.iss
```

- **Output File**: `dist_installer/CollegeFeeManager_Setup_v1.0.exe`
- **Installer Features**: Standard installation wizard, program menu shortcuts, desktop shortcut creation option, automated uninstaller.
