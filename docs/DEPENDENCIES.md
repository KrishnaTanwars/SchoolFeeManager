# EduLedger ERP - Dependencies Specification
**Baseline Version**: 2.0.0 (Enterprise Edition)  
**Execution Environment**: Python 3.12.10 (64-bit on Windows 10/11)  

---

## 1. Third-Party Production Dependencies

| Package Name | Installed Version | License | Purpose | Required / Optional |
|---|---|---|---|---|
| **PySide6** | `6.11.1` | LGPLv3 | Primary Desktop GUI framework providing Qt6 bindings (`QtWidgets`, `QtGui`, `QtCore`, `QtPrintSupport`). | **REQUIRED** |
| **SQLAlchemy** | `2.0.51` | MIT | Object-Relational Mapping (ORM) and SQLite session manager. | **REQUIRED** |
| **ReportLab** | `5.0.0` | BSD | Commercial A4 PDF document layout & rendering engine. | **REQUIRED** |
| **PyInstaller** | `6.21.0` | GPLv2+ | Bundles Python app into standalone Windows `.exe` executable. | **REQUIRED (Build)** |
| **SQLite3** | `3.49.1` | Public Domain | Embedded SQLite relational database engine compiled with Python. | **REQUIRED** |

---

## 2. Standard Library Dependencies

The system relies on standard library modules included with Python 3.12:

| Library Module | Purpose |
|---|---|
| `os` & `sys` | Path management, process execution, runtime freezing detection (`sys._MEIPASS`). |
| `pathlib` | Object-oriented path manipulation (`Path`). |
| `datetime` | Date & timestamp formatting (`date.today()`, `datetime.utcnow()`). |
| `re` | Regular Expression validation (10-digit Indian mobile regex: `^[6-9]\d{9}$`). |
| `hashlib` | PBKDF2 SHA-256 password hashing. |
| `csv` | Tabular student import and report data exporting. |
| `zipfile` | Backup archive creation and extraction. |
| `shutil` | File copying and database file replacement. |
| `subprocess` | PyInstaller build execution invocation. |
| `unittest` | Automated headless testing suite framework. |

---

## 3. Recommended `requirements.txt`

```txt
PySide6==6.11.1
SQLAlchemy==2.0.51
reportlab==5.0.0
pyinstaller==6.21.0
```
