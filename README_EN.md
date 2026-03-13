# 📁 House Survey Workflow Assistant (Dracula Edition)  
**Create folders in batches / Excel smart updates / Dual-lane import**

[中文版本](README.md)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20%2F%20ttk-6f42c1)](https://docs.python.org/3/library/tkinter.html)
[![Theme](https://img.shields.io/badge/Theme-Dracula-bd93f9)](https://draculatheme.com/)
[![Excel](https://img.shields.io/badge/Excel-openpyxl-2ea44f)](https://openpyxl.readthedocs.io/)
[![Concurrency](https://img.shields.io/badge/Import-Dual%20lane%20concurrent-ff79c6)](#)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](#)
[![Last Commit](https://img.shields.io/github/last-commit/jhihhe/Folderbatchgenerationtool)](https://github.com/jhihhe/Folderbatchgenerationtool)
[![Issues](https://img.shields.io/github/issues/jhihhe/Folderbatchgenerationtool)](https://github.com/jhihhe/Folderbatchgenerationtool/issues)
[![Stars](https://img.shields.io/github/stars/jhihhe/Folderbatchgenerationtool?style=social)](https://github.com/jhihhe/Folderbatchgenerationtool/stargazers)

> “It’s only ¥28 per set.”  
> But if your folders are messy, you might not even earn that ¥28.

A desktop tool for real estate photography / house survey workflows: **batch folder generation**, **Excel auto-inheritance and writing**, **dual-lane concurrent import**, and **real-time income stats**.

![Interface Preview](README.jpg)

---

## Highlights (V2.1)
- **Faster Excel styling**: only processes the most recent non-today date block (no full-sheet repaint)
- **Green marking with K/L/M/N skipped**: preserves original formatting for those columns
- **Custom photographer name**: affects folder name, Excel filename, and the “Photographer” column
- **Persistent setting**: default empty on first launch, auto-restored on the next launch

---

## What you get

### 1) Batch Folder Generation (Photo + VR)
- One input list, two directory trees (Photo & VR)
- Automatic date-based directory structure
- Invalid character replacement for macOS/Windows paths
- Input cleanup for common store/team prefixes and suffixes

**Default structure (example)**
```text
{root}/2026相片/03月/0313{Photographer}/0313{Photographer}.xlsx
{root}/2026VR/03月/0313/
```

### 2) Excel Smart Engine (inherit + append + styling)
- If today’s Excel is missing, it looks back (default: 365 days) and copies the latest available template
- Appends all input lines (no dedup checks to avoid accidental misses)
- Detects and writes leading indices like `1.` / `1、`
- Auto-increments monthly count based on the previous row

**Styling rules**
- Today rows: HS column highlighted in yellow
- Last working day rows: whole row in green fill/green font (K/L/M/N skipped)

### 3) Dual-lane Concurrent Import (UI stays responsive)
- Photo and VR transfers run in parallel
- Live progress + file count + speed (e.g. `86.4 MB/s`)
- Safety behavior
  - Missing card / missing path: readable status instead of scary tracebacks
  - Empty source folder: safe no-op
  - Destination write test: catches permission/read-only issues early

### 4) “Purple Mood Bar” (the more you type, the purpler it gets)
The status bar color shifts based on the number of sets entered:
- 0–5 sets: fast ramp from gray → purple
- 5–10 sets: stable purple
- 10–30 sets: purple → pink gradient

It doesn’t change the output, but it changes your mood.

### 5) UI/UX Details (Dracula + editor-like input)
- Dracula dark theme for long sessions
- Editor-like input: line numbers, current-line highlight, synced scrolling
- Smooth hover transitions via color interpolation

---

## Quick Start

### Requirements
- Python 3.10+ (3.12 / 3.13 recommended)
- macOS / Windows / Linux

### Install dependency (for Excel features)
```bash
pip install openpyxl
```

### Run
```bash
python3 main.py
```

---

## Input example
One property per line; leading indices are optional:
```text
1. Store A ZhangSan WangjingSOHO Building 1 1101 East 2BR
2、Store B LiSi SomeCommunity Building 3 902 South-North 3BR
```

---

## Settings
- Photographer name is stored at: `~/.fangkan_helper_config.json`
- Default paths can be changed in `src/utils/config.py`

---

## Packaging (macOS .app / Windows .exe)
```bash
pip install pyinstaller
python3 -m PyInstaller --noconfirm --clean "房堪助手.spec"
```

---

## More screenshots
![UI Screenshot](界面.png)

---

## FAQ
### Excel save failed (file in use)
Close the Excel file first, then retry.

### What if Photographer name is empty?
- Photo folder becomes `.../{MMDD}` (no suffix)
- Excel file becomes `MMDD.xlsx`
