# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('project_folder_structure.json', '.'), ('project_lists.json', '.')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Project Folder Manager v3.1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Project Folder Manager v3.1.0',
)
app = BUNDLE(
    coll,
    name='Project Folder Manager v3.1.0.app',
    icon=None,
    bundle_identifier=None,
)
