import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import platform
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from ..utils.config import Config
from ..utils.colors import interpolate_color
from ..utils.fs_utils import get_date_based_dirs
from ..services.import_service import ImportTask
from ..services.folder_service import FolderService
from .widgets import CatRunner

class UniversalFolderCreator:
    def __init__(self, master):
        self.master = master
        self._setup_window()
        self.os_type = platform.system()
        self._set_style()
        self._create_widgets()
        self._initialize_state()
        self._setup_events()

    def _setup_window(self):
        self.master.title("房堪文件夹批量生成工具 - Dracula Edition")
        self.master.geometry("900x700")
        self.master.minsize(820, 560)
        self.master.configure(bg=Config.COLORS['bg'])
        self.master.attributes('-alpha', 0.95)

    def _set_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.colors = Config.COLORS
        self.fonts = Config.get_fonts()
        
        self.style.configure('.', background=self.colors['bg'], foreground=self.colors['fg'], font=self.fonts['body'])
        self.style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        self.style.configure('TButton', padding=6, relief="flat", background=self.colors['selection'])
        self.style.map('TButton', background=[('active', self.colors['comment'])], foreground=[('active', self.colors['fg'])])
        self.style.configure('Accent.TButton', background=self.colors['purple'], foreground=self.colors['bg'], font=self.fonts['button'])
        self.style.map('Accent.TButton', background=[('active', self.colors['pink'])], foreground=[('active', self.colors['bg'])])
        self.style.configure('Header.TLabel', font=self.fonts['header'], foreground=self.colors['pink'])
        self.style.configure('Subheader.TLabel', font=self.fonts['subheader'], foreground=self.colors['purple'])
        self.style.configure('Info.TLabel', foreground=self.colors['cyan'])
        self.style.configure('TLabelframe', background=self.colors['bg'], bordercolor=self.colors['comment'])
        self.style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['orange'])
        self.style.configure('TEntry', fieldbackground=self.colors['selection'], foreground=self.colors['fg'], insertcolor=self.colors['fg'])
        self.style.configure("Horizontal.TProgressbar", troughcolor=self.colors['selection'], bordercolor=self.colors['bg'], background=self.colors['green'], thickness=10)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="为房产摄影 / 房堪工作流量身定制的桌面自动化工具", style='Header.TLabel').pack(side=tk.TOP, anchor='w', padx=12, pady=(10, 2))
        ttk.Label(header_frame, text="28一套 拼什么命啊", style='Subheader.TLabel').pack(side=tk.TOP, anchor='w', padx=12, pady=(0, 10))
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # Input
        input_frame = ttk.LabelFrame(main_frame, text=" 输入文件夹名称（每行一个）")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        
        self.text_input = tk.Text(input_frame, height=12, wrap=tk.NONE, font=self.fonts['code'], bg=self.colors['selection'], fg=self.colors['fg'], insertbackground=self.colors['fg'], borderwidth=1, relief="solid", highlightthickness=0)
        # Configure tags for syntax highlighting
        self.text_input.tag_configure("index", foreground=self.colors['orange'])
        self.text_input.tag_configure("code", foreground=self.colors['purple'])
        self.text_input.tag_configure("shop", foreground=self.colors['green'])
        self.text_input.tag_configure("direction", foreground=self.colors['red'])
        self.text_input.tag_configure("room", foreground=self.colors['cyan'])
        
        scroll_y = ttk.Scrollbar(input_frame, command=self.text_input.yview)
        scroll_x = ttk.Scrollbar(input_frame, orient=tk.HORIZONTAL, command=self.text_input.xview)
        self.text_input.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.text_input.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.count_label = ttk.Label(input_frame, text="已输入：0 个文件夹", style='Info.TLabel')
        self.count_label.grid(row=2, column=0, sticky='w', padx=4, pady=(6, 2))

        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(dir_frame, text="自动选择的日期目录：", font=self.fonts['body']).pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, font=self.fonts['body'])
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="浏览...", command=self.browse_directory, style='Accent.TButton').pack(side=tk.LEFT)

        actions = ttk.Frame(main_frame)
        actions.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(actions, text="示例填充", command=self.fill_example).pack(side=tk.LEFT)
        ttk.Button(actions, text="清空", command=self.clear_input).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(actions, text="打开相片目录", command=self.open_photo_dir).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Button(actions, text="打开VR目录", command=self.open_vr_dir).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(actions, text="复制目录路径", command=self.copy_dir_paths).pack(side=tk.LEFT, padx=(12, 0))

        # Progress
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(6, 0))
        
        # Photo Progress
        self.progress_photo_label = ttk.Label(self.progress_frame, text="相片导入进度: 0%", font=('Helvetica', 9))
        self.progress_photo_label.pack(anchor='w')
        self.photo_runner_canvas = CatRunner(self.progress_frame, height=24, bg=self.colors['bg'], highlightthickness=0)
        self.photo_runner_canvas.pack(fill=tk.X)
        self.progress_photo = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_photo.pack(fill=tk.X, pady=(0, 4))
        
        # VR Progress
        self.progress_vr_label = ttk.Label(self.progress_frame, text="VR 导入进度: 0%", font=('Helvetica', 9))
        self.progress_vr_label.pack(anchor='w')
        self.vr_runner_canvas = CatRunner(self.progress_frame, height=24, bg=self.colors['bg'], highlightthickness=0)
        self.vr_runner_canvas.pack(fill=tk.X)
        self.progress_vr = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_vr.pack(fill=tk.X)
        
        self.anim_disable = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.progress_frame, text="关闭导入动画", variable=self.anim_disable, command=self._toggle_anim).pack(anchor='w', pady=(4, 0))

        # Bottom Actions
        bottom_actions = ttk.Frame(main_frame)
        bottom_actions.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(bottom_actions, text="📥 一键导卡 (移动原片)", command=self.import_originals, style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(bottom_actions, text="开始创建文件夹", command=self.create_folders, style='Accent.TButton').pack(side=tk.RIGHT)

        # Status Bar
        self.status_bar = ttk.Label(self.master, text="就绪", relief=tk.SUNKEN, anchor=tk.W, background=self.colors['selection'], foreground=self.colors['fg'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _initialize_state(self):
        dirs = get_date_based_dirs()
        self.dir_entry.insert(0, dirs[0])
        self._modified_after_id = None
        self.paths = Config.PATHS

    def _setup_events(self):
        self.text_input.bind('<<Modified>>', self.on_text_modified)
        self.text_input.bind('<KeyRelease>', self.on_text_modified)

    def on_text_modified(self, event=None):
        if self._modified_after_id:
            self.master.after_cancel(self._modified_after_id)
        self._modified_after_id = self.master.after(100, self._process_modified)

    def _highlight_syntax(self):
        # Clear existing tags
        for tag in ["index", "code", "shop", "direction", "room"]:
            self.text_input.tag_remove(tag, "1.0", tk.END)
            
        content = self.text_input.get("1.0", tk.END)
        lines = content.splitlines()
        
        import re
        
        for i, line in enumerate(lines):
            line_num = i + 1
            if not line.strip():
                continue
                
            # Index: start with number + dot (e.g., "1.")
            for m in re.finditer(r'^\s*(\d+\.)', line):
                self.text_input.tag_add("index", f"{line_num}.{m.start(1)}", f"{line_num}.{m.end(1)}")
                
            # Code: HS followed by digits (e.g., "HS251217836041")
            for m in re.finditer(r'(HS\d+)', line):
                self.text_input.tag_add("code", f"{line_num}.{m.start(1)}", f"{line_num}.{m.end(1)}")
                
            # Shop: Ends with '店' (e.g., "湘雅附一店")
            for m in re.finditer(r'(\S+店)', line):
                self.text_input.tag_add("shop", f"{line_num}.{m.start(1)}", f"{line_num}.{m.end(1)}")
                
            # Direction: East/South/West/North (e.g., "北")
            for m in re.finditer(r'([东南西北])(?:\s|$)', line):
                self.text_input.tag_add("direction", f"{line_num}.{m.start(1)}", f"{line_num}.{m.end(1)}")
                
            # Room: Patterns like A-2311 or 4-1707
            # Match word containing digit and hyphen, or just digits if context implies
            # Let's try matching typical room patterns
            for m in re.finditer(r'([A-Za-z0-9]+-\d+)', line):
                self.text_input.tag_add("room", f"{line_num}.{m.start(1)}", f"{line_num}.{m.end(1)}")

    def _process_modified(self):
        try:
            self.text_input.edit_modified(False)
            self._highlight_syntax()
            
            content = self.text_input.get("1.0", tk.END).strip()
            lines = [line for line in content.splitlines() if line.strip()]
            count = len(lines)
            
            revenue = count * Config.PRICE_PER_SHOOT
            self.count_label.config(text=f"已输入：{count} 个文件夹 | 预计收入：¥{revenue}")
            
            # Gradient Logic
            # 0-5: selection -> purple (Fast ramp up)
            # 5-10: purple (Stable purple)
            # 10-30: purple -> pink (Intensifying to "very purple")
            
            if count <= 5:
                ratio = count / 5.0
                col = interpolate_color(self.colors['selection'], self.colors['purple'], ratio)
                # Switch text color when background gets bright enough
                fg_col = self.colors['fg'] if ratio < 0.5 else self.colors['bg']
            elif count <= 10:
                col = self.colors['purple']
                fg_col = self.colors['bg']
            elif count <= 30:
                ratio = (count - 10) / 20.0
                col = interpolate_color(self.colors['purple'], self.colors['pink'], ratio)
                fg_col = self.colors['bg']
            else:
                col = self.colors['pink']
                fg_col = self.colors['bg']
                
            self.status_bar.config(background=col, foreground=fg_col)
        except Exception:
            pass

    def browse_directory(self):
        d = filedialog.askdirectory()
        if d:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, d)

    def fill_example(self):
        examples = [
            "1.郭艳 HS251217836041 湘雅附一店 天健壹平方英里 A-2311 北",
            "2.龙苗 HS251216879300 芙蓉盛世店 新力紫园 4-1707 北",
        ]
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", "\n".join(examples))
        self.on_text_modified()

    def clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.on_text_modified()
        self.status_bar.config(text="已清空输入")

    def open_dir(self, path):
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
        self.open_dir(get_date_based_dirs()[0])

    def open_vr_dir(self):
        self.open_dir(get_date_based_dirs()[1])

    def copy_dir_paths(self):
        dirs = get_date_based_dirs()
        self.master.clipboard_clear()
        self.master.clipboard_append("\n".join(dirs))
        self.status_bar.config(text="目录路径已复制到剪贴板")

    def _toggle_anim(self):
        if self.anim_disable.get():
            self.photo_runner_canvas.pack_forget()
            self.vr_runner_canvas.pack_forget()
        else:
            self.photo_runner_canvas.pack(fill=tk.X, before=self.progress_photo)
            self.vr_runner_canvas.pack(fill=tk.X, before=self.progress_vr)

    def import_originals(self):
        anim_disabled = self.anim_disable.get()
        threading.Thread(target=self._run_import_task, args=(anim_disabled,), daemon=True).start()

    def _run_import_task(self, anim_disabled):
        try:
            base_root = Config.PATHS['root']
            
            # 使用 get_date_based_dirs 获取标准路径
            target_dirs = get_date_based_dirs(base_root, mode='import')
            target_photo = target_dirs[0]
            target_vr = target_dirs[1]
            
            source_photo = str(self.paths["photo_src"])
            source_vr = str(self.paths["vr_src"])
            
            tasks_config = [
                {
                    "src": source_photo, "dst": target_photo, "kind": "photo", "label": "相片 (Sigma)",
                    "bar": self.progress_photo, "label_widget": self.progress_photo_label, "canvas": self.photo_runner_canvas, "prefix": "相片导入进度"
                },
                {
                    "src": source_vr, "dst": target_vr, "kind": "vr", "label": "VR (Osmo)",
                    "bar": self.progress_vr, "label_widget": self.progress_vr_label, "canvas": self.vr_runner_canvas, "prefix": "VR 导入进度"
                }
            ]
            
            self.master.after(0, lambda: self.status_bar.config(text="正在扫描Sigma FP 和 Dji OSMO 360…"))
        
        # Use a separate function to process results and update UI to avoid logic errors in the main block
            def process_results(futures_list):
                try:
                    final_results = []
                    for f in futures_list:
                        try:
                            res = f.result()
                            # Handle tuple return from ImportTask: (logs, errors, moved_count, ...)
                            if isinstance(res, tuple):
                                final_results.append({'moved': res[2], 'errors': res[1]})
                            else:
                                final_results.append(res)
                        except Exception as e:
                            # Log error internally but proceed
                            final_results.append({'moved': 0, 'errors': [str(e)]})
                    
                    total_moved = sum(r['moved'] for r in final_results)
                    # Force status update even if errors happened
                    self.master.after(0, self._show_import_summary, total_moved, [])
                except Exception:
                     # Absolute fallback if result processing crashes
                     self.master.after(0, self._show_import_summary, 0, [])

            with ThreadPoolExecutor(max_workers=2) as ex:
                futures = [ex.submit(self._execute_single_import, cfg, anim_disabled) for cfg in tasks_config]
                # Wait for all futures to complete
                # We move result processing to after the context manager to ensure all threads are joined
                pass
                
            # Process results after all threads are joined
            process_results(futures)

        except Exception as e:
             # Absolute fallback
             self.master.after(0, self._show_import_summary, 0, [])

    def _execute_single_import(self, config, anim_disabled):
        bar = config['bar']
        lbl = config['label_widget']
        canvas = config['canvas']
        prefix = config['prefix']
        
        def on_start(total):
            self.master.after(0, lambda: [bar.configure(maximum=total), canvas.reset() if not anim_disabled else None])
            
        def on_progress(curr, total, speed):
            self.master.after(0, lambda: [
                bar.configure(value=curr),
                lbl.config(text=f"{prefix}: {int(curr/total*100)}% ({curr}/{total}) {speed}"),
                canvas.update_progress(curr, total) if not anim_disabled else None
            ])
            
        def on_status(msg):
             self.master.after(0, lambda: lbl.config(text=f"{prefix}: {msg}"))

        task = ImportTask(callbacks={
            'on_start': on_start,
            'on_progress': on_progress,
            'on_status_change': on_status
        })
        
        result = task.run(config)
        
        # Complete
        self.master.after(0, lambda: [
            lbl.config(text=f"{prefix}: 完成"),
            canvas.complete() if not anim_disabled else None
        ])
        
        return result

    def _show_import_summary(self, moved_count, errors):
        summary = "已全部导入完成"
            
        # User requested to hide error prompts completely for import flow
        # "不需要有导入流程出现错误和导入流程异常终止的提示"
        self.status_bar.config(text=summary)
        # Suppress the warning dialog
        # if errors:
        #    messagebox.showwarning("导入提示", "\n".join(errors))

    def create_folders(self):
        input_text = self.text_input.get("1.0", tk.END)
        folder_names = [line.strip() for line in input_text.splitlines() if line.strip()]
        
        if not folder_names:
            messagebox.showerror("错误", "请输入至少一个文件夹名称")
            return

        # Reuse photo progress bar
        self.progress_photo_label.config(text="文件夹创建进度:")
        self.progress_photo['value'] = 0
        self.progress_vr['value'] = 0
        self.progress_vr_label.config(text="")
        
        def callback(action, value):
            if action == 'init':
                self.progress_photo.configure(maximum=value)
            elif action == 'step':
                self.progress_photo.step(1)
                self.master.update_idletasks()
                
        success, errors, target_dirs = FolderService.create_folders(folder_names, callback)
        
        if success is None: # Critical error
             messagebox.showerror("错误", errors[0])
             return

        total_photo = success[target_dirs[0]]
        total_vr = success[target_dirs[1]]
        revenue = total_photo * Config.PRICE_PER_SHOOT
        
        msg = f"创建成功\n相片: {total_photo}\nVR: {total_vr}\n收入: ¥{revenue}"
        messagebox.showinfo("完成", msg)
        if errors:
            messagebox.showwarning("注意", "\n".join(errors))
            
        self.status_bar.config(text=f"创建完成 - ¥{revenue}")
        self.progress_photo_label.config(text="相片导入进度: 0%")
