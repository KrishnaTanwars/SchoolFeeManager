"""
Release Packaging Script for School Fee Management System v1.0.
Bundles clean client release ZIP and developer source ZIP packages with PDF Documentation.
"""

import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist" / "SchoolFeeManager"
RELEASE_DIR = BASE_DIR / "release" / "v1.1.0"
CLIENT_ZIP_PATH = RELEASE_DIR / "SchoolFeeManager_v1.1.0.zip"
SOURCE_ZIP_PATH = RELEASE_DIR / "SchoolFeeManager_Source_v1.1.0.zip"

def create_client_package():
    print("============================================================")
    print("Creating Clean Client Release Package (v1.1.0)...")
    print("============================================================")

    if not DIST_DIR.exists():
        raise FileNotFoundError(f"Executable dist folder not found at: {DIST_DIR}. Run build.py first!")

    # Wipe existing release/v1.1.0 completely to prevent stale artifact leftover
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    client_dist = RELEASE_DIR / "SchoolFeeManager"
    client_dist.mkdir(parents=True, exist_ok=True)

    # Copy PyInstaller bundled executable & dependencies (exact copy of dist/)
    shutil.copytree(DIST_DIR, client_dist, dirs_exist_ok=True)

    # Copy initial database file if present
    (client_dist / "database").mkdir(exist_ok=True)
    active_db = BASE_DIR / "database" / "school_fee.db"
    if active_db.exists():
        shutil.copy2(active_db, client_dist / "database" / "school_fee.db")

    (client_dist / "backup").mkdir(exist_ok=True)
    (client_dist / "exports").mkdir(exist_ok=True)
    (client_dist / "logs").mkdir(exist_ok=True)

    # Copy Release Documentation
    docs_to_copy = [
        "Version.txt", "License.txt", "README.md", "CHANGELOG.md",
        "PHASE_01_REPORT.md", "PHASE_01_RUNTIME_VALIDATION.md",
        "INSTALLATION_GUIDE.md", "INSTALLATION_GUIDE.pdf",
        "USER_MANUAL.md", "USER_MANUAL.pdf"
    ]
    for doc in docs_to_copy:
        doc_src = BASE_DIR / doc
        if doc_src.exists():
            shutil.copy(doc_src, client_dist)

    # Create ZIP archive containing the exact release directory
    if CLIENT_ZIP_PATH.exists():
        os.remove(CLIENT_ZIP_PATH)

    with zipfile.ZipFile(CLIENT_ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(client_dist):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(RELEASE_DIR)
                zipf.write(file_path, arcname)

    print(f"SUCCESS: Client Package Created at: {CLIENT_ZIP_PATH}")

def create_source_package():
    print("============================================================")
    print("Creating Developer Source Package...")
    print("============================================================")

    if SOURCE_ZIP_PATH.exists():
        os.remove(SOURCE_ZIP_PATH)

    exclude_dirs = {".git", ".venv", "build", "dist", "release_v1.0", "__pycache__", ".pytest_cache", ".idea", ".vscode"}
    exclude_exts = {".pyc", ".pyo", ".pyd", ".zip"}

    with zipfile.ZipFile(SOURCE_ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in exclude_exts:
                    continue
                if file_path == CLIENT_ZIP_PATH or file_path == SOURCE_ZIP_PATH:
                    continue
                arcname = file_path.relative_to(BASE_DIR)
                zipf.write(file_path, arcname)

    print(f"SUCCESS: Developer Source Package Created at: {SOURCE_ZIP_PATH}")

if __name__ == "__main__":
    create_client_package()
    create_source_package()
    print("============================================================")
    print("ALL RELEASE PACKAGES GENERATED SUCCESSFULLY!")
    print("============================================================")
