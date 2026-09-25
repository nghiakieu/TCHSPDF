# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/TCHSPDF/bookmark_app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/TCHSPDF/pdf_bookmark_parser.py', '.'), ('C:/TCHSPDF/text_search.py', '.'), ('C:/TCHSPDF/logo.ico', '.'), ('C:/TCHSPDF/app_icon.ico', '.'), ('C:/TCHSPDF/app_icon.png', '.')],
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
    name='TraCuuBanVePDF',
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
    icon=['C:/TCHSPDF/logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TraCuuBanVePDF',
)
