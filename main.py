import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


from mypackage.gui_main import MainApplication
import tkinter as tk
from tkinter import ttk

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Function.TButton", 
                   font=('微软雅黑', 11),
                   padding=4,              # 减小padding
                   width=12,              # 设置固定宽度
                   relief="flat")
    # 添加小按钮样式
    style.configure("Small.TButton", 
                   font=('微软雅黑', 9),  # 字号调小
                   padding=2,            # 内边距调小
                   width=6)             # 按钮宽度调小
    
    app = MainApplication(root)
    root.mainloop()
