# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

assets_path = Path('assets').resolve()

datas = [
    (str(assets_path), 'assets'),
    (str(Path('Version.txt').resolve()), '.'),
] + collect_data_files('reportlab')

hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtPrintSupport',
    'shiboken6',
    'sqlalchemy.ext.baked',
    'sqlalchemy.engine.interfaces',
    'sqlalchemy.dialects.sqlite',
    'reportlab.lib.pagesizes',
    'reportlab.platypus',
    'reportlab.lib.colors',
] + collect_submodules('reportlab') + collect_submodules('sqlalchemy')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'PIL._tkinter_finder',
        'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.Qt3D', 'PySide6.QtWebEngine',
        'PySide6.QtSensors', 'PySide6.QtPositioning', 'PySide6.QtBluetooth',
        'PySide6.QtNfc', 'PySide6.QtSerialPort', 'PySide6.QtMultimedia',
        'PySide6.QtSpatialAudio', 'PySide6.QtPdf', 'PySide6.QtWebSockets',
        'PySide6.QtTextToSpeech', 'PySide6.QtDesigner', 'PySide6.QtHelp'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CollegeFeeManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(assets_path / 'icons' / 'app_icon.ico'),
    version='file_version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CollegeFeeManager',
)
