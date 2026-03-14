# House Survey Workflow Assistant

English | [中文](README.md)

![GitHub last commit](https://img.shields.io/github/last-commit/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=7c3aed)
![GitHub repo size](https://img.shields.io/github/repo-size/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=2563eb)
![GitHub stars](https://img.shields.io/github/stars/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=f59e0b)
![GitHub issues](https://img.shields.io/github/issues/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=ef4444)
![Electron](https://img.shields.io/badge/Electron-41.x-0ea5e9?style=for-the-badge&logo=electron)
![React](https://img.shields.io/badge/React-19.x-06b6d4?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-2563eb?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-22c55e?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)

![Refactored UI](重构版界面.png)

## Overview

This project streamlines real-estate media operations into one reliable workflow:

- parse listing lines
- generate Photo + VR folder trees
- run dual-lane media import
- append daily Excel records with style continuity

The repository keeps both tracks:

- Electron edition (mainline): modern UI, richer interactions, packaging-ready.
- Python edition (legacy-compatible): keeps old operational scripts available.

## Core Features

- Batch folder generation from plain text input.
- Concurrent photo/VR import with live progress and speed.
- Excel template inheritance + row append + style consistency.
- Device identification strategy: volume label first, EXIF as fallback.
- Cinematic interface effects and Star-Wars-style HUD editor.

## Repository Layout

```text
.
├── electron-app/            # Electron + React + TypeScript app
├── src/                     # Python implementation
├── assets/icons/            # Icon assets
├── README.md                # Chinese documentation
└── README_EN.md             # English documentation
```

## Quick Start (Electron mainline)

### Requirements

- Node.js 20+
- npm 10+
- macOS / Windows

### Development

```bash
cd electron-app
npm install
npm run dev
```

### Packaging

```bash
cd electron-app
npm run build -- --mac
npm run build -- --win
```

Build outputs are generated in `electron-app/dist/`, archived artifacts in `electron-app/release-artifacts/`.

## Quick Start (Python legacy)

```bash
pip install -r requirements.txt
python main.py
```

## Troubleshooting

- Black screen after packaging: ensure `dist` is included in bundle and renderer assets use relative paths.
- Icon not applied: verify `electron-app/build/icons/app.icns` and `app.ico` exist.
- Excel write failure: close the opened workbook and retry.

## Screenshots

![Main UI](README.jpg)
![Refactored UI](重构版界面.png)

## Tech Stack

- Electron, React, TypeScript, Vite
- Three.js, Framer Motion, Tailwind CSS
- ExcelJS, openpyxl

---

If this project helps your workflow, a Star is always appreciated.
