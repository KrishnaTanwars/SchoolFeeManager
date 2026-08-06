# EduLedger ERP - Coding Standards & Style Guide
**Baseline Version**: 1.0.0  
**Target Environment**: Python 3.12+ / PySide6 / SQLAlchemy 2.0  

---

## 1. General Python Standards (PEP 8)

- **Indentation**: 4 spaces per indentation level. Do not use hard tabs.
- **Line Length**: Limit code lines to a maximum of 100 characters where reasonable.
- **Naming Conventions**:
  - `snake_case` for module names, function names, variable names, and database column attributes.
  - `PascalCase` for class names, PySide6 widget subclasses, and ORM model names.
  - `UPPER_SNAKE_CASE` for constants and configuration keys.
- **Type Annotations**: All public controller functions, service methods, and helper utilities MUST include explicit Python type hints (e.g. `def create_receipt(student_id: int, items: List[dict]) -> Tuple[bool, str, Optional[Receipt]]:`).
- **Docstrings**: Include module-level docstrings and function docstrings explaining purpose, arguments, and return types.

---

## 2. PySide6 GUI Coding Standards

1. **Explicit Parent Ownership**: Always pass parent widgets (e.g. `super().__init__(parent)`) to ensure proper Qt object tree garbage collection.
2. **Signal/Slot Connections**: Connect Qt signals to explicit handler slots using strong syntax (e.g., `self.btn_save.clicked.connect(self._on_save_clicked)`). Avoid lambda functions for complex slot handlers.
3. **No Direct DB Queries in Views**: Views MUST call `Controller` static methods to retrieve or persist data. Views MUST NEVER instantiate SQLAlchemy sessions directly.
4. **Layout Management**: Use PySide6 layouts (`QVBoxLayout`, `QHBoxLayout`, `QFormLayout`, `QGridLayout`) exclusively. Do not use fixed coordinate positioning (`setGeometry`).
5. **UI Thread Safety**: Long-running file operations or network tasks MUST run inside `utils.workers.WorkerThread` (`QThread`) to keep the main GUI responsive.

---

## 3. SQLAlchemy & Database Coding Standards

1. **Scoped Session Hygiene**: Retrieve sessions via `get_db()`. Always close sessions inside `finally:` blocks:
   ```python
   db = get_db()
   try:
       # perform queries
       db.commit()
   except Exception as e:
       db.rollback()
       raise e
   finally:
       db.close()
   ```
2. **SQLAlchemy 2.0 Query Syntax**: Use `db.execute(select(Model).where(...))` syntax rather than legacy `db.query(Model)`.
3. **Relation Eager Loading**: Explicitly specify `options(joinedload(Receipt.student))` when querying models whose attributes will be accessed after session closure.

---

## 4. Error Handling & Logging Standards

- Use the centralized logger (`from utils.logger import logger`).
- Never swallow exceptions with empty `except:` blocks. Always log exceptions with detailed context (`logger.error("Failed to issue receipt", exc_info=True)`).
- Return standard tuple response format from controllers: `(success: bool, message: str, data: Any)`.
