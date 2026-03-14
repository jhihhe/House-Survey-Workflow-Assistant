# 📁 房堪工作流自动化助手（Dracula 版 - PyQt6 重构）

**House Survey Workflow Assistant**

专为房产摄影工作流打造的桌面工具，采用 PyQt6 重构，界面更现代化，功能更稳定。

## ✨ 主要功能

### 1. 批量创建文件夹
- **双路生成**：输入房源名称，同时生成“相片”和“VR”两套目录。
- **自动归档**：按 `年/月/日` 结构自动创建，无需手动管理层级。
- **Excel 自动记录**：自动将生成的文件夹记录到每日 Excel 表格中，支持从历史数据继承表头和样式。

### 2. 智能导卡（一键导入）
- **并发导入**：同时从相片卡（Sigma/Sony）和 VR 卡（Insta360/Osmo）导入素材。
- **进度追踪**：实时显示进度条、文件数量和传输速度。
- **自动归档**：自动将素材导入到对应的“原片”目录。

### 3. 现代化界面
- **Dracula 主题**：深色模式，护眼且专业。
- **设置面板**：直接在界面上配置“工作根目录”、“相片源目录”、“VR 源目录”，无需修改代码。
- **跨平台**：完美支持 macOS 和 Windows，路径自动适配。

## 🚀 使用指南

### 运行环境
- Python 3.10+

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动应用
```bash
python main.py
```

## 📦 打包指南 (生成 .app 或 .exe)

本皆目包含 `build.spec` 配置文件，支持一键打包。

### macOS
生成 `.app` 应用程序：
```bash
pyinstaller build.spec
```
完成后在 `dist/` 目录下找到 `HouseSurveyAssistant.app`。

### Windows
生成 `.exe` 可执行文件：
```bash
pyinstaller build.spec
```
完成后在 `dist/` 目录下找到 `HouseSurveyAssistant` 文件夹（包含 exe）。

## ⚙️ 配置
所有设置（摄影师姓名、路径）会自动保存到用户目录下的配置文件 `~/.fangkan_helper_config.json` 中。

## 📝 更新日志
- **v3.0 (PyQt6)**: 
    - 核心 UI 重写，移除 Tkinter。
    - 新增可视化设置面板，路径不再硬编码。
    - 优化多线程导入逻辑，界面不卡顿。
    - 统一 macOS 和 Windows 的打包配置。

---
Copyright © 2024 JhihHe, All Rights Reserved.
