# EduLedger ERP - Folder Structure Rules & Organization Standards
**Baseline Version**: 1.0.0  

---

## 1. Directory Placement Rules

| Directory Path | Allowed Content Types | Strict Restrictions |
|---|---|---|
| `assets/` | Static images, icons, logo files, and QSS style sheets. | No Python source code or runtime generated files. |
| `config/` | Core configuration settings, DB URLs, storage paths, engine setup. | No UI widget code or controller logic. |
| `controllers/` | Application business logic, validation, DB transaction handlers. | No PySide6 UI rendering or direct widget manipulation. |
| `database/` | Local SQLite database files (`college_fee.db`). | Excluded from version control tracking via `.gitignore`. |
| `dialogs/` | PySide6 modal dialog windows (`QDialog` subclasses). | Must delegate business logic to controllers. |
| `docs/` | System baseline markdown documentation and governance standards. | No temporary scratch files or binary dumps. |
| `models/` | Declarative SQLAlchemy ORM models (`models.base.Base` subclasses). | No UI logic or external service calls. |
| `phases/` | Phase-by-phase development control folders (`PHASE_00` to `PHASE_10`). | Each phase folder must contain `README.md`, `REPORT.md`, `CHECKLIST.md`, `NOTES.md`. |
| `release/` | Final release distribution packages (`v1.0.0` to `v2.0.0`). | Organized by semantic version tags. |
| `scripts/` | Project automation PowerShell build, clean, and release scripts. | All scripts must be fully documented. |
| `services/` | Technical services (PDF, Print, Backup, Export, Seeding). | Independent of UI views; reusable across CLI or GUI. |
| `tests/` | Automated unit and integration test scripts (`test_*.py`). | All test files must execute headlessly. |
| `utils/` | Shared helper modules, logger, security hashing, background workers. | General utility functions only. |
| `views/` | PySide6 main screen widgets (`QWidget` subclasses). | No direct raw SQL or SQLAlchemy session instantiations. |
| `.github/` | CI/CD workflows and GitHub template configurations. | Standard YAML configuration files. |

---

## 2. File Creation Guidelines

1. Never create random top-level directories outside the defined structure.
2. Maintain clean separation between source code and generated output artifacts (`build/`, `dist/`, `backup/`, `exports/`, `logs/`).
