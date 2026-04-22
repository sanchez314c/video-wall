# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('m3u8-hosts.m3u8', '.'), ('src', 'src'), ('resources', 'resources')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets', 'PyQt5.QtNetwork'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['scripts/qt_plugin_path_hook.py'],
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
    name='VideoWall',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/icon.png',
)

app = BUNDLE(
    exe,
    name='VideoWall.app',
    icon='resources/icons/icon.png',
    bundle_identifier='com.videowall.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
    },
)
