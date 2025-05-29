# 功能示例代码
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import glob
import os
from datetime import datetime
import sys

class DataConcatTool(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)  # 正确继承
        self.transient(master)  # 标记为主窗口的附属窗口
        self.grab_set()         # 独占焦点
        self.attributes('-topmost', True)  # 强制置顶
        self.title("数据合并工具（支持指定模板）")
        # 创建主容器
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        

        # 运行按钮
        self.create_action_buttons()
        

 

    def create_action_buttons(self):
        frame = ttk.Frame(self.main_frame)
        frame.grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="运行", command=self.run_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="退出", command=self.quit).pack(side=tk.LEFT)

   

    def run_merge(self):
        try:
            messagebox.showerror("Hello mfk")
        except Exception as e:
            messagebox.showerror("错误", f"运行过程中发生错误：\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataConcatTool(root)
    root.mainloop()
