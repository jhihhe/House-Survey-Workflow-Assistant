import tkinter as tk
import platform
from src.ui.main_window import UniversalFolderCreator

def main():
    root = tk.Tk()

    # Hi-DPI
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

if __name__ == "__main__":
    main()
