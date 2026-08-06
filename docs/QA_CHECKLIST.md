# EduLedger ERP - Quality Assurance (QA) Checklist
**Baseline Version**: 1.0.0  

---

## 1. Automated QA Verification

Run the following command in PowerShell prior to every release tag:

```powershell
python -m unittest discover tests
```

- **Criteria**: 100% of tests MUST pass with zero failures or uncaught exceptions.

---

## 2. Manual QA Verification Matrix

| Area | QA Verification Step | Expected Result | Pass/Fail |
|---|---|---|---|
| **App Launch** | Execute `python main.py` or compiled `.exe`. | Application main window opens smoothly to login screen. | |
| **Authentication** | Login with `admin` / `admin123`. | Authenticates cleanly and loads main dashboard view. | |
| **Role Guarding** | Login with `operator` / `operator123`. | Restricts administrative operations (e.g. system settings / cancellation). | |
| **Student Master** | Add new student record with valid 10-digit mobile number. | Student added to grid; duplicate admission number rejected. | |
| **CSV Import** | Import sample CSV via `StudentView`. | Imports records without throwing encoding or parsing errors. | |
| **Fee Receipt** | Issue receipt with tuition fee item, apply discount & fine, select payment mode. | Computes correct subtotal, total, and outstanding due balance. | |
| **Currency Words** | Inspect generated receipt text. | Amount converted to Indian currency words format (e.g. Lakhs/Crores). | |
| **PDF Generation** | Click "Generate PDF Receipt". | Generates crisp A4 PDF in `exports/` folder with school header & watermark. | |
| **Direct Print** | Trigger direct print command. | Routes print job to default Windows print spooler. | |
| **Backup / Restore**| Trigger 1-Click Backup in `SettingsView`. | ZIP backup created in `backup/`; restore replaces DB safely. | |
