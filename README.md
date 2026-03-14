# 房勘工作流助手 · House Survey Workflow Assistant

[English](README_EN.md) | 中文

![GitHub last commit](https://img.shields.io/github/last-commit/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=7c3aed)
![GitHub repo size](https://img.shields.io/github/repo-size/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=2563eb)
![GitHub stars](https://img.shields.io/github/stars/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=f59e0b)
![GitHub issues](https://img.shields.io/github/issues/jhihhe/Folderbatchgenerationtool?style=for-the-badge&color=ef4444)
![Electron](https://img.shields.io/badge/Electron-41.x-0ea5e9?style=for-the-badge&logo=electron)
![React](https://img.shields.io/badge/React-19.x-06b6d4?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-2563eb?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-22c55e?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)

![重构版界面](重构版界面.png)

## 项目简介

这是一个面向房产摄影/VR 团队的生产力工具，核心目标是把“录入房源、建目录、导素材、写 Excel”串成一条稳定流水线。  
当前仓库同时保留：

- Electron 重构版（主线）：炫酷 UI、并发导卡、Excel 自动追加与样式继承。
- Python 版本（兼容）：历史脚本与旧工作流可继续使用。

## 关键能力

- 批量目录生成：一段文本同时生成“相片 + VR”目录树。
- 导卡并发同步：相片与 VR 双通道并发复制，实时显示速度与进度。
- Excel 智能写入：复制前日模板、追加当天数据、保持行高与样式一致。
- 设备识别策略：优先盘符名称，其次 EXIF 机型。
- 高级交互界面：3D 背景、电影级动效、星战 HUD 风输入框。

## 目录结构

```text
.
├── electron-app/            # Electron + React + TS 主线应用
├── src/                     # Python 版本核心代码
├── assets/icons/            # 图标资源
├── README.md                # 中文说明
└── README_EN.md             # English docs
```

## 快速开始（Electron 主线）

### 环境要求

- Node.js 20+
- npm 10+
- macOS / Windows

### 开发模式

```bash
cd electron-app
npm install
npm run dev
```

### 打包

```bash
cd electron-app
npm run build -- --mac
npm run build -- --win
```

构建产物位于 `electron-app/dist/`，归档产物位于 `electron-app/release-artifacts/`。

## 快速开始（Python 兼容版）

```bash
pip install -r requirements.txt
python main.py
```

## 常见问题

- 打包后黑屏：确认 `dist` 资源已被打包且前端资源路径为相对路径。
- 图标未生效：确认 `electron-app/build/icons/app.icns` 与 `app.ico` 存在。
- Excel 写入异常：先关闭正在占用的 Excel 文件后重试。

## 预览图

![界面预览](README.jpg)
![重构版预览](重构版界面.png)

## 致谢

- Electron / React / Vite / Framer Motion / Three.js
- ExcelJS / openpyxl

---

如果这个项目帮你节省了时间，欢迎点一个 Star。
