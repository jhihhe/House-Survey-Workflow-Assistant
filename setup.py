from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
        'argv_emulation': False,
    'iconfile': 'assets/icons/final_icon.icns',
    'packages': [],
    'includes': ['src', 'tkinter'],
    'plist': {
        'CFBundleName': "房堪助手",
        'CFBundleDisplayName': "房堪工作流助手",
        'CFBundleGetInfoString': "House Survey Workflow Assistant (Dracula Edition)",
        'CFBundleIdentifier': "com.jhihhe.housesurvey",
        'CFBundleVersion': "2.0.0",
        'CFBundleShortVersionString': "2.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024 JhihHe, All Rights Reserved"
    }
}

setup(
    app=APP,
    name="HouseSurveyAssistant",
    description="专为房产摄影工作流打造的桌面自动化工具",
    author="JhihHe",
    url="https://github.com/jhihhe/Folderbatchgenerationtool",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
