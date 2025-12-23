from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
        'argv_emulation': False,
        'iconfile': 'assets/icons/final_icon.png',
        'packages': [],
    'includes': ['src', 'tkinter'],
    'plist': {
        'CFBundleName': "房堪工具",
        'CFBundleDisplayName': "房堪文件夹生成",
        'CFBundleGetInfoString': "Folder Generator Dracula Edition",
        'CFBundleIdentifier': "com.trae.foldergenerator",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024 Trae User, All Rights Reserved"
    }
}

setup(
    app=APP,
    name="FolderGenerator",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
