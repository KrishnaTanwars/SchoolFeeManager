"""
PyInstaller Build Orchestration Script.
Builds single-folder distribution for Windows 10 / Windows 11.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_build():
    print("=" * 60)
    print("Building College Fee Management System Executable...")
    print("=" * 60)

    spec_file = Path(__file__).parent / "CollegeFeeManager.spec"
    
    dist_path = Path(__file__).parent / "dist"
    work_path = Path(__file__).parent / "build"
    cmd = [
        sys.executable, "-m", "PyInstaller", "--noconfirm",
        "--distpath", str(dist_path),
        "--workpath", str(work_path),
        str(spec_file)
    ]
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("Executable output directory: dist/CollegeFeeManager/CollegeFeeManager.exe")
        print("=" * 60)
    else:
        print("\nBUILD FAILED!")
        sys.exit(res.returncode)

if __name__ == "__main__":
    run_build()
