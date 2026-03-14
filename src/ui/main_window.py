import sys
import os
import shutil
import platform
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
    QMessageBox, QGroupBox, QFrame, QApplication, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QAction

from src.utils.config import Config
from src.utils.fs_utils import get_date_based_dirs, resource_path
from src.services.folder_service import FolderService
from src.services.import_service import ImportTask
from src.ui.styles import get_stylesheet, THEMES
from src.ui.highlighter import FolderHighlighter

class ImportWorker(QThread):
    progress_photo = pyqtSignal(int, int, str)
    progress_vr = pyqtSignal(int, int, str)
    status = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, photo_src, vr_src, photo_dst, vr_dst):
        super().__init__()
        self.photo_src = photo_src
        self.vr_src = vr_src
        self.photo_dst = photo_dst
        self.vr_dst = vr_dst

    def run(self):
        # Concurrency Implementation
        
        # Photo Task Wrapper
        def run_photo_task():
            def on_photo_progress(curr, total, speed):
                self.progress_photo.emit(curr, total, speed)
            
            photo_task = ImportTask({
                'on_progress': on_photo_progress,
                'on_status_change': lambda msg: self.status.emit(f"相片: {msg}")
            })
            
            return photo_task.run({
                "src": str(self.photo_src),
                "dst": str(self.photo_dst),
                "kind": "photo",
                "label": "相片"
            })

        # VR Task Wrapper
        def run_vr_task():
            def on_vr_progress(curr, total, speed):
                self.progress_vr.emit(curr, total, speed)
                
            vr_task = ImportTask({
                'on_progress': on_vr_progress,
                'on_status_change': lambda msg: self.status.emit(f"VR: {msg}")
            })
            
            return vr_task.run({
                "src": str(self.vr_src),
                "dst": str(self.vr_dst),
                "kind": "vr",
                "label": "VR"
            })

        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_photo = executor.submit(run_photo_task)
            future_vr = executor.submit(run_vr_task)
            
            # Wait for both to complete
            results.append(future_photo.result())
            results.append(future_vr.result())
        
        self.finished.emit(results)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("房堪工作流助手")
        self.setWindowIcon(QIcon(resource_path("assets/icons/final_icon.png")))
        self.resize(960, 800)
        self.setMinimumSize(850, 650)
        
        # Device Monitor Timer
        self.device_timer = QTimer(self)
        self.device_timer.timeout.connect(self.check_devices)
        self.device_timer.start(2000) # Check every 2 seconds
        
        # Load theme preference or default
        self.current_theme = Config.get("theme", "Dracula (Official) - 德古拉(官方)")
        
        self.init_ui()
        self.apply_theme(self.current_theme)
        self.load_settings()
        
        # Initial check
        self.check_devices()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(20)

        # 1. Header Section (Title + Theme Selector)
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("房堪工作流助手")
        title_label.setObjectName("header_title")
        title_box.addWidget(title_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        # Theme Selector
        theme_box = QVBoxLayout()
        theme_label = QLabel("界面风格")
        theme_label.setStyleSheet("font-size: 12px; font-weight: bold; opacity: 0.7;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setFixedWidth(180)
        
        theme_box.addWidget(theme_label)
        theme_box.addWidget(self.theme_combo)
        header_layout.addLayout(theme_box)
        
        main_layout.addLayout(header_layout)

        # 2. Input Section
        input_group = QGroupBox(" 房源信息录入")
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(16, 24, 16, 16)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在此粘贴房源信息...\n例如：\n1.郭艳 HS251217836041 湘雅附一店 天健壹平方英里 A-2311 北")
        self.input_text.textChanged.connect(self.update_stats)
        
        # Syntax Highlighter
        self.highlighter = FolderHighlighter(self.input_text.document(), self.current_theme)
        
        input_layout.addWidget(self.input_text)
        
        # Stats & Tools
        tools_layout = QHBoxLayout()
        
        self.stats_label = QLabel("已输入: 0 | 预计收入: ¥0")
        self.stats_label.setObjectName("stats_label")
        tools_layout.addWidget(self.stats_label)
        
        tools_layout.addStretch()
        
        btn_example = QPushButton("示例填充")
        btn_example.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_example.clicked.connect(self.fill_example)
        tools_layout.addWidget(btn_example)
        
        btn_clear = QPushButton("清空")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_input)
        tools_layout.addWidget(btn_clear)
        
        input_layout.addLayout(tools_layout)
        main_layout.addWidget(input_group, stretch=1)

        # 3. Settings Section
        settings_group = QGroupBox(" 工作参数配置")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(16, 24, 16, 16)
        settings_layout.setSpacing(12)

        # Row 1: Photographer Name
        row1 = QHBoxLayout()
        lbl_pg = QLabel("摄影师姓名:")
        lbl_pg.setFixedWidth(80)
        row1.addWidget(lbl_pg)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入姓名自动保存")
        self.name_input.textChanged.connect(self.save_settings)
        row1.addWidget(self.name_input)
        
        settings_layout.addLayout(row1)

        # Row 2: Auto Path
        row2 = QHBoxLayout()
        lbl_path = QLabel("输出路径:")
        lbl_path.setFixedWidth(80)
        row2.addWidget(lbl_path)
        
        self.auto_path_display = QLineEdit()
        self.auto_path_display.setReadOnly(True)
        self.auto_path_display.setStyleSheet("font-style: italic; opacity: 0.8;")
        row2.addWidget(self.auto_path_display)
        
        # Path Tools
        # btn_open_root = QPushButton("📂") # Icon issue
        btn_open_root = QPushButton("打开")
        btn_open_root.setToolTip("打开当前工作目录")
        btn_open_root.setFixedWidth(60)
        btn_open_root.clicked.connect(lambda: self.open_dir("photo")) 
        row2.addWidget(btn_open_root)
        
        settings_layout.addLayout(row2)
        
        # Row 3: Advanced Buttons
        row3 = QHBoxLayout()
        
        btn_open_photo = QPushButton("打开相片")
        btn_open_photo.clicked.connect(lambda: self.open_dir("photo"))
        row3.addWidget(btn_open_photo)
        
        btn_open_vr = QPushButton("打开 VR")
        btn_open_vr.clicked.connect(lambda: self.open_dir("vr"))
        row3.addWidget(btn_open_vr)
        
        btn_copy = QPushButton("复制路径")
        btn_copy.clicked.connect(self.copy_paths)
        row3.addWidget(btn_copy)
        
        row3.addStretch()
        
        # btn_config = QPushButton("⚙️ 设置源路径") # Icon might be missing/invisible
        btn_config = QPushButton("设置源路径")
        btn_config.clicked.connect(self.show_path_config_dialog)
        row3.addWidget(btn_config)
        
        settings_layout.addLayout(row3)
        main_layout.addWidget(settings_group)

        # 4. Progress Section
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        
        # Photo
        h_photo = QHBoxLayout()
        lbl_p = QLabel("相片导入:")
        lbl_p.setFixedWidth(70)
        h_photo.addWidget(lbl_p)
        self.prog_photo = QProgressBar()
        self.prog_photo.setTextVisible(True)
        self.prog_photo.setFormat("%p%")
        h_photo.addWidget(self.prog_photo)
        progress_layout.addLayout(h_photo)
        
        # VR
        h_vr = QHBoxLayout()
        lbl_v = QLabel("VR 导入:")
        lbl_v.setFixedWidth(70)
        h_vr.addWidget(lbl_v)
        self.prog_vr = QProgressBar()
        self.prog_vr.setTextVisible(True)
        self.prog_vr.setFormat("%p%")
        h_vr.addWidget(self.prog_vr)
        progress_layout.addLayout(h_vr)
        
        main_layout.addLayout(progress_layout)

        # 5. Footer Actions
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(24)
        
        self.btn_import = QPushButton("📥 一键并发导卡")
        self.btn_import.setObjectName("btn_import")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.clicked.connect(self.import_files)
        footer_layout.addWidget(self.btn_import)
        
        self.btn_create = QPushButton("✨ 开始创建文件夹")
        self.btn_create.setObjectName("btn_create")
        self.btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create.clicked.connect(self.create_folders)
        footer_layout.addWidget(self.btn_create)
        
        main_layout.addLayout(footer_layout)

        # Status Bar & Device Monitor
        self.status_bar = self.statusBar()
        
        # Add permanent widget for device status (on the right)
        # But user wants it on the left where "Ready" was.
        # QStatusBar has a simple message area (left) and permanent widgets (right).
        # To put it on the left, we just use showMessage or a normal widget.
        # Let's replace the default message with a permanent label on the left.
        
        # Clear default message
        self.status_bar.clearMessage()
        
        # Create a widget to hold the status label on the left
        # Actually, addPermanentWidget adds to the right. 
        # addWidget adds to the left (before the stretch).
        
        self.device_status_label = QLabel("检测设备中...")
        self.device_status_label.setContentsMargins(10, 0, 0, 0)
        self.status_bar.addWidget(self.device_status_label)
        
        # self.status_bar.showMessage("就绪") # Remove this as requested
        
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)
        Config.set("theme", theme_name)
        
        # Update highlighter colors
        self.highlighter.set_theme(theme_name)

    def apply_theme(self, theme_name):
        self.setStyleSheet(get_stylesheet(theme_name))

    def check_devices(self):
        p_src = Config.get_photo_src()
        v_src = Config.get_vr_src()
        
        p_ok = os.path.exists(p_src)
        v_ok = os.path.exists(v_src)
        
        if p_ok and v_ok:
            self.device_status_label.setText("🟢 已连接相机 & 全景设备")
            self.device_status_label.setObjectName("status_ok")
        elif p_ok:
            self.device_status_label.setText("🟡 已连接相机 (未检测到 VR)")
            self.device_status_label.setObjectName("status_warn")
        elif v_ok:
            self.device_status_label.setText("🟡 已连接 VR (未检测到 相机)")
            self.device_status_label.setObjectName("status_warn")
        else:
            self.device_status_label.setText("🔴 未检测到设备")
            self.device_status_label.setObjectName("status_err")
            
        # Refresh style for the label to pick up new object name
        self.device_status_label.style().unpolish(self.device_status_label)
        self.device_status_label.style().polish(self.device_status_label)

    def update_progress_style(self, bar, value, total):
        # Dynamic color change based on progress
        percent = 0
        speed_text = ""
        
        # Calculate percent
        if total > 0:
            percent = int((value / total) * 100)
            
        # Get speed from bar format if possible, or we need to pass speed in.
        # The update_*_progress methods call this with just value/total.
        # We should modify this method signature to accept speed or 
        # modify the update_*_progress methods to set the text directly.
        
        # Let's change how this method works: it only styles. 
        # Text setting should happen in update_*_progress where speed is available.
        
        # Get theme colors for gradient
        t = THEMES.get(self.current_theme, THEMES["Dracula (Official) - 德古拉(官方)"])
        
        # Apply Style
        if percent >= 100:
            # Gold/Green Gradient for completion
            bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.GREEN}, stop:1 {t.YELLOW});
                    border-radius: 6px;
                }}
            """)
        else:
            # Dynamic Gradient
            if percent < 30:
                c1, c2 = t.RED, t.ORANGE
            elif percent < 70:
                c1, c2 = t.ORANGE, t.YELLOW
            else:
                c1, c2 = t.YELLOW, t.GREEN
                
            bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c1}, stop:1 {c2});
                    border-radius: 6px;
                }}
            """)

    def update_photo_progress(self, curr, total, speed):
        self.prog_photo.setMaximum(total)
        self.prog_photo.setValue(curr)
        
        # Set text with speed
        if curr >= total and total > 0:
             self.prog_photo.setFormat(f"✅ 完成 ({curr}/{total}) {speed}")
        else:
             self.prog_photo.setFormat(f"%p% ({curr}/{total}) {speed}")
             
        self.update_progress_style(self.prog_photo, curr, total)

    def update_vr_progress(self, curr, total, speed):
        self.prog_vr.setMaximum(total)
        self.prog_vr.setValue(curr)
        
        # Set text with speed
        if curr >= total and total > 0:
             self.prog_vr.setFormat(f"✅ 完成 ({curr}/{total}) {speed}")
        else:
             self.prog_vr.setFormat(f"%p% ({curr}/{total}) {speed}")
             
        self.update_progress_style(self.prog_vr, curr, total)

    # ... (Rest of the methods remain unchanged: load_settings, save_settings, etc.)
    
    def load_settings(self):
        Config.load_settings()
        self.name_input.setText(Config.get_photographer_name())
        self.update_auto_path_display()

    def save_settings(self):
        Config.set("photographer_name", self.name_input.text())
        self.update_auto_path_display()

    def update_auto_path_display(self):
        pg_name = self.name_input.text()
        targets = get_date_based_dirs(photographer_name=pg_name)
        if targets:
            self.auto_path_display.setText(targets[0])

    def update_stats(self):
        text = self.input_text.toPlainText()
        lines = [l for l in text.splitlines() if l.strip()]
        count = len(lines)
        revenue = count * Config.PRICE_PER_SHOOT
        self.stats_label.setText(f"已输入: {count} | 预计收入: ¥{revenue}")

    def fill_example(self):
        examples = [
            "1.郭艳 HS251217836041 湘雅附一店 天健壹平方英里 A-2311 北",
            "2.龙苗 HS251216879300 芙蓉盛世店 新力紫园 4-1707 北",
            "3.张三 HS260312222077 湘雅附一店 华远华时代 B53049 西"
        ]
        self.input_text.setPlainText("\n".join(examples))

    def clear_input(self):
        self.input_text.clear()

    def open_dir(self, kind):
        pg_name = self.name_input.text()
        targets = get_date_based_dirs(photographer_name=pg_name)
        path = targets[0] if kind == "photo" else targets[1]
        
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except:
                pass
                
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开目录:\n{e}")

    def copy_paths(self):
        pg_name = self.name_input.text()
        targets = get_date_based_dirs(photographer_name=pg_name)
        text = "\n".join(targets)
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage("路径已复制到剪贴板", 3000)

    def show_path_config_dialog(self):
        from PyQt6.QtWidgets import QDialog, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("路径配置")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(get_stylesheet(self.current_theme))
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        inputs = {}
        for key, label in [("root_dir", "工作根目录"), ("photo_src", "相片源目录 (SD卡)"), ("vr_src", "VR源目录 (SD卡)")]:
            row = QHBoxLayout()
            le = QLineEdit(str(Config.get(key) or ""))
            btn = QPushButton("浏览")
            
            def browse(k=key, line_edit=le):
                d = QFileDialog.getExistingDirectory(dialog, f"选择 {k}")
                if d:
                    line_edit.setText(d)
                    
            btn.clicked.connect(browse)
            row.addWidget(le)
            row.addWidget(btn)
            form.addRow(label, row)
            inputs[key] = le
            
        layout.addLayout(form)
        
        btn_box = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(lambda: self._save_paths(dialog, inputs))
        btn_box.addStretch()
        btn_box.addWidget(btn_save)
        
        layout.addLayout(btn_box)
        dialog.exec()

    def _save_paths(self, dialog, inputs):
        for key, le in inputs.items():
            val = le.text().strip()
            if val:
                Config.set(key, val)
        self.load_settings()
        dialog.accept()

    def create_folders(self):
        text = self.input_text.toPlainText()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            QMessageBox.warning(self, "提示", "请输入至少一个文件夹名称")
            return

        pg_name = self.name_input.text()
        
        self.btn_create.setEnabled(False)
        self.status_bar.showMessage("正在创建文件夹...")
        
        def callback(action, val):
            pass

        success, errors, target_dirs, excel_info = FolderService.create_folders(
            lines, callback, photographer_name=pg_name
        )

        if success is None:
             QMessageBox.critical(self, "严重错误", "\n".join(errors))
        else:
            msg = f"创建成功!\n\n相片目录: {success[target_dirs[0]]} 个\nVR 目录: {success[target_dirs[1]]} 个\n"
            msg += f"预计收入: ¥{success[target_dirs[0]] * Config.PRICE_PER_SHOOT}\n"
            msg += f"Excel 记录: 新增 {excel_info.get('added', 0)}, 跳过 {excel_info.get('skipped', 0)}"
            if excel_info.get('error'):
                msg += f"\nExcel 错误: {excel_info.get('error')}"
                
            QMessageBox.information(self, "完成", msg)
            if errors:
                QMessageBox.warning(self, "注意", "\n".join(errors))

        self.btn_create.setEnabled(True)
        self.status_bar.showMessage("就绪")

    def import_files(self):
        p_src = Config.get_photo_src()
        v_src = Config.get_vr_src()
        
        if not os.path.exists(p_src) and not os.path.exists(v_src):
            QMessageBox.warning(self, "未检测到设备", f"请检查存储卡是否插入。\n相片源: {p_src}\nVR源: {v_src}")
            return
            
        from ..utils.fs_utils import get_date_based_dirs
        base_root = Config.get_root_dir()
        targets = get_date_based_dirs(base_root=base_root, mode='import')
        photo_dst, vr_dst = targets[0], targets[1]
        
        self.btn_import.setEnabled(False)
        self.worker = ImportWorker(p_src, v_src, photo_dst, vr_dst)
        self.worker.progress_photo.connect(self.update_photo_progress)
        self.worker.progress_vr.connect(self.update_vr_progress)
        self.worker.status.connect(self.status_bar.showMessage)
        self.worker.finished.connect(self.on_import_finished)
        self.worker.start()

    def on_import_finished(self, results):
        self.btn_import.setEnabled(True)
        total_moved = sum(r[2] for r in results) 
        errors = []
        for r in results:
            if r[1]: 
                errors.extend(r[1])
        
        msg = f"导入完成。\n总计移动文件: {total_moved}"
        if errors:
            msg += f"\n异常数量: {len(errors)} (详情见日志)"
            QMessageBox.warning(self, "完成但有错误", msg + "\n" + "\n".join(errors[:5]))
        else:
            QMessageBox.information(self, "全部完成", msg)
        
        self.status_bar.showMessage("就绪")
