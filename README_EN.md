# 📁 House Survey Workflow Assistant · V2 (Dracula Edition)
**House Survey Workflow Assistant**

> **"It's only 28 per set, why work so hard?"**
> But if the folders are messy, you might not even earn that 28.

This is a **desktop automation tool tailored for real estate photography / survey workflows**.
It doesn't just solve "how to create folders," but rather—
**Creating folders repeatedly every day, creating them correctly, quickly, and with a good mood.**

The V2 version maintains **Python native, zero dependency, out-of-the-box** features, while completely refactoring **UI experience, interaction details, and concurrency performance**.
In a nutshell: **Not just usable, but handy, good-looking, and emotionally satisfying.**

![Interface Preview](README.jpg)

---

## ✨ Introduction

The daily reality of house survey photography is usually like this:

- How many sets today?
- Should the Photo and VR directories be aligned?
- Is the date correct?
- Are there any "/" in the filenames?
- Did the interface freeze while importing cards?
- After shooting a bunch, only one sentence remains in my mind: "What am I doing?"

This tool is designed to solve these "seemingly simple but energy-consuming small things".

It is a **cross-platform desktop GUI application** focused on three things:

1. **Creating folders correctly at once**
2. **Importing materials completely at once**
3. **Calculating income clearly**

And the V2 version makes these three things **faster, more stable, and better looking**.

---

## 🚀 Core Features Overview

### 📂 1. Batch Folder Generation (Essential for Survey)

- **One Input, Dual Sync**
  - Create corresponding property folders in both "Photo" and "VR" directories simultaneously
- **Automatic Date Recognition**
  - Year / Month / Day automatically matched, no manual typing needed
- **Standardized Directory Structure**
  - Photo Directory:
    `.../{YYYY}Photo/{MM}Month/{MMDD}HeZhi`
  - VR Directory:
    `.../{YYYY}VR/{MM}Month/{MMDD}`
- **Illegal Character Auto-Cleaning**
  - `/ \ : * ? " < > |` automatically replaced, works on macOS / Windows
- **One-Click High-Frequency Operations**
  - Open directory / Copy path / Fill example, no thinking required

---

### 💰 2. Real-time Income Calculation (Spiritual Support System)

- Automatically calculate estimated income for today at **¥28 / set**
- Updates instantly upon input and creation
- Popup prompt upon completion:
  > "Not a loss today, at least it's purple."

---

### ⚡️ 3. High-Speed Smart Import (V2 Major Upgrade)

V2 introduces truly **perceptible performance improvements**:

#### 🚄 Multi-threaded Concurrent Import
- Background multi-threaded file IO processing
- **Interface does not freeze during card import**
- Photo / VR **dual parallel transmission**

#### 📊 Geek-level Progress Visualization
- Real-time transmission speed display (e.g., `86.4 MB/s`)
- Dual progress bars independently displayed:
  - Percentage
  - File count (`23 / 51`)
- You can clearly know:
  - It's working
  - It's fast
  - It's not slacking off

#### 🛡 Safety Mechanism
- Memory card not inserted → Auto skip
- Source directory empty → No error, no scare
- All paths undergo existence verification

---

## 🎨 V2 UI / UX Deep Upgrade (Highlight)

> **The UI upgrade of Project V2 is entirely based on the Python standard library.**
> No third-party UI frameworks were introduced.

### 🧛 Dracula Dark Theme
- Full interface adopts **Dracula official color scheme**
- Eye-friendly, restrained, not cheap
- Not just "dimmed," but a systematic color specification

---

### 🧠 VS Code-like Editor Experience
- Custom input component implementation:
  - **Line number display**
  - **Current line highlight**
  - **Text and line number synchronous scrolling**
- Used to fill in property names, but with the ritual of writing code

---

### 🌊 Native Fluid Animation
- Color interpolation algorithm for button Hover
- Smooth gradient, no jumping, no flickering
- **Completely independent of third-party animation libraries**

---

### 💜 "Purple Air Comes from the East" Mood Status Bar
- The status bar color changes according to the number of survey sets entered
- From calm dark gray → rich light purple
- The more sets, the "purpler" it gets
- A very unnecessary, but very useful design

---

### 🖥 Cross-Platform Adaptation
- Auto-detect Windows / macOS / Linux
- macOS Retina high-resolution screen adaptation
- Windows DPI scaling support
- Font auto-switching:
  - Windows: Microsoft YaHei
  - macOS: Helvetica

---

## 🛠 Tech Stack

- **Language**: Python 3.x
- **GUI**: Tkinter / ttk (Standard Library)
- **Concurrency**: threading + UI safe callbacks
- **File System**: os / shutil
- **Dependency**: **Zero Dependency**

> No `pip install` needed
> No virtual environment needed
> No need to explain "why it won't open"

---

## 🚀 Quick Start

### Environment Requirements
- Python 3.x
- macOS / Windows / Linux
- macOS recommended (default path fits survey habits better)

### How to Run
```bash
python3 main.py
```

---


## 📌 Who is this for?

If you fit any of the following, this tool will likely save you from cursing your computer every day:

- **Real Estate Photographers / Survey Practitioners**
  Creating directories, copying materials, checking dates every day until you doubt life.

- **VR / Panorama Shooters**
  Photo and VR dual lines parallel, most afraid of messy directories, leading to overtime in post-production.

- **High-Frequency Shooting, Multi-Set Burst Mode**
  Shooting a dozen sets a day, manually creating folders isn't impossible, it's just not worth it.

- **People who hate "usable but hard to use" tools**
  Not pursuing fancy things, but at least it should be handy, stable, and humane.

- **Tool enthusiasts with basic UI aesthetic requirements**
  Dark theme, detail animation, status feedback, don't want to compromise on any.

---

**28 per set, indeed not expensive.**
But if the tool is a bit handier,
A little less annoying every day,
Then earning that 28 won't feel so suffocating.

*Created with ❤️ by JhihHe*
