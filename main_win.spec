# -*- mode: python ; coding: utf-8 -*-

# Spec file for the refactored version

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('project_folder_structure.json', '.'), ('project_lists.json', '.')],
    hiddenimports=[
        'win32com.shell', 
        'win32com.shell.shell', 
        'pythoncom', 
        'pywintypes',
        'win32api',
        'win32con'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Project Folder Manager v3.3.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
