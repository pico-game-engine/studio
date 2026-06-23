# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Pico Game Engine Studio.
#
# Build with:
#   pyinstaller PicoGameEngineStudio.spec
#
# Output: dist/PicoGameEngineStudio.app  

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['studio.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[],
    hiddenimports=[
        # customtkinter dynamic imports
        'customtkinter',
        'darkdetect',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageOps',
        # tkinter font module (used by CTkFont)
        'tkinter.font',
        'tkinter.filedialog',
        # Our own modules (PyInstaller sometimes misses package-relative imports)
        'helpers.color',
        'helpers.presets',
        'views.code_view',
        'views.creator_view',
        'views.export_view',
        'views.presets_view',
        'views.property_view',
        'views.settings_view',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Unnecessary bulk
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'notebook',
        'jupyter',
        'IPython',
        'PyQt5',
        'PySide6',
        'PyQt6',
        'PySide2',
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
    name='PicoGameEngineStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # windowed app — no terminal window on launch
    disable_windowed_traceback=False,
    argv_emulation=True,   # required for macOS .app bundles
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PicoGameEngineStudio',
)

app = BUNDLE(
    coll,
    name='PicoGameEngineStudio.app',
    icon=None,
    bundle_identifier='com.picogameengine.studio',
    version='1.0.0',
    info_plist={
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Pico Game Engine',
    },
)
