import sys
import os
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mypackage.gui_main import MainApplication
from mypackage.user_auth import UserAuth

def disable_widget(widget):
    """递归禁用所有支持的控件"""
    try:
        if hasattr(widget, 'state') and callable(getattr(widget, 'state')):
            widget.state(['disabled'])
        elif hasattr(widget, 'configure'):
            widget.configure(state='disabled')
    except tk.TclError:
        pass
    
    for child in widget.winfo_children():
        disable_widget(child)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("AGGD工作流套件")  # 设置主窗口标题
    
    # 设置窗口样式
    style = ttk.Style()
    style.configure("Function.TButton", 
                   font=('微软雅黑', 11),
                   padding=4,
                   width=12,
                   relief="flat")
    
    style.configure("Small.TButton", 
                   font=('微软雅黑', 9),
                   padding=2,
                   width=6)
    
    # 创建主应用窗口
    app = MainApplication(root)
    
    # 等待窗口完全加载
    root.update()
    
    # 禁用所有控件
    disable_widget(root)
    
    # 创建认证窗口
    auth = UserAuth(root, app)
    
    root.mainloop()
