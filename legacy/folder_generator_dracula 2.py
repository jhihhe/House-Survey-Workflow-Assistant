import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import platform
import time
from datetime import datetime
import errno


def hex_to_rgb(hex_val):
    hex_val = hex_val.lstrip('#')
    if len(hex_val) == 3:
        hex_val = ''.join([c*2 for c in hex_val])
    return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*map(int, rgb))

def interpolate_color(start_hex, end_hex, t):
    t = max(0.0, min(1.0, t))
    s = hex_to_rgb(start_hex)
    e = hex_to_rgb(end_hex)
    curr = tuple(s[i] + (e[i] - s[i]) * t for i in range(3))
    return rgb_to_hex(curr)


class UniversalFolderCreator:
    def __init__(self, master):
        self.master = master
        master.title("房堪文件夹批量生成工具 - Dracula Edition")
        master.geometry("900x640")
        master.minsize(820, 560)
        
        # 设置窗口背景色和透明度
        master.configure(bg='#282a36')
        master.attributes('-alpha', 0.95)  # 半透明效果

        # 检测操作系统 & 样式
        self.os_type = platform.system()
        self.set_style()

        # 界面布局
        self.create_widgets()

        # 初始化默认日期目录并预填展示
        self.initialize_default_dirs()

        # 事件绑定
        self.setup_events()

    def set_style(self):
        """配置跨平台样式 - Dracula Theme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用 clam 主题以获得更好的自定义支持

        # Dracula 配色方案
        self.colors = {
            'bg': '#282a36',           # 背景色
            'fg': '#f8f8f2',           # 前景色
            'selection': '#44475a',    # 选中/当前行/深色背景
            'comment': '#6272a4',      # 注释/灰色文字
            'cyan': '#8be9fd',
            'green': '#50fa7b',
            'orange': '#ffb86c',
            'pink': '#ff79c6',
            'purple': '#bd93f9',
            'red': '#ff5555',
            'yellow': '#f1fa8c'
        }

        # 字体配置
        if self.os_type == 'Windows':
            base_font = '微软雅黑'
        elif self.os_type == 'Darwin':
            base_font = 'Helvetica'
        else:
            base_font = 'Sans'

        self.fonts = {
            'body': (base_font, 11),
            'button': (base_font, 11, 'bold'),
            'header': (base_font, 20, 'bold'),
            'subheader': (base_font, 12),
        }

        # 配置全局样式
        self.style.configure('.', 
            background=self.colors['bg'], 
            foreground=self.colors['fg'],
            font=self.fonts['body']
        )
        
        self.style.configure('TFrame', background=self.colors['bg'])
        
        # 标签样式
        self.style.configure('TLabel', 
            background=self.colors['bg'], 
            foreground=self.colors['fg']
        )
        self.style.configure('Header.TLabel', 
            font=self.fonts['header'], 
            foreground=self.colors['pink'],
            background=self.colors['selection']  # Banner background
        )
        self.style.configure('Subheader.TLabel', 
            font=self.fonts['subheader'], 
            foreground=self.colors['cyan'],
            background=self.colors['selection']  # Banner background
        )
        self.style.configure('Info.TLabel',
            foreground=self.colors['comment']
        )

        # 容器样式
        self.style.configure('TLabelframe', 
            background=self.colors['bg'], 
            foreground=self.colors['green']
        )
        self.style.configure('TLabelframe.Label', 
            background=self.colors['bg'], 
            foreground=self.colors['green'],
            font=self.fonts['button']
        )

        # 按钮样式
        self.style.configure('TButton', 
            background=self.colors['selection'], 
            foreground=self.colors['fg'],
            borderwidth=0,
            focuscolor=self.colors['purple']
        )
        self.style.map('TButton',
            background=[('active', self.colors['comment']), ('pressed', self.colors['purple'])],
            foreground=[('active', self.colors['fg'])]
        )
        
        # 强调按钮
        self.style.configure('Accent.TButton', 
            background=self.colors['purple'], 
            foreground=self.colors['bg'],
            font=self.fonts['button']
        )
        self.style.map('Accent.TButton',
            background=[('active', self.colors['pink']), ('pressed', self.colors['cyan'])],
            foreground=[('active', self.colors['bg'])]
        )

        # 输入框样式
        self.style.configure('TEntry', 
            fieldbackground=self.colors['selection'],
            foreground=self.colors['fg'],
            insertcolor=self.colors['fg'],
            borderwidth=0
        )
        
        # 滚动条样式
        self.style.configure('Vertical.TScrollbar', 
            background=self.colors['selection'],
            troughcolor=self.colors['bg'],
            arrowcolor=self.colors['fg'],
            bordercolor=self.colors['bg']
        )
        self.style.configure('Horizontal.TScrollbar', 
            background=self.colors['selection'],
            troughcolor=self.colors['bg'],
            arrowcolor=self.colors['fg'],
            bordercolor=self.colors['bg']
        )
        
        # 进度条样式
        self.style.configure('Horizontal.TProgressbar',
            background=self.colors['green'],
            troughcolor=self.colors['selection'],
            bordercolor=self.colors['bg']
        )

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # 顶部横幅
        banner = tk.Frame(main_frame, bg=self.colors['selection']) # Banner bg
        banner.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            banner,
            text="📁 房堪文件夹批量生成",
            style='Header.TLabel'
        ).pack(side=tk.TOP, anchor='w', padx=12, pady=(10, 2))

        ttk.Label(
            banner,
            text="28一套 拼什么命啊",
            style='Subheader.TLabel'
        ).pack(side=tk.TOP, anchor='w', padx=12, pady=(0, 10))

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text=" 输入文件夹名称（每行一个）")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        # 文本输入框 (tk.Text needs manual coloring)
        self.text_input = tk.Text(
            input_frame,
            height=12,
            wrap=tk.NONE,
            font=self.fonts['body'],
            bg=self.colors['selection'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'], # Cursor color
            borderwidth=1,
            relief="solid",
            highlightthickness=0
        )

        # 滚动条
        scroll_y = ttk.Scrollbar(input_frame, command=self.text_input.yview)
        scroll_x = ttk.Scrollbar(input_frame, orient=tk.HORIZONTAL, command=self.text_input.xview)
        self.text_input.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.text_input.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        # 输入统计
        self.count_label = ttk.Label(input_frame, text="已输入：0 个文件夹", style='Info.TLabel')
        self.count_label.grid(row=2, column=0, sticky='w', padx=4, pady=(6, 2))

        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # 目录选择（展示为只读信息）
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(dir_frame, text="自动选择的日期目录：", font=self.fonts['body']).pack(side=tk.LEFT)

        self.dir_entry = ttk.Entry(dir_frame, font=self.fonts['body'])
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(dir_frame, text="浏览...", command=self.browse_directory, style='Accent.TButton').pack(side=tk.LEFT)

        # 操作按钮区域
        actions = ttk.Frame(main_frame)
        actions.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(actions, text="示例填充", command=self.fill_example).pack(side=tk.LEFT)
        ttk.Button(actions, text="清空", command=self.clear_input).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(actions, text="打开相片目录", command=self.open_photo_dir).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Button(actions, text="打开VR目录", command=self.open_vr_dir).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(actions, text="复制目录路径", command=self.copy_dir_paths).pack(side=tk.LEFT, padx=(12, 0))

        # 进度条区域 (包含两个独立进度条)
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(6, 0))

        # 相片进度
        self.progress_photo_label = ttk.Label(self.progress_frame, text="相片导入进度: 0%", font=('Helvetica', 9))
        self.progress_photo_label.pack(anchor='w')
        self.photo_runner_canvas = tk.Canvas(self.progress_frame, height=24, bg=self.colors['bg'], highlightthickness=0)
        self.photo_runner_canvas.pack(fill=tk.X)
        self.progress_photo = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_photo.pack(fill=tk.X, pady=(0, 4))

        # VR进度
        self.progress_vr_label = ttk.Label(self.progress_frame, text="VR 导入进度: 0%", font=('Helvetica', 9))
        self.progress_vr_label.pack(anchor='w')
        self.vr_runner_canvas = tk.Canvas(self.progress_frame, height=24, bg=self.colors['bg'], highlightthickness=0)
        self.vr_runner_canvas.pack(fill=tk.X)
        self.progress_vr = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_vr.pack(fill=tk.X)
        self.anim_disable = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.progress_frame, text="关闭导入动画", variable=self.anim_disable, command=self._toggle_anim).pack(anchor='w', pady=(4, 0))

        # 底部按钮区域 (Import & Create)
        bottom_actions = ttk.Frame(main_frame)
        bottom_actions.pack(fill=tk.X, pady=(6, 0))
        
        # 导卡按钮 (左侧)
        ttk.Button(bottom_actions, text="📥 一键导卡 (移动原片)", command=self.import_originals, style='Accent.TButton').pack(side=tk.LEFT)

        # 创建按钮 (右侧)
        ttk.Button(bottom_actions, text="开始创建文件夹", command=self.create_folders, style='Accent.TButton').pack(side=tk.RIGHT)

        # 状态栏
        self.status_bar = tk.Label(
            self.master,
            text="就绪",
            relief=tk.FLAT,
            anchor=tk.W,
            font=self.fonts['body'],
            bg=self.colors['selection'],
            fg=self.colors['fg'],
            padx=5,
            pady=2
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_events(self):
        # 文本输入实时统计
        self.text_input.bind('<<Modified>>', self.on_text_modified)

    def on_text_modified(self, event=None):
        if self.text_input.edit_modified():
            text = self.text_input.get("1.0", tk.END)
            folder_names = [line.strip() for line in text.splitlines() if line.strip()]
            count = len(folder_names)
            self.count_label.config(text=f"已输入：{count} 个文件夹")
            self.text_input.edit_modified(False)

            # 状态栏变色：数量越多越紫 (Dracula版)
            # 寓意：紫气东来
            max_count = 50
            ratio = min(count / max_count, 1.0)
            
            # 从默认背景色 (selection #44475a) 渐变到紫色 (purple #bd93f9)
            start_color = self.colors['selection']
            end_color = self.colors['purple']
            
            bg_color = interpolate_color(start_color, end_color, ratio)
            
            # 如果背景色太亮，可能需要调整字体颜色为黑色，保持对比度
            # 但 Dracula purple (#bd93f9) 上白色文字 (#f8f8f2) 也是可读的，
            # 不过为了更好看，如果接近全紫，可以考虑把文字变深一点？
            # 简单起见，保持白色文字即可，或者稍微变暗一点背景。
            # 这里只改变背景色。
            self.status_bar.config(bg=bg_color)

    def get_date_based_dirs(self):
        """返回基于今天日期的两个目标目录路径（相片：MMDD贺志；VR：MMDD）"""
        today = datetime.today()
        year = today.strftime('%Y')
        month_label = f"{today.month:02d}月"  # MM月
        photo_day_label = f"{today.month:02d}{today.day:02d}贺志"  # 相片使用 MMDD贺志
        vr_day_label = f"{today.month:02d}{today.day:02d}"          # VR 使用 MMDD

        base_photo = os.path.join("/Users/mac/Pictures/工作", f"{year}相片", month_label, photo_day_label)
        base_vr = os.path.join("/Users/mac/Pictures/工作", f"{year}VR", month_label, vr_day_label)

        return [base_photo, base_vr]

    def get_base_root(self):
        """优先使用用户通过“浏览...”选择的路径作为根目录，否则回退到默认 '/Users/mac/Pictures/工作'"""
        p = self.dir_entry.get().strip()
        if p and os.path.isabs(p):
            try:
                # 期望格式：.../{Year}相片/{Month}月/{MMDD...}
                # 向上回退三级，得到根路径（例如 /Users/mac/Pictures/工作）
                root = os.path.dirname(os.path.dirname(os.path.dirname(p)))
                if os.path.exists(root):
                    return root
            except Exception:
                pass
        return "/Users/mac/Pictures/工作"

    def initialize_default_dirs(self):
        """预填默认日期目录并创建缺失层级"""
        target_dirs = self.get_date_based_dirs()
        # 自动创建年/月/日目录层级
        for d in target_dirs:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError:
                pass # Fail silently if permission denied, user might change path

        # 在输入框预填第一个目录，仅用于展示
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, target_dirs[0])

        # 状态栏展示两个目录
        self.status_bar.config(text=f"自动日期目录：1) {target_dirs[0]}  2) {target_dirs[1]}")

    def browse_directory(self):
        """选择输出目录（可选）"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.status_bar.config(text=f"当前目录（手动选择）：{directory}")

    def open_dir(self, path: str):
        try:
            if self.os_type == 'Windows':
                os.startfile(path)
            elif self.os_type == 'Darwin':
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showwarning("打开失败", f"无法打开目录：{path}\n错误：{e}")

    def open_photo_dir(self):
        self.open_dir(self.get_date_based_dirs()[0])

    def open_vr_dir(self):
        self.open_dir(self.get_date_based_dirs()[1])

    def copy_dir_paths(self):
        dirs = self.get_date_based_dirs()
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append("\n".join(dirs))
            self.status_bar.config(text="目录路径已复制到剪贴板")
        except Exception as e:
            messagebox.showwarning("复制失败", f"复制失败：{e}")

    def fill_example(self):
        examples = [
            "1.郭艳 HS251217836041 湘雅附一店 天健壹平方英里 A-2311 北",
            "2.龙苗 HS251216879300 芙蓉盛世店 新力紫园 4-1707 北",
            "3.王检元 HS251216976198 湘雅附一店 新时代广场 南栋-1822 北",
            "4.余秀珍 HS250304529130 昆玉国际店 景园小区 1-406 南",
        ]
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", "\n".join(examples))
        self.on_text_modified()

    def clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.on_text_modified()
        self.status_bar.config(text="已清空输入")

    def import_originals(self):
        """一键移动原片到指定日期目录 (多线程版)"""
        # 启动后台线程，避免阻塞 UI
        threading.Thread(target=self._run_import_task, daemon=True).start()

    def _run_import_task(self):
        # 1. 目标路径计算
        today = datetime.today()
        year = today.strftime('%Y')
        month_label = f"{today.month:02d}月"
        day_folder_name = f"{today.month:02d}{today.day:02d}原片"
        base_root = self.get_base_root()
        
        target_photo = os.path.join(base_root, f"{year}相片", month_label, day_folder_name)
        target_vr = os.path.join(base_root, f"{year}VR", month_label, day_folder_name)
        
        # 2. 源路径定义
        source_photo = "/Volumes/Untitled/DCIM/100SIGMA"
        source_vr = "/Volumes/Osmo360/DCIM/CAM_001"
        
        tasks = [
            {
                "src": source_photo, 
                "dst": target_photo, 
                "label": "相片 (Sigma)",
                "kind": "photo",
                "bar": self.progress_photo,
                "label_widget": self.progress_photo_label,
                "label_prefix": "相片导入进度",
                "runner_canvas": self.photo_runner_canvas
            },
            {
                "src": source_vr, 
                "dst": target_vr, 
                "label": "VR (Osmo)",
                "kind": "vr",
                "bar": self.progress_vr,
                "label_widget": self.progress_vr_label,
                "label_prefix": "VR 导入进度",
                "runner_canvas": self.vr_runner_canvas
            }
        ]
        
        # 3. 并行执行移动
        # 用于存储每个任务的结果
        results = [None] * len(tasks)
        threads = []

        # 更新状态栏
        self.master.after(0, lambda: self.status_bar.config(text="正在扫描存储卡..."))
        
        for i, task in enumerate(tasks):
            t = threading.Thread(target=self._process_single_task, args=(task, results, i))
            threads.append(t)
            t.start()
        
        # 等待所有任务完成
        for t in threads:
            t.join()
        
        # 4. 汇总结果（按任务标签区分）
        all_logs = []
        all_errors = []
        total_moved = 0
        photo_moved = 0
        vr_moved = 0
        photo_delete_fail = 0
        vr_delete_fail = 0
        
        for res in results:
            if res:
                r_logs, r_errors, r_moved, r_label, r_delete_fail, r_kind = res
                all_logs.extend(r_logs)
                all_errors.extend(r_errors)
                total_moved += r_moved
                if r_kind == "photo":
                    photo_moved += r_moved
                    photo_delete_fail += r_delete_fail
                elif r_kind == "vr":
                    vr_moved += r_moved
                    vr_delete_fail += r_delete_fail
        
        # 结果摘要（纯状态栏，仅提示完成）
        summary_msg = "导卡完成"
        
        # 状态栏输出
        self.master.after(0, self._show_import_result, all_logs, all_errors, total_moved, summary_msg)

    def _process_single_task(self, task, results, index):
        src_dir = task["src"]
        dst_dir = task["dst"]
        label = task["label"]
        pbar = task["bar"]
        plabel = task["label_widget"]
        prefix = task["label_prefix"]
        kind = task.get("kind", "photo")
        runner_canvas = task.get("runner_canvas")
        
        logs = []
        errors = []
        moved_count = 0
        delete_fail_count = 0
        permission_issue_reported = False
        
        # 重置进度条
        self.master.after(0, lambda p=pbar, l=plabel, pre=prefix: [p.configure(value=0), l.config(text=f"{pre}: 等待中...")])
        if runner_canvas and not self.anim_disable.get():
            self.master.after(0, self._runner_reset, runner_canvas)
        
        if not os.path.exists(src_dir):
            logs.append(f"⚠️ {label}: 源目录不存在 (未插入存储卡?)")
            self.master.after(0, lambda l=plabel, pre=prefix: l.config(text=f"{pre}: 未检测到设备"))
            results[index] = (logs, errors, moved_count, label, delete_fail_count, kind)
            return
            
        try:
            # 确保目标目录存在
            os.makedirs(dst_dir, exist_ok=True)
            
            # 获取源文件列表
            files = [f for f in os.listdir(src_dir) if not f.startswith('.')] # 忽略隐藏文件
            if not files:
                logs.append(f"ℹ️ {label}: 源目录为空")
                self.master.after(0, lambda l=plabel, pre=prefix: l.config(text=f"{pre}: 无文件"))
                results[index] = (logs, errors, moved_count, label, delete_fail_count, kind)
                return
            
            logs.append(f"🚀 开始移动 {label}...")
            
            # 更新进度条最大值
            total_files = len(files)
            self.master.after(0, lambda p=pbar, t=total_files: p.configure(maximum=t))
            
            # 速度统计相关变量（累计统计）
            total_bytes_transferred = 0
            
            for idx, filename in enumerate(files):
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)
                
                speed_str = "0.0 MB/s"
                if os.path.isfile(src_file):
                    try:
                        # 获取文件大小
                        file_size = os.path.getsize(src_file)
                        # 处理重名冲突：如果目标已存在，生成不冲突的新文件名
                        if os.path.exists(dst_file):
                            base, ext = os.path.splitext(filename)
                            counter = 1
                            new_name = f"{base}_{counter}{ext}"
                            new_dst = os.path.join(dst_dir, new_name)
                            while os.path.exists(new_dst) and counter < 1000:
                                counter += 1
                                new_name = f"{base}_{counter}{ext}"
                                new_dst = os.path.join(dst_dir, new_name)
                            dst_file = new_dst
                        # 判断是否同设备（同盘重命名 vs 跨盘复制）
                        same_device = False
                        try:
                            same_device = (os.stat(src_dir).st_dev == os.stat(dst_dir).st_dev)
                        except Exception:
                            same_device = False
                        if kind == "photo":
                            shutil.copy2(src_file, dst_file)
                            moved_count += 1
                            speed_str = ""
                        else:
                            # VR 保持移动语义：同盘 move，跨盘复制后删除源文件
                            if same_device:
                                shutil.move(src_file, dst_file)
                                moved_count += 1
                                speed_str = "0.0 MB/s"
                            else:
                                t0 = time.perf_counter()
                                shutil.copy2(src_file, dst_file)
                                dt = time.perf_counter() - t0
                                moved_count += 1
                                total_bytes_transferred += file_size
                                speed_mbps = (file_size / (1024 * 1024)) / dt if dt > 0 else 0.0
                                speed_str = f"{speed_mbps:.1f} MB/s"
                                try:
                                    os.remove(src_file)
                                except Exception:
                                    delete_fail_count += 1
                                    errors.append(f"{label}: {filename} 已复制，但原卡文件未删除（可能写保护或权限拦截）")
                    except Exception as e:
                        if isinstance(e, PermissionError) or getattr(e, "errno", None) in (errno.EPERM, errno.EACCES, 1, 13):
                            if not permission_issue_reported:
                                errors.append("检测到目标目录写入权限不足 (macOS 隐私拦截)。可通过 系统设置→隐私与安全性→完全磁盘访问 解决，或点击“浏览...”选择其他可写目录。")
                                permission_issue_reported = True
                            self.master.after(0, lambda l=plabel: l.config(text=f"{prefix}: 权限不足"))
                        else:
                            errors.append(f"{filename}: {str(e)}")
                
                # 更新进度
                current_val = idx + 1
                self.master.after(0, self._update_progress_ui, pbar, plabel, prefix, current_val, total_files, speed_str, kind != "photo")
                if runner_canvas and not self.anim_disable.get():
                    self.master.after(0, self._runner_update, runner_canvas, current_val, total_files)
            
            logs.append(f"✅ {label}: 成功移动文件到 {dst_dir}")
            # 强制更新为完成状态
            self.master.after(0, lambda l=plabel, pre=prefix: l.config(text=f"{pre}: 完成"))
            if runner_canvas and not self.anim_disable.get():
                self.master.after(0, self._runner_complete, runner_canvas)
            
        except Exception as e:
            errors.append(f"{label} 致命错误: {str(e)}")
            self.master.after(0, lambda l=plabel, pre=prefix: l.config(text=f"{pre}: 错误"))
            
        results[index] = (logs, errors, moved_count, label, delete_fail_count, kind)

    def _update_progress_ui(self, pbar, plabel, prefix, current, total, speed="", show_speed=True):
        percent = int((current / total) * 100)
        pbar['value'] = current
        speed_text = f" - {speed}" if (show_speed and speed) else ""
        plabel.config(text=f"{prefix}: {percent}% ({current}/{total}){speed_text}")
    
    def _runner_reset(self, canvas):
        w = canvas.winfo_width() or 1
        h = canvas.winfo_height() or 24
        items = getattr(canvas, "cat_items", [])
        for i in items:
            canvas.delete(i)
        canvas.cat_items = []
        base_y = h//2 - 10
        body = canvas.create_rectangle(10, base_y+6, 30, base_y+18, fill=self.colors['pink'], outline="")
        head = canvas.create_oval(30, base_y+6, 42, base_y+18, fill=self.colors['pink'], outline="")
        ear1 = canvas.create_polygon(34, base_y+6, 36, base_y+0, 38, base_y+6, fill=self.colors['pink'], outline="")
        ear2 = canvas.create_polygon(39, base_y+6, 41, base_y+0, 43, base_y+6, fill=self.colors['pink'], outline="")
        eye1 = canvas.create_oval(33, base_y+10, 35, base_y+12, fill=self.colors['bg'], outline="")
        eye2 = canvas.create_oval(36, base_y+10, 38, base_y+12, fill=self.colors['bg'], outline="")
        whisker1 = canvas.create_line(42, base_y+12, 44, base_y+12, fill=self.colors['pink'])
        whisker2 = canvas.create_line(42, base_y+14, 44, base_y+15, fill=self.colors['pink'])
        leg1 = canvas.create_rectangle(14, base_y+18, 18, base_y+22, fill=self.colors['pink'], outline="")
        leg2 = canvas.create_rectangle(22, base_y+18, 26, base_y+22, fill=self.colors['pink'], outline="")
        leg3 = canvas.create_rectangle(14, base_y+18, 18, base_y+22, fill=self.colors['pink'], outline="")
        leg4 = canvas.create_rectangle(22, base_y+18, 26, base_y+22, fill=self.colors['pink'], outline="")
        tail = canvas.create_polygon(10, base_y+14, 2, base_y+12, 5, base_y+16, fill=self.colors['pink'], outline="")
        canvas.cat_items = [body, head, ear1, ear2, eye1, eye2, whisker1, whisker2, leg1, leg2, leg3, leg4, tail]
        for i in canvas.cat_items:
            canvas.addtag_withtag("cat", i)
        canvas.cat_prev_x = 0
        canvas.cat_prev_y = 0
        canvas.cat_phase = 0
        canvas.cat_running = True
        self._runner_set_pos(canvas, 0, 0)
        self._runner_start(canvas)
    
    def _runner_update(self, canvas, current, total):
        if self.anim_disable.get() or total <= 0 or not getattr(canvas, "cat_items", None):
            return
        w = canvas.winfo_width() or 1
        h = canvas.winfo_height() or 24
        frac = max(0.0, min(1.0, current / total))
        x = int(frac * (w - 60))
        y = 0
        self._runner_set_pos(canvas, x, y)
        if not getattr(canvas, "cat_running", False):
            return
    
    def _runner_complete(self, canvas):
        if self.anim_disable.get() or not getattr(canvas, "cat_items", None):
            return
        canvas.cat_running = False
        if getattr(canvas, "cat_anim_id", None):
            try:
                canvas.after_cancel(canvas.cat_anim_id)
            except Exception:
                pass
        cx = canvas.cat_prev_x
        cy = canvas.cat_prev_y
        steps = 24
        radius = 6
        def step(i=0):
            if i <= steps:
                x = cx + int(radius * 0.8 * (i/steps))
                y = cy
                self._runner_set_pos(canvas, x, y)
                canvas.after(60, step, i+1)
            else:
                for it in canvas.cat_items:
                    canvas.itemconfigure(it, state="hidden")
        step()

    def _runner_start(self, canvas):
        def tick():
            if self.anim_disable.get() or not getattr(canvas, "cat_running", False):
                return
            self._runner_anim_step(canvas)
            canvas.cat_anim_id = canvas.after(120, tick)
        canvas.cat_anim_id = canvas.after(120, tick)

    def _runner_anim_step(self, canvas):
        if not getattr(canvas, "cat_items", None):
            return
        body = canvas.cat_items[0]
        head = canvas.cat_items[1]
        legs = canvas.cat_items[8:12]
        tail = canvas.cat_items[12]
        amp = 4
        if canvas.cat_phase == 0:
            for i, leg in enumerate(legs):
                canvas.move(leg, 0, -amp if i % 2 == 0 else amp)
            x1, y1, x2, y2, x3, y3 = canvas.coords(tail)
            canvas.coords(tail, x1, y1-2, x2, y2-2, x3, y3-2)
            canvas.move(body, 0, -1)
            canvas.move(head, 0, -1)
            canvas.cat_phase = 1
        else:
            for i, leg in enumerate(legs):
                canvas.move(leg, 0, amp if i % 2 == 0 else -amp)
            x1, y1, x2, y2, x3, y3 = canvas.coords(tail)
            canvas.coords(tail, x1, y1+2, x2, y2+2, x3, y3+2)
            canvas.move(body, 0, 1)
            canvas.move(head, 0, 1)
            canvas.cat_phase = 0
    def _runner_set_pos(self, canvas, x, y):
        dx = x - getattr(canvas, "cat_prev_x", 0)
        dy = y - getattr(canvas, "cat_prev_y", 0)
        canvas.move("cat", dx, dy)
        canvas.cat_prev_x = x
        canvas.cat_prev_y = y

    def _toggle_anim(self):
        if self.anim_disable.get():
            try:
                self.photo_runner_canvas.pack_forget()
                self.vr_runner_canvas.pack_forget()
            except Exception:
                pass
        else:
            try:
                self.photo_runner_canvas.pack(fill=tk.X, before=self.progress_photo)
                self.vr_runner_canvas.pack(fill=tk.X, before=self.progress_vr)
            except Exception:
                pass

    def _show_import_result(self, logs, errors, moved_count, summary=None):
        # 强制刷新 UI，确保进度条已显示 100% / 完成
        self.master.update_idletasks()
        if not summary:
            delete_photo_issue = any(("未删除" in e and "相片" in e) for e in errors)
            if delete_photo_issue and moved_count > 0:
                summary = f"导卡完成 成功 {moved_count} 文件 未删除相片源文件"
            else:
                summary = f"导卡完成 - 成功 {moved_count} 文件"
                if errors:
                    summary += f"，提示 {len(errors)} 条"
                else:
                    summary += "，无提示"
        self.status_bar.config(text=summary)

    def create_folders(self):
        """创建文件夹核心逻辑：在两个日期目录中分别创建"""
        # 每次点击时按当天日期重新计算两个目标目录
        target_dirs = self.get_date_based_dirs()
        for d in target_dirs:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError as e:
                messagebox.showerror("错误", f"无法创建目录 {d}: {e}")
                return

        input_text = self.text_input.get("1.0", tk.END)
        folder_names = [line.strip() for line in input_text.splitlines() if line.strip()]

        if not folder_names:
            messagebox.showerror("错误", "请输入至少一个文件夹名称")
            return

        total_steps = len(folder_names) * len(target_dirs)
        
        # 使用相片进度条作为总进度条 (因为移除了旧的单进度条)
        # 这里为了兼容，我们临时征用相片进度条显示创建进度
        self.progress_photo_label.config(text="文件夹创建进度:")
        self.progress_photo.configure(maximum=total_steps)
        self.progress_photo['value'] = 0
        
        # 隐藏 VR 进度条避免困惑
        # 或者也可以两个都用？这里简单起见只用上面那个
        self.progress_vr['value'] = 0
        self.progress_vr_label.config(text="")

        success_by_dir = {target_dirs[0]: 0, target_dirs[1]: 0}
        errors = []
        for name in folder_names:
            # 替换非法字符（跨平台安全）
            valid_name = name.replace('/', '／').replace('\\', '＼')
            for base in target_dirs:
                try:
                    full_path = os.path.join(base, valid_name)
                    os.makedirs(full_path, exist_ok=False)
                    success_by_dir[base] += 1
                except FileExistsError:
                    errors.append(f"{base} 中 '{name}' 已存在")
                except OSError as e:
                    errors.append(f"{base} 中 '{name}' 创建失败: {e.strerror}")
                except Exception as e:
                    errors.append(f"{base} 中 '{name}' 发生未知错误: {str(e)}")
                finally:
                    self.progress_photo.step(1)
                    self.master.update_idletasks()

        # 显示结果
        total_created_photo = success_by_dir[target_dirs[0]]
        total_created_vr = success_by_dir[target_dirs[1]]
        total_items = len(folder_names)
        shoots = total_created_photo  # 保留原始统计依据：相片成功数
        revenue = shoots * 28
        if total_created_photo or total_created_vr:
            success_msg = (
                "文件夹创建成功\n\n"
                f"日期目录：\n1) {target_dirs[0]}\n2) {target_dirs[1]}\n\n"
                f"创建结果：相片目录 {total_created_photo}/{total_items}，VR目录 {total_created_vr}/{total_items}\n\n"
                f"您今日拍摄{shoots}套房堪\n\n🎉恭喜收米 ¥{revenue}！🎉"
            )
            messagebox.showinfo("操作成功", success_msg)

        if errors:
            error_msg = "以下问题需要注意：\n\n" + "\n".join(errors)
            messagebox.showwarning("操作完成", error_msg)

        self.status_bar.config(text=(
            f"操作完成 - 相片成功{total_created_photo}个，VR成功{total_created_vr}个，失败{len(errors)}条；今日拍摄{shoots}套，¥{revenue}"
        ))
        
        # 恢复标签
        self.progress_photo_label.config(text="相片导入进度: 0%")
        self.progress_vr_label.config(text="VR 导入进度: 0%")


if __name__ == "__main__":
    root = tk.Tk()

    # 高DPI适配
    if platform.system() == 'Windows':
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    elif platform.system() == 'Darwin':
        root.tk.call('tk', 'scaling', 2.0)

    app = UniversalFolderCreator(root)
    root.mainloop()
