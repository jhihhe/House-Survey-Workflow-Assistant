# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Ensure current directory is in path so PyInstaller can find 'src'
sys.path.insert(0, os.path.abspath('.'))

tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all('src')

hidden_imports = tmp_hiddenimports
# Add src.ui.styles explicitly just in case
if 'src.ui.styles' not in hidden_imports:
    hidden_imports.append('src.ui.styles')

block_cipher = None

# Determine icon based on platform
icon_file = None
if sys.platform == 'darwin':
    icon_file = 'assets/icons/final_icon.icns'
elif sys.platform == 'win32':
    # Ideally use .ico for Windows
    if os.path.exists('assets/icons/final_icon.ico'):
        icon_file = 'assets/icons/final_icon.ico'
    else:
        # Fallback to None or try png if supported (usually not for exe icon)
        icon_file = None 

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=tmp_binaries,
    datas=[('assets', 'assets')] + tmp_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='HouseSurveyAssistant',
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
    icon=icon_file
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='HouseSurveyAssistant.app',
        icon=icon_file,
        bundle_identifier='com.jhihhe.housesurvey',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '2.0.0',
            'CFBundleVersion': '2.0.0',
            'NSHumanReadableCopyright': "Copyright © 2024 JhihHe, All Rights Reserved"
        },
    )
else:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='HouseSurveyAssistant',
    )
