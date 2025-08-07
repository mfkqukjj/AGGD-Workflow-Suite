import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import fnmatch
import re

class BatchExtractTool(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("批量文件提取工具")
        self.geometry("600x500")
        self.transient(master)
        self.grab_set()
        
        # 初始化变量
        self.source_folder = tk.StringVar()
        self.target_extract_folder = tk.StringVar()
        self.create_in_source = tk.BooleanVar(value=True)
        self.use_regex = tk.BooleanVar(value=False)
        self.extract_mode = tk.StringVar(value="move")
        
        # 创建界面
        self.create_extract_window()
        
    def create_extract_window(self):
        """创建批量提取窗口"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择区域
        source_frame = ttk.LabelFrame(main_frame, text="源文件夹", padding=5)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(source_frame, textvariable=self.source_folder, text="未选择文件夹").pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="选择文件夹", command=self.select_extract_source).pack(side=tk.LEFT, padx=2)
        
        # 文件筛选条件区域
        filter_frame = ttk.LabelFrame(main_frame, text="文件筛选", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件类型/名称输入
        pattern_frame = ttk.Frame(filter_frame)
        pattern_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pattern_frame, text="文件类型/名称:").pack(side=tk.LEFT, padx=5)
        self.pattern_entry = ttk.Entry(pattern_frame)
        self.pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 使用正则表达式选项
        ttk.Checkbutton(filter_frame, text="使用正则表达式", 
                       variable=self.use_regex).pack(anchor=tk.W, padx=5)
        
        # 目标文件夹选择区域
        target_frame = ttk.LabelFrame(main_frame, text="存放目录", padding=5)
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(target_frame, textvariable=self.target_extract_folder, 
                 text="未选择目录").pack(side=tk.LEFT, padx=5)
        ttk.Button(target_frame, text="选择存放目录", 
                  command=self.select_extract_target).pack(side=tk.LEFT, padx=2)
        
        # 在源文件夹创建目录选项
        ttk.Checkbutton(target_frame, text="于源文件处创建根目录", 
                       variable=self.create_in_source,
                       command=self.toggle_target_selection).pack(anchor=tk.W, padx=5)
        
        # 操作模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="操作模式", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="移动文件", 
                       variable=self.extract_mode, 
                       value="move").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="复制文件", 
                       variable=self.extract_mode, 
                       value="copy").pack(side=tk.LEFT, padx=5)
    
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="运行", 
                  command=self.execute_extract).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置", 
                  command=self.reset_extract_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def select_extract_source(self):
        """选择源文件夹"""
        folder = filedialog.askdirectory(parent=self)
        if folder:
            self.source_folder.set(folder)
    
    def select_extract_target(self):
        """选择目标文件夹"""
        folder = filedialog.askdirectory(parent=self)
        if folder:
            self.target_extract_folder.set(folder)
    
    def toggle_target_selection(self):
        """切换目标目录选择状态"""
        # 当选择在源文件夹创建目录时，禁用目标目录选择
        if self.create_in_source.get():
            self.target_button.config(state=tk.DISABLED)
            self.target_extract_folder.set("")
        else:
            self.target_button.config(state=tk.NORMAL)
    
    def reset_extract_form(self):
        """重置表单"""
        self.source_folder.set("")
        self.target_extract_folder.set("")
        self.pattern_entry.delete(0, tk.END)
        self.use_regex.set(False)
        self.create_in_source.set(True)
        self.extract_mode.set("move")
    
    def execute_extract(self):
        """执行提取操作"""
        source = self.source_folder.get()
        if not source:
            messagebox.showwarning("警告", "请选择源文件夹！")
            return
        
        pattern = self.pattern_entry.get().strip()
        if not pattern:
            messagebox.showwarning("警告", "请输入文件筛选条件！")
            return
        
        # 确定目标目录
        if self.create_in_source.get():
            # 在源文件夹下创建新目录
            target = os.path.join(source, "Extracted_Files")
            os.makedirs(target, exist_ok=True)
        else:
            target = self.target_extract_folder.get()
            if not target:
                messagebox.showwarning("警告", "请选择目标目录！")
                return
        
        # 收集文件
        file_list = []
        if self.use_regex.get():
            # 使用正则表达式
            regex = re.compile(pattern)
            for root, _, files in os.walk(source):
                for file in files:
                    if regex.search(file):
                        file_list.append(os.path.join(root, file))
        else:
            # 使用通配符
            for root, _, files in os.walk(source):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_list.append(os.path.join(root, file))
        
        # 根据操作模式复制或移动
        if self.extract_mode.get() == "copy":
            for file_path in file_list:
                # 保持相对路径结构
                rel_path = os.path.relpath(file_path, source)
                target_path = os.path.join(target, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(file_path, target_path)
        else:  # move
            for file_path in file_list:
                rel_path = os.path.relpath(file_path, source)
                target_path = os.path.join(target, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(file_path, target_path)
        
        messagebox.showinfo("完成", f"操作完成！共处理 {len(file_list)} 个文件。\n目标目录：{target}")