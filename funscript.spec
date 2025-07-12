# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['funscript.py'],
    pathex=[],
    binaries=[('/usr/lib/python3.13/site-packages/keystone/libkeystone.so', '.'), ('/usr/lib/python3.13/site-packages/unicorn/lib/libunicorn.so.2', '.')],
    datas=[],
    hiddenimports=['unicorn.unicorn_py3.arch.intel', 'unicorn.unicorn_py3.arch', 'keystone'],
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
    name='funscript',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
