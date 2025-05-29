# 功能示例代码
import tkinter as tk
from tkinter import messagebox, ttk  # 只保留需要的导入

class HelloWorld(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.attributes('-topmost', True)
        self.title("这是一个示例")
        
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_action_buttons()

    def create_action_buttons(self):
        frame = ttk.Frame(self.main_frame)
        frame.grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="运行", command=self.run_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="退出", command=self.destroy).pack(side=tk.LEFT)  # 使用destroy替代quit

    def run_merge(self):
        try:
            messagebox.showinfo("提示", "Hello world！")
        except Exception as e:
            messagebox.showerror("错误", f"运行过程中发生错误：\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HelloWorld(root)
    root.mainloop()
