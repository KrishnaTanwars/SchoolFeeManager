"""
Master Release Automation Script for College Fee ERP (EduLedger ERP).
Generates PyInstaller Executable, Inno Setup Installer, Portable ZIP, Developer ZIP,
Documentation, Checksums, and Formatted Release Package.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_version() -> str:
    vfile = BASE_DIR / "Version.txt"
    if vfile.exists():
        v = vfile.read_text(encoding="utf-8").strip()
        if v.startswith("v"):
            return v
        return f"v{v}"
    return "v3.6.0"

VERSION_TAG = get_version() # e.g. "v2.3.0"
VERSION_NUM = VERSION_TAG.lstrip("v") # e.g. "2.3.0"

DIST_DIR = BASE_DIR / "dist" / "CollegeFeeManager"
BUILD_DIR = BASE_DIR / "build"
SETUP_OUTPUT_DIR = BASE_DIR / "dist_installer"
RELEASE_BASE = BASE_DIR / "release"
RELEASE_VER_DIR = RELEASE_BASE / VERSION_TAG

def log_step(step_name: str):
    print("\n" + "=" * 70)
    print(f"  [BUILD STEP] {step_name}")
    print("=" * 70)

def find_iscc() -> Path:
    """Locates Inno Setup Compiler ISCC.exe."""
    possible_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
    ]
    for p in possible_paths:
        if p.exists():
            return p
    # Try finding in PATH
    iscc_in_path = shutil.which("ISCC.exe") or shutil.which("iscc")
    if iscc_in_path:
        return Path(iscc_in_path)
    raise FileNotFoundError("Inno Setup Compiler (ISCC.exe) not found. Please install Inno Setup 6.")

def step_1_sync_version():
    log_step("1. Synchronizing Version Numbers Across Project Files")
    print(f"Target Release Version: {VERSION_TAG} ({VERSION_NUM})")
    
    # Sync file_version_info.txt
    file_ver_info = BASE_DIR / "file_version_info.txt"
    if file_ver_info.exists():
        content = file_ver_info.read_text(encoding="utf-8")
        ver_tuple = f"({VERSION_NUM.replace('.', ', ')}, 0)"
        ver_str = f"{VERSION_NUM}.0"
        import re
        content = re.sub(r'filevers=\(\d+,\s*\d+,\s*\d+,\s*\d+\)', f'filevers={ver_tuple}', content)
        content = re.sub(r'prodvers=\(\d+,\s*\d+,\s*\d+,\s*\d+\)', f'prodvers={ver_tuple}', content)
        content = re.sub(r"StringStruct\('FileVersion',\s*'[^']+'\)", f"StringStruct('FileVersion', '{ver_str}')", content)
        content = re.sub(r"StringStruct\('ProductVersion',\s*'[^']+'\)", f"StringStruct('ProductVersion', '{ver_str}')", content)
        file_ver_info.write_text(content, encoding="utf-8")
        print("Updated file_version_info.txt")
        
    print("Version synchronization complete.")

def step_2_build_executable():
    log_step("2. Building PyInstaller Binary Executable Distribution")
    spec_file = BASE_DIR / "CollegeFeeManager.spec"
    if not spec_file.exists():
        raise FileNotFoundError("CollegeFeeManager.spec not found!")
        
    cmd = [
        sys.executable, "-m", "PyInstaller", "--noconfirm",
        "--distpath", str(BASE_DIR / "dist"),
        "--workpath", str(BUILD_DIR),
        str(spec_file)
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"PyInstaller build failed with return code {res.returncode}")
        
    exe_file = DIST_DIR / "CollegeFeeManager.exe"
    if not exe_file.exists():
        raise FileNotFoundError(f"Expected executable not found at: {exe_file}")
    print(f"SUCCESS: PyInstaller Executable built at: {exe_file} ({exe_file.stat().st_size / (1024*1024):.2f} MB)")

def step_3_verify_executable():
    log_step("3. Verifying Executable Integrity & Assets")
    exe_file = DIST_DIR / "CollegeFeeManager.exe"
    if not exe_file.exists():
        raise FileNotFoundError(f"Missing executable: {exe_file}")
        
    # Copy top-level assets to dist root for portable mode if needed
    if (BASE_DIR / "assets").exists():
        shutil.copytree(BASE_DIR / "assets", DIST_DIR / "assets", dirs_exist_ok=True)

    required_assets = [
        DIST_DIR / "_internal" / "assets" / "icons" / "app_icon.ico",
        DIST_DIR / "_internal" / "assets" / "styles" / "theme.qss",
    ]
    for asset in required_assets:
        if not asset.exists():
            raise FileNotFoundError(f"Missing required bundled asset: {asset}")
            
    print("Executable integrity check PASSED!")

def step_4_build_installer():
    log_step("4. Building Professional Inno Setup Windows Installer")
    iscc_exe = find_iscc()
    iss_script = BASE_DIR / "installer.iss"
    
    cmd = [
        str(iscc_exe),
        f"/DMyAppVersion={VERSION_NUM}",
        f"/O{SETUP_OUTPUT_DIR}",
        f"/FCollegeFeeERP_Setup_{VERSION_TAG}",
        str(iss_script)
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Inno Setup compilation failed with code {res.returncode}")
        
    installer_file = SETUP_OUTPUT_DIR / f"CollegeFeeERP_Setup_{VERSION_TAG}.exe"
    if not installer_file.exists():
        # Fallback search in setup output dir
        setup_exes = list(SETUP_OUTPUT_DIR.glob("*.exe"))
        if setup_exes:
            installer_file = setup_exes[0]
        else:
            raise FileNotFoundError("Inno Setup installer file not found after build.")
            
    print(f"SUCCESS: Windows Installer Setup built at: {installer_file} ({installer_file.stat().st_size / (1024*1024):.2f} MB)")
    return installer_file

def step_5_create_portable_package(target_dir: Path) -> Path:
    log_step("5. Creating Standalone Portable Package")
    portable_root = target_dir / "CollegeFeeERP_Portable"
    if portable_root.exists():
        shutil.rmtree(portable_root)
    
    shutil.copytree(DIST_DIR, portable_root)
    
    # Create portable marker file
    (portable_root / ".portable").touch()
    
    # Seed database directory
    (portable_root / "database").mkdir(exist_ok=True)
    seed_db = BASE_DIR / "database" / "college_fee.db"
    if seed_db.exists():
        shutil.copy2(seed_db, portable_root / "database" / "college_fee.db")
        
    for d in ["logs", "backup", "exports", "settings", "reports", "cache", "temp"]:
        (portable_root / d).mkdir(exist_ok=True)
        
    # Copy essential docs to portable folder
    for doc in ["Version.txt", "License.txt", "README.md", "CHANGELOG.md", "USER_MANUAL.pdf", "INSTALLATION_GUIDE.pdf"]:
        src_doc = BASE_DIR / doc
        if src_doc.exists():
            shutil.copy2(src_doc, portable_root)
            
    zip_path = target_dir / f"CollegeFeeERP_Portable_{VERSION_TAG}.zip"
    if zip_path.exists():
        os.remove(zip_path)
        
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(portable_root):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(target_dir)
                zipf.write(file_path, arcname)
                
    shutil.rmtree(portable_root)
    print(f"SUCCESS: Portable Package ZIP created at: {zip_path} ({zip_path.stat().st_size / (1024*1024):.2f} MB)")
    return zip_path

def step_6_create_developer_package(target_dir: Path) -> Path:
    log_step("6. Creating Developer Source Code Package")
    source_zip_path = target_dir / f"CollegeFeeERP_Source_{VERSION_TAG}.zip"
    if source_zip_path.exists():
        os.remove(source_zip_path)
        
    exclude_dirs = {".git", ".venv", "build", "dist", "dist_installer", "release", "archive", "__pycache__", ".pytest_cache", ".idea", ".vscode"}
    exclude_exts = {".pyc", ".pyo", ".pyd", ".zip", ".exe"}

    with zipfile.ZipFile(source_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in exclude_exts:
                    continue
                if file_path == source_zip_path:
                    continue
                arcname = file_path.relative_to(BASE_DIR)
                zipf.write(file_path, arcname)
                
    print(f"SUCCESS: Developer Source Package created at: {source_zip_path} ({source_zip_path.stat().st_size / (1024*1024):.2f} MB)")
    return source_zip_path

def step_7_generate_documentation():
    log_step("7. Generating PDF Documentation & Release Notes")
    gen_doc_script = BASE_DIR / "generate_pdf_docs.py"
    if gen_doc_script.exists():
        res = subprocess.run([sys.executable, str(gen_doc_script)])
        if res.returncode != 0:
            print("Warning: Documentation PDF generation returned non-zero code.")
    print("Documentation ready.")

def step_8_compute_checksums(files_to_hash: list, target_dir: Path):
    log_step("8. Computing SHA256 & MD5 Checksums")
    sha256_lines = []
    md5_lines = []
    
    for fpath in files_to_hash:
        if not fpath.exists():
            continue
        rel_name = fpath.name
        
        # SHA256
        sha256_hash = hashlib.sha256()
        with open(fpath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        sha256_lines.append(f"{sha256_hash.hexdigest()}  {rel_name}")
        
        # MD5
        md5_hash = hashlib.md5()
        with open(fpath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                md5_hash.update(byte_block)
        md5_lines.append(f"{md5_hash.hexdigest()}  {rel_name}")
        
    sha_file = target_dir / "SHA256.txt"
    md5_file = target_dir / "MD5.txt"
    
    sha_file.write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")
    md5_file.write_text("\n".join(md5_lines) + "\n", encoding="utf-8")
    
    print(f"SUCCESS: Checksums written to {sha_file} and {md5_file}")

def step_9_assemble_release():
    log_step("9. Assembling Final Release Directory Structure")
    # Preserve existing release directories
    RELEASE_VER_DIR.mkdir(parents=True, exist_ok=True)
    
    installer_dir = RELEASE_VER_DIR / "Installer"
    portable_dir = RELEASE_VER_DIR / "Portable"
    developer_dir = RELEASE_VER_DIR / "Developer"
    checksums_dir = RELEASE_VER_DIR / "Checksums"
    docs_dir = RELEASE_VER_DIR / "Documentation"
    
    for d in [installer_dir, portable_dir, developer_dir, checksums_dir, docs_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    # Copy Installer Setup EXE
    setup_exes = list(SETUP_OUTPUT_DIR.glob("*.exe"))
    if not setup_exes:
        raise FileNotFoundError("Installer executable missing from dist_installer.")
    setup_exe = setup_exes[0]
    final_setup = installer_dir / f"CollegeFeeERP_Setup_{VERSION_TAG}.exe"
    shutil.copy2(setup_exe, final_setup)
    print(f"Installer copied to: {final_setup}")
    
    # Create Portable ZIP
    final_portable = step_5_create_portable_package(portable_dir)
    
    # Create Developer Source ZIP
    final_developer = step_6_create_developer_package(developer_dir)
    
    # Copy Documentation
    doc_files = [
        "Version.txt", "License.txt", "README.md", "CHANGELOG.md",
        "VERSION_HISTORY.md", "RELEASE_STATUS.md",
        "RELEASE_NOTES_v2.0.0.md", "RELEASE_NOTES_v2.1.0.md",
        "INSTALLATION_GUIDE.md", "INSTALLATION_GUIDE.pdf",
        "USER_MANUAL.md", "USER_MANUAL.pdf"
    ]
    rel_notes = BASE_DIR / f"RELEASE_NOTES_{VERSION_TAG}.md"
    if rel_notes.exists():
        shutil.copy2(rel_notes, docs_dir)
        
    for doc in doc_files:
        dpath = BASE_DIR / doc
        if dpath.exists():
            shutil.copy2(dpath, docs_dir)
            
    # Compute Checksums
    files_for_checksum = [final_setup, final_portable, final_developer]
    step_8_compute_checksums(files_for_checksum, checksums_dir)
    
    print("\n" + "=" * 70)
    print(f"  RELEASE PIPELINE COMPLETED SUCCESSFULLY FOR VERSION {VERSION_TAG}")
    print("=" * 70)
    print(f"Release Artifacts Location: {RELEASE_VER_DIR}")
    print(f"  |-- Installer/ : {final_setup.name}")
    print(f"  |-- Portable/   : {final_portable.name}")
    print(f"  |-- Developer/  : {final_developer.name}")
    print(f"  |-- Checksums/  : SHA256.txt, MD5.txt")
    print(f"  +-- Documentation/: PDF Manuals, Release Notes, License")
    print("=" * 70)

if __name__ == "__main__":
    step_1_sync_version()
    step_2_build_executable()
    step_3_verify_executable()
    step_4_build_installer()
    step_7_generate_documentation()
    step_9_assemble_release()
