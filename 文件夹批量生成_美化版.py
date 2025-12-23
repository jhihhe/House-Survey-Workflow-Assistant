import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import platform
from datetime import datetime


class UniversalFolderCreator:
    def __init__(self, master):
        self.master = master
        master.title("房堪文件夹批量生成工具 · 美化版")
        master.geometry("900x640")
        master.minsize(820, 560)

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
        """配置跨平台样式"""
        self.style = ttk.Style()

        # 统一颜色配置
        self.colors = {
            'text_primary': '#000000',
            'text_muted': '#666666',
            'bg_primary': '#FFFFFF',
            'banner_bg': '#F5FAFF',
            'accent_win': '#0078D7',
            'accent_mac': '#007AFF',
            'danger': '#D7263D',
        }

        # 根据系统设置主题与字体
        if self.os_type == 'Windows':
            self.style.theme_use('vista')
            self.fonts = {
                'body': ('微软雅黑', 10),
                'button': ('微软雅黑', 10, 'bold'),
                'header': ('微软雅黑', 18, 'bold'),
                'subheader': ('微软雅黑', 11),
            }
            self.accent = self.colors['accent_win']
        elif self.os_type == 'Darwin':  # macOS
            self.style.theme_use('aqua')
            self.fonts = {
                'body': ('Helvetica', 12),
                'button': ('Helvetica', 12, 'bold'),
                'header': ('Helvetica', 20, 'bold'),
                'subheader': ('Helvetica', 12),
            }
            self.accent = self.colors['accent_mac']
        else:  # Linux
            self.style.theme_use('clam')
            self.fonts = {
                'body': ('Sans', 10),
                'button': ('Sans', 10, 'bold'),
                'header': ('Sans', 18, 'bold'),
                'subheader': ('Sans', 11),
            }
            self.accent = self.colors['accent_win']

        # 强制设置文本颜色
        self.style.configure('TEntry', foreground=self.colors['text_primary'])
        self.style.configure('TText', foreground=self.colors['text_primary'])

        # 自定义样式：标题、次标题、按钮等
        self.style.configure('Header.TLabel', foreground=self.colors['text_primary'], font=self.fonts['header'])
        self.style.configure('Subheader.TLabel', foreground=self.colors['text_muted'], font=self.fonts['subheader'])
        self.style.configure('Accent.TButton', foreground='#ffffff')
        self.style.map('Accent.TButton', background=[('!disabled', self.accent)])

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # 顶部横幅
        banner = tk.Frame(main_frame, bg=self.colors['banner_bg'])
        banner.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            banner,
            text="📁 房堪文件夹批量生成",
            font=self.fonts['header'],
            bg=self.colors['banner_bg'],
            fg=self.colors['text_primary']
        ).pack(side=tk.TOP, anchor='w', padx=12, pady=(10, 2))

        tk.Label(
            banner,
            text="更清晰的布局，更便捷的操作",
            font=self.fonts['subheader'],
            bg=self.colors['banner_bg'],
            fg=self.colors['text_muted']
        ).pack(side=tk.TOP, anchor='w', padx=12, pady=(0, 10))

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text=" 输入文件夹名称（每行一个）")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        # 文本输入框
        self.text_input = tk.Text(
            input_frame,
            height=12,
            wrap=tk.NONE,
            font=self.fonts['body'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            borderwidth=1,
            relief="solid"
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
        self.count_label = ttk.Label(input_frame, text="已输入：0 个文件夹", style='Subheader.TLabel')
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

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(6, 0))

        # 创建按钮
        create_wrap = ttk.Frame(main_frame)
        create_wrap.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(create_wrap, text="开始创建", command=self.create_folders, style='Accent.TButton').pack(side=tk.RIGHT)

        # 状态栏
        self.status_bar = ttk.Label(
            self.master,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.fonts['body']
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_events(self):
        # 文本输入实时统计
        self.text_input.bind('<<Modified>>', self.on_text_modified)

    def on_text_modified(self, event=None):
        if self.text_input.edit_modified():
            text = self.text_input.get("1.0", tk.END)
            folder_names = [line.strip() for line in text.splitlines() if line.strip()]
            self.count_label.config(text=f"已输入：{len(folder_names)} 个文件夹")
            self.text_input.edit_modified(False)

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

    def initialize_default_dirs(self):
        """预填默认日期目录并创建缺失层级"""
        target_dirs = self.get_date_based_dirs()
        # 自动创建年/月/日目录层级
        for d in target_dirs:
            os.makedirs(d, exist_ok=True)

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
            "阳光花园1栋101",
            "阳光花园1栋102",
            "蔚蓝小区3栋708",
            "星河湾二期5栋1201",
        ]
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", "\n".join(examples))
        self.on_text_modified()

    def clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.on_text_modified()
        self.status_bar.config(text="已清空输入")

    def create_folders(self):
        """创建文件夹核心逻辑：在两个日期目录中分别创建"""
        # 每次点击时按当天日期重新计算两个目标目录
        target_dirs = self.get_date_based_dirs()
        for d in target_dirs:
            os.makedirs(d, exist_ok=True)

        input_text = self.text_input.get("1.0", tk.END)
        folder_names = [line.strip() for line in input_text.splitlines() if line.strip()]

        if not folder_names:
            messagebox.showerror("错误", "请输入至少一个文件夹名称")
            return

        total_steps = len(folder_names) * len(target_dirs)
        self.progress.configure(maximum=total_steps)
        self.progress['value'] = 0

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
                    self.progress.step(1)
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


if __name__ == "__main__":
    root = tk.Tk()

    # 高DPI适配
    if platform.system() == 'Windows':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    elif platform.system() == 'Darwin':
        root.tk.call('tk', 'scaling', 2.0)

    app = UniversalFolderCreator(root)
    root.mainloop()