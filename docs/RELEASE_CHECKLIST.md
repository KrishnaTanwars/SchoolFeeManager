# EduLedger ERP - Release Verification Checklist
**Baseline Version**: 1.0.0 (Semantic Versioning Standard)  

---

## Pre-Release Verification Steps

- [ ] **Phase Completion Verification**: All phase requirements completed and verified against phase checklist (`phases/PHASE_XX/CHECKLIST.md`).
- [ ] **Automated Unit Tests**: Execute `python -m unittest discover tests` — 100% tests MUST pass.
- [ ] **Semantic Version Alignment**: Verify version numbers in `Version.txt`, `config/app_config.py`, `installer.iss`, and documentation match target version string (e.g. `v1.1.0`).
- [ ] **PyInstaller Build Execution**: Execute PyInstaller build script:
  ```powershell
  python build.py
  ```
  Verify executable output exists at `dist/CollegeFeeManager/CollegeFeeManager.exe`.
- [ ] **Release Packaging Execution**: Execute release packaging script:
  ```powershell
  python package_release.py
  ```
  Verify output archives created (`CollegeFeeManager_vX.X.zip` and `CollegeFeeManager_Source_vX.X.zip`).
- [ ] **Release Folder Storage**: Copy release ZIP and PDF manuals into corresponding release folder:
  `release/vX.X.X/`
- [ ] **Documentation Update**: Update `CHANGELOG.md`, `VERSION_HISTORY.md`, and `RELEASE_STATUS.md`.
- [ ] **Git Tagging**: Create official git release tag:
  ```bash
  git tag -a vX.X.X -m "Release vX.X.X"
  ```
