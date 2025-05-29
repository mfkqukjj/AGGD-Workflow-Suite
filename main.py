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
                   font=('微软雅黑', 12),
                   padding=8,
                   relief="flat")
    app = MainApplication(root)
    root.mainloop()
