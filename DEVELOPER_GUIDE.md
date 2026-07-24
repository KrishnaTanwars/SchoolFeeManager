# School Fee Management System v1.0 - Developer Guide

This document outlines the developer architecture, code conventions, and maintenance procedures for the **School Fee Management System**.

---

## 1. Project Architecture (MVC + Service Layer)

The codebase is organized into modular layers:

- **`config/`**: System configuration, paths (`app_config.py`), and SQLAlchemy engine initialization (`database.py`).
- **`models/`**: SQLAlchemy ORM models (`student.py`, `fee_category.py`, `receipt.py`, `user.py`, `settings.py`, `audit.py`).
- **`controllers/`**: Core business logic and database transaction handling (`student_controller.py`, `fee_controller.py`, `receipt_controller.py`, `report_controller.py`, `auth_controller.py`, `settings_controller.py`).
- **`services/`**: Specialized system services:
  - `pdf_service.py`: ReportLab A4 Fee Receipt & tabular report generator.
  - `print_service.py`: `QtPrintSupport` Windows printing interface.
  - `backup_service.py`: SQLite backup & safety-checked restore engine.
  - `export_service.py`: CSV data exporter.
  - `db_seed.py`: Initial database seeder.
- **`views/` & `dialogs/`**: PySide6 UI views and popups.
- **`utils/`**: Utility modules:
  - `number_to_words.py`: Indian Currency Converter (Crores, Lakhs, Thousands, Rupees & Paise).
  - `security.py`: Password hashing using PBKDF2-HMAC-SHA256.
  - `helpers.py`: Validation (Indian phone regex), date and currency formatters.
  - `workers.py`: Background `QThread` workers.
  - `logger.py`: Centralized logging.

---

## 2. Database Design & Conventions

- Database file: `database/school_fee.db` (SQLite).
- Pragmas configured on connect:
  - `PRAGMA foreign_keys=ON;`
  - `PRAGMA journal_mode=WAL;`
- Thread safety: `SessionLocal` uses `scoped_session` bound to `check_same_thread=False`.

---

## 3. Adding New Features or Fee Categories

- **New Fee Category**: Fee categories are dynamically saved in the `fee_categories` table. No code modification is required to add or rename fee heads.
- **New Module Integration**: To add a new sidebar view (e.g. Attendance, ID Cards, Inventory), create a view in `views/`, register it in `views/main_window.py` in the `self.views` dictionary and navigation items list.

---

## 4. Running Unit Tests

Run unit tests from the workspace root:
```powershell
python -m unittest discover -s tests
```

---

## 5. Rebuilding Executable

To compile executable updates:
```powershell
python build.py
```
Output directory: `dist/SchoolFeeManager/`.
