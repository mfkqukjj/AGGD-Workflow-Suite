import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import glob
import os
import subprocess
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
        
        # 第一步：输入选择部分
        self.create_input_section()
        # 第二步：模板选择
        self.create_template_section()
        # 第三步：输出目录
        self.create_output_section()
        # 运行按钮
        self.create_action_buttons()
        
        # 初始化变量
        self.input_paths = []
        self.template_path = ""
        self.output_dir = ""

    def create_input_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="1. 选择输入源", padding=10)
        frame.grid(row=0, column=0, sticky="w", pady=5)
        
        self.input_type = tk.IntVar(value=0)
        ttk.Radiobutton(frame, text="选择文件（多选）", variable=self.input_type, value=1,
                       command=self.select_files).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(frame, text="选择文件夹", variable=self.input_type, value=2,
                       command=self.select_folder).grid(row=1, column=0, sticky="w")
        
        self.input_label = ttk.Label(frame, text="当前选择：无")
        self.input_label.grid(row=2, column=0, sticky="w")

    def create_template_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="2. 格式模板（可选）", padding=10)
        frame.grid(row=1, column=0, sticky="w", pady=5)
        
        self.use_template = tk.BooleanVar()
        ttk.Checkbutton(frame, text="使用格式模板", variable=self.use_template,
                       command=self.toggle_template).grid(row=0, column=0, sticky="w")
        self.template_btn = ttk.Button(frame, text="选择模板文件", state="disabled",
                                     command=self.select_template)
        self.template_btn.grid(row=0, column=1, padx=5)
        self.template_label = ttk.Label(frame, text="未选择模板")
        self.template_label.grid(row=1, column=0, columnspan=2, sticky="w")

    def create_output_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="3. 输出设置", padding=10)
        frame.grid(row=2, column=0, sticky="w", pady=5)
        
        self.auto_save = tk.BooleanVar()
        ttk.Checkbutton(frame, text="自动保存到数据目录", variable=self.auto_save,
                       command=self.toggle_auto_save).grid(row=0, column=0, sticky="w")
        
        self.output_btn = ttk.Button(frame, text="选择输出目录", command=self.select_output)
        self.output_btn.grid(row=1, column=0, pady=5)
        self.output_label = ttk.Label(frame, text="当前输出目录：无")
        self.output_label.grid(row=2, column=0, sticky="w")

    def create_action_buttons(self):
        frame = ttk.Frame(self.main_frame)
        frame.grid(row=3, column=0, pady=10)
        ttk.Button(frame, text="运行", command=self.run_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="重置", command=self.reset_all).pack(side=tk.LEFT, padx=5)  # 新增重置按钮
        ttk.Button(frame, text="关闭", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def select_files(self):
        self.input_paths = filedialog.askopenfilenames()
        self.input_label.config(text=f"已选择 {len(self.input_paths)} 个文件")
        self.update_output_path()

    def select_folder(self):
        folder = filedialog.askdirectory(parent=self)
        if folder:
            self.input_paths = [folder]
            self.input_label.config(text=f"已选择文件夹：{folder}")
            self.update_output_path()

    def toggle_template(self):
        state = "normal" if self.use_template.get() else "disabled"
        self.template_btn.config(state=state)

    def select_template(self):
        path = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv")])
        if path:
            self.template_path = path
            self.template_label.config(text=f"已选模板：{os.path.basename(path)}")

    def toggle_auto_save(self):
        self.output_btn.config(state="disabled" if self.auto_save.get() else "normal")
        self.update_output_path()

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self.output_label.config(text=f"当前输出目录：{path}")

    def update_output_path(self):
        if self.auto_save.get() and self.input_paths:
            base_path = os.path.dirname(self.input_paths[0]) if self.input_type.get() == 1 else self.input_paths[0]
            self.output_dir = base_path
            self.output_label.config(text=f"当前输出目录：{base_path}")

    def run_merge(self):
        try:
            # 获取输入文件列表
            if self.input_type.get() == 1:  # 文件模式
                files = self.input_paths
                folder_path = os.path.dirname(files[0]) if files else ""
            else:  # 文件夹模式
                folder_path = self.input_paths[0]
                csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
                xlsx_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
                files = csv_files + xlsx_files

            # 处理模板
            if self.use_template.get() and self.template_path:
                template_df = pd.read_excel(self.template_path) if '.xls' in self.template_path else pd.read_csv(self.template_path)
                dfs = [template_df]
            else:
                dfs = []

            # 读取所有文件
            for f in files:
                if f.endswith('.csv'):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)
                dfs.append(df)

            # 创建输出目录
            output_dir = self.output_dir if self.output_dir else os.getcwd()
            os.makedirs(output_dir, exist_ok=True)

            # 合并并保存
            combined_df = pd.concat(dfs, ignore_index=True)
            output_path = os.path.join(output_dir, f"【合并结果】{datetime.now().strftime('%Y%m%d-%H%M')}.xlsx")
            combined_df.to_excel(output_path, index=False)

            # 显示完成对话框
            self.show_completion_dialog(output_dir)
        except Exception as e:
            messagebox.showerror("错误", f"运行过程中发生错误：\n{str(e)}")

    def show_completion_dialog(self, output_dir):
        answer = messagebox.askyesno("完成", "数据已成功合并！\n是否要跳转到结果文件夹？")
        if answer:
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            else:  # macOS/Linux
                subprocess.Popen(['open', output_dir] if sys.platform == 'darwin' else ['xdg-open', output_dir])

    def reset_all(self):
        """重置所有选择和设置"""
        # 重置输入选择
        self.input_paths = []
        self.input_type.set(0)
        self.input_label.config(text="当前选择：无")
        
        # 重置模板设置
        self.template_path = ""
        self.use_template.set(False)
        self.template_btn.config(state="disabled")
        self.template_label.config(text="未选择模板")
        
        # 重置输出设置
        self.output_dir = ""
        self.auto_save.set(False)
        self.output_btn.config(state="normal")
        self.output_label.config(text="当前输出目录：无")
        
        # 提示用户重置完成
        messagebox.showinfo("提示", "所有设置已重置")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataConcatTool(root)
    root.mainloop()
