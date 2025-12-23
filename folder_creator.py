import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import platform

class UniversalFolderCreator:
    def __init__(self, master):
        self.master = master
        master.title("房堪文件夹批量生成工具")
        master.geometry("800x600")
        
        # 检测操作系统
        self.os_type = platform.system()
        self.set_style()
        
        # 界面布局
        self.create_widgets()
        
    def set_style(self):
        """配置跨平台样式"""
        self.style = ttk.Style()
        
        # 统一颜色配置
        self.colors = {
            'text_primary': '#000000',    # 主文本颜色
            'bg_primary': '#FFFFFF',     # 输入框背景
            'button_win': '#0078D7',      # Windows按钮色
            'button_mac': '#007AFF'       # macOS按钮色
        }
        
        # 根据系统设置主题
        if self.os_type == 'Windows':
            self.style.theme_use('vista')
            self.fonts = {
                'body': ('微软雅黑', 10),
                'button': ('微软雅黑', 10, 'bold')
            }
        elif self.os_type == 'Darwin':  # macOS
            self.style.theme_use('aqua')
            self.fonts = {
                'body': ('Helvetica', 12),
                'button': ('Helvetica', 12, 'bold')
            }
        else:  # Linux
            self.style.theme_use('clam')
            self.fonts = {
                'body': ('Sans', 10),
                'button': ('Sans', 10, 'bold')
            }
        
        # 强制设置文本颜色
        self.style.configure('TEntry', foreground=self.colors['text_primary'])
        self.style.configure('TText', foreground=self.colors['text_primary'])
        
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text=" 输入文件夹名称（每行一个）")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 文本输入框
        self.text_input = tk.Text(
            input_frame,
            height=10,
            wrap=tk.NONE,
            font=self.fonts['body'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],        # 文本颜色
            insertbackground=self.colors['text_primary'],  # 光标颜色
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
        
        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # 目录选择
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(dir_frame, 
                text="输出目录：", 
                font=self.fonts['body']).pack(side=tk.LEFT)
        
        self.dir_entry = ttk.Entry(dir_frame, font=self.fonts['body'])
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 浏览按钮
        btn_style = 'primary.TButton' if self.os_type == 'Darwin' else 'TButton'
        ttk.Button(dir_frame,
                 text="浏览...",
                 command=self.browse_directory,
                 style=btn_style).pack(side=tk.LEFT)
        
        # 创建按钮
        ttk.Button(control_frame,
                 text="开始创建",
                 command=self.create_folders,
                 style=btn_style).pack(side=tk.RIGHT)
        
        # 状态栏
        self.status_bar = ttk.Label(
            self.master,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.fonts['body']
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 按钮样式
        if self.os_type == 'Windows':
            self.style.configure('TButton',
                                foreground='white',
                                background=self.colors['button_win'])
        elif self.os_type == 'Darwin':
            self.style.configure('primary.TButton',
                                foreground='white',
                                background=self.colors['button_mac'])
        
    def browse_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.status_bar.config(text=f"当前目录：{directory}")
            
    def create_folders(self):
        """创建文件夹核心逻辑"""
        target_dir = self.dir_entry.get().strip()
        if not target_dir:
            messagebox.showerror("错误", "请先选择输出目录")
            return
            
        if not os.path.exists(target_dir):
            messagebox.showerror("错误", "指定目录不存在")
            return
            
        input_text = self.text_input.get("1.0", tk.END)
        folder_names = [line.strip() for line in input_text.splitlines() if line.strip()]
        
        if not folder_names:
            messagebox.showerror("错误", "请输入至少一个文件夹名称")
            return
            
        success = []
        errors = []
        for name in folder_names:
            try:
                # 替换非法字符
                valid_name = name.replace('/', '／').replace('\\', '＼')
                full_path = os.path.join(target_dir, valid_name)
                os.makedirs(full_path, exist_ok=False)
                success.append(valid_name)
            except FileExistsError:
                errors.append(f"'{name}' 已存在")
            except OSError as e:
                errors.append(f"'{name}' 创建失败: {e.strerror}")
            except Exception as e:
                errors.append(f"'{name}' 发生未知错误: {str(e)}")
                
        # 显示结果
        report = []
        if success:
            x = len(success)
            y = x * 35
            success_msg = f"文件夹创建成功\n\n您今日拍摄{x}套房堪\n\n🎉恭喜收米 ¥{y}！🎉"
            messagebox.showinfo("操作成功", success_msg)
            
        if errors:
            error_msg = "以下问题需要注意：\n\n" + "\n".join(errors)
            messagebox.showwarning("操作完成", error_msg)
            
        self.status_bar.config(text=f"操作完成 - 成功{len(success)}个，失败{len(errors)}个")

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