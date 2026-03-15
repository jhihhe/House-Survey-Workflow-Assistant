import sys
import os
import shutil
import platform
import math
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, 
    QMessageBox, QGroupBox, QFrame, QApplication, QComboBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QRectF
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QAction, QPainter, QPen, QLinearGradient, QBrush, QRadialGradient

from src.utils.config import Config
from src.utils.fs_utils import get_date_based_dirs, resource_path
from src.services.folder_service import FolderService
from src.services.import_service import ImportTask
from src.ui.styles import get_stylesheet, THEMES
from src.ui.highlighter import FolderHighlighter


class StarWarsDisplayTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._accent = QColor("#8be9fd")
        self._phase = 0
        self.setViewportMargins(12, 14, 12, 14)
        self.document().setDocumentMargin(24)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(36)

    def _tick(self):
        self._phase = (self._phase + 4) % 1000
        self.viewport().update()

    def set_hud_palette(self, accent: QColor):
        self._accent = QColor(accent)
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w = self.viewport().width()
        h = self.viewport().height()
        top_h = 24
        bottom_h = 30
        margin = 12  # Use a fixed symmetric margin for both top and bottom corners
        bottom_base = h - margin  # The Y coordinate of the bottom corner line
        bottom_band_top = bottom_base - bottom_h + 6

        top_band = QColor(6, 20, 36, 160)
        bottom_band = QColor(6, 20, 36, 160)
        painter.fillRect(QRectF(0, 0, w, top_h), top_band)
        painter.fillRect(QRectF(0, bottom_band_top, w, bottom_h), bottom_band)

        scan = QColor(self._accent)
        scan.setAlpha(13)
        painter.setPen(scan)
        for y in range(0, h, 3):
            painter.drawLine(0, y, w, y)

        grid = QColor(self._accent)
        grid.setAlpha(9)
        painter.setPen(grid)
        for x in range(0, w, 22):
            painter.drawLine(x, 0, x, h)

        warp = QColor(self._accent)
        warp.setAlpha(14)
        painter.setPen(warp)
        for y in range(0, h, 9):
            offset = math.sin((y * 0.06) + (self._phase * 0.035)) * 7.5
            painter.drawLine(int(offset), y, int(w + offset), y)

        sweep_x = (self._phase / 1000.0) * (w + 260) - 130
        sweep = QLinearGradient(sweep_x - 120, 0, sweep_x + 120, 0)
        c0 = QColor(self._accent)
        c0.setAlpha(0)
        c1 = QColor(self._accent)
        c1.setAlpha(58)
        sweep.setColorAt(0.0, c0)
        sweep.setColorAt(0.5, c1)
        sweep.setColorAt(1.0, c0)
        painter.fillRect(QRectF(sweep_x - 120, 0, 240, h), QBrush(sweep))

        halo = QRadialGradient(w * 0.52, h * 0.25, h * 0.7)
        h0 = QColor(self._accent)
        h0.setAlpha(22)
        h1 = QColor(self._accent)
        h1.setAlpha(0)
        halo.setColorAt(0, h0)
        halo.setColorAt(1, h1)
        painter.fillRect(QRectF(0, 0, w, h), QBrush(halo))

        noise = QColor(self._accent)
        noise.setAlpha(18)
        painter.setPen(noise)
        for i in range(140):
            x = (i * 73 + self._phase * 3) % max(1, w)
            y = (i * 47 + self._phase * 5) % max(1, h)
            painter.drawPoint(int(x), int(y))

        glitch = QColor(self._accent)
        glitch.setAlpha(22)
        painter.setPen(glitch)
        for i in range(6):
            gy = int(((self._phase * (i + 3)) % max(10, h - 10)))
            gw = int(w * (0.18 + (i * 0.1)))
            gx = int((self._phase * (i + 5) * 1.7) % max(1, w - gw))
            painter.fillRect(QRectF(gx, gy, gw, 1), glitch)

        corner = QPen(QColor(self._accent))
        corner.setWidth(2)
        painter.setPen(corner)
        size = 16
        # Draw corners symmetrically using `margin` and `bottom_base`
        painter.drawLine(margin, margin, margin + size, margin)
        painter.drawLine(margin, margin, margin, margin + size)
        painter.drawLine(w - margin - size, margin, w - margin, margin)
        painter.drawLine(w - margin, margin, w - margin, margin + size)
        painter.drawLine(margin, bottom_base, margin + size, bottom_base)
        painter.drawLine(margin, bottom_base - size, margin, bottom_base)
        painter.drawLine(w - margin - size, bottom_base, w - margin, bottom_base)
        painter.drawLine(w - margin, bottom_base - size, w - margin, bottom_base)

        text_color = QColor(self._accent)
        text_color.setAlpha(205)
        painter.setPen(text_color)
        f = QFont("Menlo")
        f.setPointSize(8)
        f.setBold(True)
        painter.setFont(f)
        
        fm = painter.fontMetrics()
        auth_text = "AUTH: PHOTOGRAPHER"
        link_text = "LINK_STABLE"
        
        # Top text: y=margin + 12 (to sit nicely inside the top bracket)
        top_y = margin + 12
        painter.drawText(margin + 6, top_y, "NAVI-COMM // INPUT_CHANNEL")
        painter.drawText(w - margin - 6 - fm.horizontalAdvance(auth_text), top_y, auth_text)
        
        # Bottom text: y=bottom_base - 4 (to sit nicely above the bottom bracket)
        bottom_y = bottom_base - 4
        painter.drawText(margin + 6, bottom_y, "SECTOR: CN-CHANGSHA")
        painter.drawText(w - margin - 6 - fm.horizontalAdvance(link_text), bottom_y, link_text)
        
        painter.end()

class CRTEffectOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._phase = 0
        self._color = QColor("#8be9fd")
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def set_color(self, color: QColor):
        self._color = color
        self.update()

    def _tick(self):
        self._phase = (self._phase + 1) % 100
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()

        # 1. Vignette (CRT Corners / 暗角)
        gradient = QRadialGradient(w/2, h/2, math.hypot(w/2, h/2))
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.65, QColor(0, 0, 0, 30))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 190))
        painter.fillRect(0, 0, w, h, QBrush(gradient))

        # 2. Global subtle scanlines (全局扫描线)
        scan_color = QColor(0, 0, 0, 20)
        painter.setPen(scan_color)
        for y in range(0, h, 3):
            painter.drawLine(0, y, w, y)

        # 3. Slow interference refresh bar (屏幕刷新干扰纹)
        bar_y = (self._phase / 100.0) * h * 1.5 - (h * 0.25)
        bar_grad = QLinearGradient(0, bar_y - 40, 0, bar_y + 40)
        c = QColor(self._color)
        c.setAlpha(0)
        c_mid = QColor(self._color)
        c_mid.setAlpha(8)
        bar_grad.setColorAt(0.0, c)
        bar_grad.setColorAt(0.5, c_mid)
        bar_grad.setColorAt(1.0, c)
        painter.fillRect(QRectF(0, bar_y - 40, w, 80), QBrush(bar_grad))
        
        # 4. Sparse screen noise (做旧噪点)
        noise_color = QColor(self._color)
        noise_color.setAlpha(12)
        painter.setPen(noise_color)
        for _ in range(300):
            nx = random.randint(0, w)
            ny = random.randint(0, h)
            painter.drawPoint(nx, ny)

        painter.end()


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
        self.resize(1280, 1100)
        self.setMinimumSize(1200, 1000)
        
        # Device Monitor Timer
        self.device_timer = QTimer(self)
        self.device_timer.timeout.connect(self.check_devices)
        self.device_timer.start(2000) # Check every 2 seconds
        self._hud_phase = 0
        self._device_state_text = "SCANNING DEVICES"
        self.hud_timer = QTimer(self)
        self.hud_timer.timeout.connect(self.tick_hud)
        self.hud_timer.start(140)
        
        # Load theme preference or default
        self.current_theme = Config.get("theme", "Dracula (Official) - 德古拉(官方)")
        
        self.init_ui()
        
        # Initialize Global CRT Overlay
        self.crt_overlay = CRTEffectOverlay(self)
        self.crt_overlay.raise_()
        
        self.apply_theme(self.current_theme)
        self.load_settings()
        
        # Initial check
        self.check_devices()
        QTimer.singleShot(0, self.ensure_default_geometry)

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
        self.title_label = QLabel("房堪工作流助手")
        self.title_label.setObjectName("header_title")
        title_box.addWidget(self.title_label)
        
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
        input_layout.setSpacing(12)
        
        self.input_text = StarWarsDisplayTextEdit()
        self.input_text.setObjectName("starwars_console")
        self.input_text.setMinimumHeight(250)
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
        main_layout.addWidget(input_group, stretch=3)

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
        self.device_status_label.setObjectName("status_hud_scan")
        self.status_bar.addWidget(self.device_status_label)
        
        # self.status_bar.showMessage("就绪") # Remove this as requested
        
        self.apply_cinematic_effects()
        self.sync_console_palette()

    def ensure_default_geometry(self):
        target_w, target_h = 1280, 1100
        self.resize(target_w, target_h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'crt_overlay'):
            self.crt_overlay.resize(self.size())
            self.crt_overlay.raise_()

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)
        Config.set("theme", theme_name)
        
        # Update highlighter colors
        self.highlighter.set_theme(theme_name)

    def apply_theme(self, theme_name):
        self.setStyleSheet(get_stylesheet(theme_name))
        self.apply_cinematic_effects()
        self.sync_console_palette()

    def sync_console_palette(self):
        t = THEMES.get(self.current_theme, THEMES["Dracula (Official) - 德古拉(官方)"])
        self.input_text.set_hud_palette(QColor(t.CYAN))
        if hasattr(self, 'crt_overlay'):
            self.crt_overlay.set_color(QColor(t.CYAN))

    def apply_cinematic_effects(self):
        t = THEMES.get(self.current_theme, THEMES["Dracula (Official) - 德古拉(官方)"])
        pairs = [
            (self.btn_import, QColor(t.PINK), 42),
            (self.btn_create, QColor(t.PURPLE), 42),
            (self.input_text, QColor(t.CYAN), 28),
            (self.title_label, QColor(t.CYAN), 20),
        ]
        for widget, color, blur in pairs:
            glow = QGraphicsDropShadowEffect(self)
            color.setAlpha(145)
            glow.setColor(color)
            glow.setBlurRadius(blur)
            glow.setOffset(0, 0)
            widget.setGraphicsEffect(glow)

    def check_devices(self):
        p_src = Config.get_photo_src()
        v_src = Config.get_vr_src()
        
        p_ok = os.path.exists(str(p_src))
        v_ok = os.path.exists(str(v_src))
        
        # 提取设备名称逻辑
        def get_device_name(path_str):
            if not path_str or not os.path.exists(path_str):
                return ""
            
            drive_name = ""
            
            # 1. 尝试获取卷标
            if platform.system() == 'Windows':
                drive = os.path.splitdrive(path_str)[0]
                if drive:
                    try:
                        import win32api
                        vol_info = win32api.GetVolumeInformation(drive + "\\")
                        if vol_info[0]:
                            drive_name = vol_info[0]
                    except:
                        pass
                    if not drive_name:
                        drive_name = drive
            elif platform.system() == 'Darwin':
                if path_str.startswith('/Volumes/'):
                    parts = Path(path_str).parts
                    if len(parts) >= 3:
                        drive_name = parts[2]
            
            # 2. 如果卷标是 Untitled 或为空，尝试读取 EXIF
            is_generic = not drive_name or drive_name.lower() in ['untitled', 'no name', 'disk']
            
            if is_generic:
                try:
                    from PIL import Image
                    from PIL.ExifTags import TAGS
                    
                    # 扫描目录下前3个文件寻找图片
                    for root, dirs, files in os.walk(path_str):
                        for f in files:
                            if f.lower().endswith(('.jpg', '.jpeg', '.arw', '.dng')):
                                full_path = os.path.join(root, f)
                                try:
                                    img = Image.open(full_path)
                                    exif = img.getexif()
                                    if exif:
                                        for tag_id, value in exif.items():
                                            tag = TAGS.get(tag_id, tag_id)
                                            if tag == 'Model':
                                                # Clean up model string (remove null bytes, non-printable chars)
                                                raw_model = str(value).strip()
                                                clean_model = "".join(c for c in raw_model if c.isprintable())
                                                return f"[{clean_model}]"
                                except:
                                    continue
                        # 只扫描顶层或一层子目录，避免太慢
                        break
                except ImportError:
                    pass
            
            return f"[{drive_name}]" if drive_name else ""

        p_name = get_device_name(str(p_src))
        v_name = get_device_name(str(v_src))
        
        # Dual-line status format
        line1 = ""
        line2 = ""
        
        if p_ok:
            line1 = f"PHOTO {p_name} : ONLINE"
        else:
            line1 = "PHOTO : OFFLINE"
            
        if v_ok:
            line2 = f"VR {v_name} : ONLINE"
        else:
            line2 = "VR : OFFLINE"
            
        # If both are missing
        if not p_ok and not v_ok:
             self._device_state_text = "SYS-LINK NO DEVICE LINK"
             self.device_status_label.setObjectName("status_hud_err")
        else:
            self._device_state_text = f"SYS-LINK {line1}\nSYS-LINK {line2}"
            if p_ok and v_ok:
                self.device_status_label.setObjectName("status_hud_ok")
            else:
                self.device_status_label.setObjectName("status_hud_warn")
            
        self.render_device_status()
        self.device_status_label.style().unpolish(self.device_status_label)
        self.device_status_label.style().polish(self.device_status_label)

    def tick_hud(self):
        # Update less frequently or just for redundancy
        self.render_device_status()

    def render_device_status(self):
        # Format the text with color highlights
        text = self._device_state_text
        t = THEMES.get(self.current_theme, THEMES["Dracula (Official) - 德古拉(官方)"])
        
        # Replace status keywords with colored spans
        # ONLINE -> Green, OFFLINE -> Red, NO DEVICE -> Red
        
        # We need to split lines if it contains a newline
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line_html = line \
                .replace("ONLINE", f"<span style='color:{t.GREEN}; font-weight:bold'>ONLINE</span>") \
                .replace("OFFLINE", f"<span style='color:{t.RED}; font-weight:bold'>OFFLINE</span>") \
                .replace("NO DEVICE LINK", f"<span style='color:{t.RED}; font-weight:bold'>NO DEVICE LINK</span>") \
                .replace("SYS-LINK", f"<span style='color:{t.ORANGE}'>SYS-LINK</span>")
            formatted_lines.append(line_html)
            
        final_html = "<br>".join(formatted_lines)
        self.device_status_label.setText(final_html)

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
