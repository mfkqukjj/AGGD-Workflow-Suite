import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import glob
import re
import shutil
import time
import fnmatch
import sys
import subprocess

class FileOperations(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("批量文件操作工具")
        self.geometry("800x600")
        self.transient(master)
        self.grab_set()
        
        # 初始化变量
        self.selected_folders = []
        self.file_types = []
        
        self.create_main_window()
        
    def create_main_window(self):
        """创建主窗口"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建功能按钮区
        ttk.Label(main_frame, text="请选择要使用的功能：", 
                 font=('微软雅黑', 12)).pack(pady=(0, 20))
        
        buttons = [
            ("批量读取文件名", self.create_file_list_window),
            ("批量修改文件名", self.create_rename_window),
            ("批量提取", self.create_extract_window)  # 新增
        ]
        
        for text, command in buttons:
            ttk.Button(main_frame, text=text, command=command,
                      style="Function.TButton").pack(pady=10, fill=tk.X)
        
        # 底部关闭按钮
        ttk.Button(main_frame, text="关闭", 
                  command=self.destroy).pack(pady=(20, 0))

    def create_file_list_window(self):
        """创建文件名读取窗口"""
        dialog = tk.Toplevel(self)
        dialog.title("批量读取文件名")
        dialog.geometry("800x700")
        dialog.transient(self)
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件夹选择区域
        folder_frame = ttk.LabelFrame(main_frame, text="选择目录", padding=5)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_var = tk.StringVar()
        self.folder_label = ttk.Label(folder_frame, text="已选择文件夹：0")  # 添加引用
        self.folder_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(folder_frame, text="选择文件夹", 
                  command=lambda: self.select_folders(dialog)).pack(side=tk.LEFT, padx=2)
        ttk.Button(folder_frame, text="清除选择",
                  command=self.clear_folders).pack(side=tk.LEFT, padx=2)

        # 文件类型筛选区域
        filter_frame = ttk.LabelFrame(main_frame, text="文件筛选", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预定义文件类型复选框
        types_frame = ttk.Frame(filter_frame)
        types_frame.pack(fill=tk.X)
        
        self.type_vars = {}
        common_types = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf']
        for i, ftype in enumerate(common_types):
            var = tk.BooleanVar()
            self.type_vars[ftype] = var
            ttk.Checkbutton(types_frame, text=ftype, 
                           variable=var).grid(row=i//3, column=i%3, padx=5, pady=2)
        
        # 自定义筛选条件
        custom_frame = ttk.Frame(filter_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        ttk.Label(custom_frame, 
                 text="自定义筛选:").pack(side=tk.LEFT, padx=5)
        self.custom_filter = ttk.Entry(custom_frame)
        self.custom_filter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 显示选项
        options_frame = ttk.LabelFrame(main_frame, text="显示选项", padding=5)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 排序选项
        sort_frame = ttk.Frame(options_frame)
        sort_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sort_frame, text="排序方式：").pack(side=tk.LEFT, padx=5)
        
        self.sort_method = tk.StringVar(value="name")
        ttk.Radiobutton(sort_frame, text="按文件名", 
                       variable=self.sort_method, 
                       value="name").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sort_frame, text="按文件类型", 
                       variable=self.sort_method, 
                       value="type").pack(side=tk.LEFT, padx=5)
        
        # 子目录选项
        subdir_frame = ttk.Frame(options_frame)
        subdir_frame.pack(fill=tk.X, pady=2)
        self.include_subdirs = tk.BooleanVar(value=True)
        ttk.Checkbutton(subdir_frame, text="包含子目录文件", 
                        variable=self.include_subdirs).pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="文件列表", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="获取文件名", 
                  command=self.get_file_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制结果",
                  command=self.copy_results).pack(side=tk.LEFT, padx=5)  # 新增复制按钮
        ttk.Button(button_frame, text="保存结果", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def create_rename_window(self):
        """创建批量重命名窗口"""
        dialog = tk.Toplevel(self)
        dialog.title("批量修改文件名")
        dialog.geometry("800x700")  # 增加窗口高度以适应新内容
        dialog.transient(self)
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 目标文件夹选择区域
        folder_frame = ttk.LabelFrame(main_frame, text="目标文件夹", padding=5)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.target_folder = tk.StringVar()
        ttk.Label(folder_frame, textvariable=self.target_folder,
                 text="未选择文件夹").pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="选择文件夹",
                  command=self.select_target_folder).pack(side=tk.LEFT, padx=2)
        
        # 新增：当前目录文件列表预览
        preview_frame = ttk.LabelFrame(main_frame, text="当前目录文件列表", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        preview_button_frame = ttk.Frame(preview_frame)
        preview_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(preview_button_frame, text="读取文件名",
                  command=self.read_current_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_button_frame, text="复制文件名",
                  command=lambda: self.copy_results(self.preview_text)).pack(side=tk.LEFT, padx=2)
        
        # 重命名规则输入区域
        rule_frame = ttk.LabelFrame(main_frame, text="重命名规则", padding=5)
        rule_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(rule_frame, 
                 text="请输入重命名规则（每行：原文件名 新文件名）:").pack(anchor=tk.W)
        
        self.rule_text = scrolledtext.ScrolledText(rule_frame, height=10)
        self.rule_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="执行重命名",
                  command=self.execute_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭",
                  command=dialog.destroy).pack(side=tk.LEFT)

    def create_extract_window(self):
        """创建批量提取窗口"""
        dialog = tk.Toplevel(self)
        dialog.title("批量文件提取")
        dialog.geometry("600x500")
        dialog.transient(self)
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择区域
        source_frame = ttk.LabelFrame(main_frame, text="源文件夹", padding=5)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_folder = tk.StringVar()
        ttk.Label(source_frame, textvariable=self.source_folder,
                 text="未选择文件夹").pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="选择文件夹",
                  command=lambda: self.select_extract_source(dialog)).pack(side=tk.LEFT, padx=2)
        
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
        self.use_regex = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="使用正则表达式", 
                        variable=self.use_regex).pack(anchor=tk.W, padx=5)
        
        # 目标文件夹选择区域
        target_frame = ttk.LabelFrame(main_frame, text="存放目录", padding=5)
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.target_extract_folder = tk.StringVar()
        ttk.Label(target_frame, textvariable=self.target_extract_folder,
                 text="未选择目录").pack(side=tk.LEFT, padx=5)
        ttk.Button(target_frame, text="选择存放目录",
                  command=lambda: self.select_extract_target(dialog)).pack(side=tk.LEFT, padx=2)
        
        # 在源文件夹创建目录选项
        self.create_in_source = tk.BooleanVar(value=True)
        ttk.Checkbutton(target_frame, text="于源文件处创建根目录", 
                        variable=self.create_in_source,
                        command=self.toggle_target_selection).pack(anchor=tk.W, padx=5)
        
        # 在筛选条件区域下方添加操作模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="操作模式", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.extract_mode = tk.StringVar(value="move")
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
                  command=lambda: self.reset_extract_form(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def select_folders(self, parent):
        """选择多个文件夹"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            if folder not in self.selected_folders:  # 避免重复添加
                self.selected_folders.append(folder)
                # 更新显示标签
                self.folder_label.config(text=f"已选择文件夹：{len(self.selected_folders)}")
                # 显示选择的文件夹列表
                folders_str = "\n".join(self.selected_folders)
                messagebox.showinfo("当前选择的文件夹", f"已选择的文件夹列表：\n{folders_str}")

    def select_extract_folders(self, parent):
        """选择多个文件夹用于提取"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            if folder not in self.selected_folders:  # 避免重复添加
                self.selected_folders.append(folder)
                # 更新显示标签
                self.extract_folder_label.config(text=f"已选择文件夹：{len(self.selected_folders)}")
                # 显示选择的文件夹列表
                folders_str = "\n".join(self.selected_folders)
                messagebox.showinfo("当前选择的文件夹", f"已选择的文件夹列表：\n{folders_str}")

    def select_target_folder(self):
        """选择目标文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)
    
    def get_file_list(self):
        """获取文件列表"""
        if not self.selected_folders:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
        
        self.result_text.delete('1.0', tk.END)
        total_files = 0
        
        for folder_index, folder in enumerate(self.selected_folders, 1):
            folder_files = []
            selected_types = [ext for ext, var in self.type_vars.items() if var.get()]
            custom_pattern = self.custom_filter.get().strip()
            
            def get_files_from_dir(dir_path, is_root=True):
                files = []
                try:
                    with os.scandir(dir_path) as entries:
                        for entry in entries:
                            if entry.is_file():
                                # 排除临时文件
                                if not (entry.name.startswith('~') or 
                                      entry.name.startswith('.') or 
                                      entry.name.endswith('.tmp') or 
                                      entry.name.endswith('.temp') or 
                                      '~$' in entry.name):
                                
                                    if not selected_types and not custom_pattern:
                                        files.append(entry.path)
                                    else:
                                        if any(entry.name.endswith(t) for t in selected_types):
                                            files.append(entry.path)
                                        elif custom_pattern and glob.fnmatch.fnmatch(entry.name, custom_pattern):
                                            files.append(entry.path)
                        
                            elif entry.is_dir() and self.include_subdirs.get() and not is_root:
                                files.extend(get_files_from_dir(entry.path, False))
                except Exception as e:
                    messagebox.showerror("错误", f"读取目录失败：{str(e)}")
                return files
            
            # 首先获取根目录文件
            root_files = get_files_from_dir(folder)
            folder_files.extend(root_files)
            
            # 如果包含子目录，获取子目录文件
            if self.include_subdirs.get():
                for root, dirs, _ in os.walk(folder):
                    if root != folder:  # 跳过根目录
                        subdir_files = get_files_from_dir(root, False)
                        folder_files.extend(subdir_files)
            
            # 根据选择的方式排序
            def sort_key(file_path):
                name = os.path.basename(file_path)
                if self.sort_method.get() == "type":
                    # 按扩展名排序，相同扩展名按文件名排序
                    ext = os.path.splitext(name)[1].lower()
                    return (ext, name.lower())
                else:
                    # 按文件名排序
                    return name.lower()
            
            # 分离根目录和子目录文件
            root_files = [f for f in folder_files if os.path.dirname(f) == folder]
            subdir_files = [f for f in folder_files if os.path.dirname(f) != folder]
            
            # 分别排序
            root_files.sort(key=sort_key)
            subdir_files.sort(key=sort_key)
            
            # 显示文件夹标题
            folder_name = os.path.basename(folder) or folder
            self.result_text.insert(tk.END, f"\n{'='*50}\n")
            self.result_text.insert(tk.END, f"文件夹 {folder_index}: {folder_name}\n")
            self.result_text.insert(tk.END, f"{'='*50}\n\n")
            
            # 显示根目录文件
            if root_files:
                self.result_text.insert(tk.END, "【根目录】\n")
                for file_path in root_files:
                    self.result_text.insert(tk.END, f"{os.path.basename(file_path)}\n")
            
            # 显示子目录文件
            if subdir_files:
                current_subdir = ""
                for file_path in subdir_files:
                    subdir = os.path.relpath(os.path.dirname(file_path), folder)
                    if subdir != current_subdir:
                        current_subdir = subdir
                        self.result_text.insert(tk.END, f"\n【{subdir}】\n")
                    self.result_text.insert(tk.END, f"    {os.path.basename(file_path)}\n")
            
            total_files += len(root_files) + len(subdir_files)
        
        # 显示总计
        if self.selected_folders:
            self.result_text.insert(tk.END, f"\n{'='*50}\n")
            self.result_text.insert(tk.END, f"总计: {len(self.selected_folders)} 个文件夹, {total_files} 个文件\n")
        
        # 滚动到开头
        self.result_text.see("1.0")
        
        # 显示完成消息
        messagebox.showinfo("完成", f"共找到 {total_files} 个文件")

    def save_results(self):
        """保存结果到文件"""
        content = self.result_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("成功", "文件保存成功！")
    
    def execute_rename(self):
        """执行批量重命名"""
        target_folder = self.target_folder.get()
        if not target_folder:
            messagebox.showwarning("警告", "请选择目标文件夹！")
            return
            
        rules_text = self.rule_text.get('1.0', tk.END).strip()
        if not rules_text:
            messagebox.showwarning("警告", "请输入重命名规则！")
            return
            
        # 解析规则
        rules = {}
        for line in rules_text.split('\n'):
            if line.strip():
                parts = re.split(r'\s+', line.strip(), maxsplit=1)
                if len(parts) == 2:
                    old_name, new_name = parts
                    rules[old_name] = new_name
        
        if not rules:
            messagebox.showwarning("警告", "未找到有效的重命名规则！")
            return
            
        # 执行重命名
        success_count = 0
        errors = []
        
        for old_name, new_name in rules.items():
            old_path = os.path.join(target_folder, old_name)
            new_path = os.path.join(target_folder, new_name)
            
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    success_count += 1
                else:
                    errors.append(f"文件不存在: {old_name}")
            except Exception as e:
                errors.append(f"重命名失败 {old_name}: {str(e)}")
        
        # 显示结果
        result_message = f"成功重命名 {success_count} 个文件\n"
        if errors:
            result_message += "\n失败项目：\n" + "\n".join(errors)
        
        messagebox.showinfo("完成", result_message)

    def select_folders(self, parent):
        """选择多个文件夹"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            if folder not in self.selected_folders:  # 避免重复添加
                self.selected_folders.append(folder)
                # 更新显示标签
                self.folder_label.config(text=f"已选择文件夹：{len(self.selected_folders)}")
                # 显示选择的文件夹列表
                folders_str = "\n".join(self.selected_folders)
                messagebox.showinfo("当前选择的文件夹", f"已选择的文件夹列表：\n{folders_str}")

    def select_extract_folders(self, parent):
        """选择多个文件夹用于提取"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            if folder not in self.selected_folders:  # 避免重复添加
                self.selected_folders.append(folder)
                # 更新显示标签
                self.extract_folder_label.config(text=f"已选择文件夹：{len(self.selected_folders)}")
                # 显示选择的文件夹列表
                folders_str = "\n".join(self.selected_folders)
                messagebox.showinfo("当前选择的文件夹", f"已选择的文件夹列表：\n{folders_str}")

    def select_target_folder(self):
        """选择目标文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)
    
    def get_file_list(self):
        """获取文件列表"""
        if not self.selected_folders:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
        
        self.result_text.delete('1.0', tk.END)
        total_files = 0
        
        for folder_index, folder in enumerate(self.selected_folders, 1):
            folder_files = []
            selected_types = [ext for ext, var in self.type_vars.items() if var.get()]
            custom_pattern = self.custom_filter.get().strip()
            
            def get_files_from_dir(dir_path, is_root=True):
                files = []
                try:
                    with os.scandir(dir_path) as entries:
                        for entry in entries:
                            if entry.is_file():
                                # 排除临时文件
                                if not (entry.name.startswith('~') or 
                                      entry.name.startswith('.') or 
                                      entry.name.endswith('.tmp') or 
                                      entry.name.endswith('.temp') or 
                                      '~$' in entry.name):
                                
                                    if not selected_types and not custom_pattern:
                                        files.append(entry.path)
                                    else:
                                        if any(entry.name.endswith(t) for t in selected_types):
                                            files.append(entry.path)
                                        elif custom_pattern and glob.fnmatch.fnmatch(entry.name, custom_pattern):
                                            files.append(entry.path)
                        
                            elif entry.is_dir() and self.include_subdirs.get() and not is_root:
                                files.extend(get_files_from_dir(entry.path, False))
                except Exception as e:
                    messagebox.showerror("错误", f"读取目录失败：{str(e)}")
                return files
            
            # 首先获取根目录文件
            root_files = get_files_from_dir(folder)
            folder_files.extend(root_files)
            
            # 如果包含子目录，获取子目录文件
            if self.include_subdirs.get():
                for root, dirs, _ in os.walk(folder):
                    if root != folder:  # 跳过根目录
                        subdir_files = get_files_from_dir(root, False)
                        folder_files.extend(subdir_files)
            
            # 根据选择的方式排序
            def sort_key(file_path):
                name = os.path.basename(file_path)
                if self.sort_method.get() == "type":
                    # 按扩展名排序，相同扩展名按文件名排序
                    ext = os.path.splitext(name)[1].lower()
                    return (ext, name.lower())
                else:
                    # 按文件名排序
                    return name.lower()
            
            # 分离根目录和子目录文件
            root_files = [f for f in folder_files if os.path.dirname(f) == folder]
            subdir_files = [f for f in folder_files if os.path.dirname(f) != folder]
            
            # 分别排序
            root_files.sort(key=sort_key)
            subdir_files.sort(key=sort_key)
            
            # 显示文件夹标题
            folder_name = os.path.basename(folder) or folder
            self.result_text.insert(tk.END, f"\n{'='*50}\n")
            self.result_text.insert(tk.END, f"文件夹 {folder_index}: {folder_name}\n")
            self.result_text.insert(tk.END, f"{'='*50}\n\n")
            
            # 显示根目录文件
            if root_files:
                self.result_text.insert(tk.END, "【根目录】\n")
                for file_path in root_files:
                    self.result_text.insert(tk.END, f"{os.path.basename(file_path)}\n")
            
            # 显示子目录文件
            if subdir_files:
                current_subdir = ""
                for file_path in subdir_files:
                    subdir = os.path.relpath(os.path.dirname(file_path), folder)
                    if subdir != current_subdir:
                        current_subdir = subdir
                        self.result_text.insert(tk.END, f"\n【{subdir}】\n")
                    self.result_text.insert(tk.END, f"    {os.path.basename(file_path)}\n")
            
            total_files += len(root_files) + len(subdir_files)
        
        # 显示总计
        if self.selected_folders:
            self.result_text.insert(tk.END, f"\n{'='*50}\n")
            self.result_text.insert(tk.END, f"总计: {len(self.selected_folders)} 个文件夹, {total_files} 个文件\n")
        
        # 滚动到开头
        self.result_text.see("1.0")
        
        # 显示完成消息
        messagebox.showinfo("完成", f"共找到 {total_files} 个文件")

    def save_results(self):
        """保存结果到文件"""
        content = self.result_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("成功", "文件保存成功！")
    
    def execute_rename(self):
        """执行批量重命名"""
        target_folder = self.target_folder.get()
        if not target_folder:
            messagebox.showwarning("警告", "请选择目标文件夹！")
            return
            
        rules_text = self.rule_text.get('1.0', tk.END).strip()
        if not rules_text:
            messagebox.showwarning("警告", "请输入重命名规则！")
            return
            
        # 解析规则
        rules = {}
        for line in rules_text.split('\n'):
            if line.strip():
                parts = re.split(r'\s+', line.strip(), maxsplit=1)
                if len(parts) == 2:
                    old_name, new_name = parts
                    rules[old_name] = new_name
        
        if not rules:
            messagebox.showwarning("警告", "未找到有效的重命名规则！")
            return
            
        # 执行重命名
        success_count = 0
        errors = []
        
        for old_name, new_name in rules.items():
            old_path = os.path.join(target_folder, old_name)
            new_path = os.path.join(target_folder, new_name)
            
            try:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    success_count += 1
                else:
                    errors.append(f"文件不存在: {old_name}")
            except Exception as e:
                errors.append(f"重命名失败 {old_name}: {str(e)}")
        
        # 显示结果
        result_message = f"成功重命名 {success_count} 个文件\n"
        if errors:
            result_message += "\n失败项目：\n" + "\n".join(errors)
        
        messagebox.showinfo("完成", result_message)

    def create_extract_window(self):
        """创建批量提取窗口"""
        dialog = tk.Toplevel(self)
        dialog.title("批量文件提取")
        dialog.geometry("600x500")
        dialog.transient(self)
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择区域
        source_frame = ttk.LabelFrame(main_frame, text="源文件夹", padding=5)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_folder = tk.StringVar()
        ttk.Label(source_frame, textvariable=self.source_folder,
                 text="未选择文件夹").pack(side=tk.LEFT, padx=5)
        ttk.Button(source_frame, text="选择文件夹",
                  command=lambda: self.select_extract_source(dialog)).pack(side=tk.LEFT, padx=2)
        
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
        self.use_regex = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="使用正则表达式", 
                        variable=self.use_regex).pack(anchor=tk.W, padx=5)
        
        # 目标文件夹选择区域
        target_frame = ttk.LabelFrame(main_frame, text="存放目录", padding=5)
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.target_extract_folder = tk.StringVar()
        ttk.Label(target_frame, textvariable=self.target_extract_folder,
                 text="未选择目录").pack(side=tk.LEFT, padx=5)
        ttk.Button(target_frame, text="选择存放目录",
                  command=lambda: self.select_extract_target(dialog)).pack(side=tk.LEFT, padx=2)
        
        # 在源文件夹创建目录选项
        self.create_in_source = tk.BooleanVar(value=True)
        ttk.Checkbutton(target_frame, text="于源文件处创建根目录", 
                        variable=self.create_in_source,
                        command=self.toggle_target_selection).pack(anchor=tk.W, padx=5)
        
        # 在筛选条件区域下方添加操作模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="操作模式", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.extract_mode = tk.StringVar(value="move")
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
                  command=lambda: self.reset_extract_form(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def select_extract_source(self, parent):
        """选择源文件夹"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            self.source_folder.set(folder)
            if self.create_in_source.get():
                self.update_extract_target_folder()

    def select_extract_target(self, parent):
        """选择目标文件夹"""
        folder = filedialog.askdirectory(parent=parent)
        if folder:
            self.target_extract_folder.set(folder)

    def toggle_target_selection(self):
        """切换目标文件夹选择方式"""
        if self.create_in_source.get():
            self.update_extract_target_folder()
        else:
            self.target_extract_folder.set("未选择目录")

    def update_extract_target_folder(self):
        """更新目标文件夹路径"""
        source = self.source_folder.get()
        if source and self.create_in_source.get():
            timestamp = time.strftime("%Y-%m-%d %H%M")
            target = os.path.join(source, f"【文件提取结果】{timestamp}")
            self.target_extract_folder.set(target)

    def reset_extract_form(self, dialog):
        """重置表单"""
        self.source_folder.set("未选择文件夹")
        self.target_extract_folder.set("未选择目录")
        self.pattern_entry.delete(0, tk.END)
        self.use_regex.set(False)
        self.create_in_source.set(True)
        self.extract_mode.set("move")  # 重置为默认移动模式

    def execute_extract(self):
        """执行文件提取"""
        source = self.source_folder.get()
        target = self.target_extract_folder.get()
        pattern = self.pattern_entry.get().strip()
        
        if not source or source == "未选择文件夹":
            messagebox.showwarning("警告", "请选择源文件夹！")
            return
        
        if not target or target == "未选择目录":
            messagebox.showwarning("警告", "请选择存放目录！")
            return
        
        if not pattern:
            messagebox.showwarning("警告", "请输入文件类型/名称筛选条件！")
            return
        
        try:
            # 创建目标文件夹
            os.makedirs(target, exist_ok=True)
            
            # 收集符合条件的文件
            matched_files = []
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 根据选择的匹配方式进行匹配
                    if self.use_regex.get():
                        if re.search(pattern, file):
                            matched_files.append(file_path)
                    else:
                        if fnmatch.fnmatch(file, pattern):
                            matched_files.append(file_path)
        
            if not matched_files:
                messagebox.showinfo("提示", "未找到符合条件的文件！")
                return
            
            # 执行操作
            success_count = 0
            errors = []
            operation = "移动" if self.extract_mode.get() == "move" else "复制"
            
            for file_path in matched_files:
                try:
                    file_name = os.path.basename(file_path)
                    file_base, file_ext = os.path.splitext(file_name)
                    target_path = os.path.join(target, file_name)
                    
                    # 如果目标文件已存在，重命名文件
                    if os.path.exists(target_path):
                        folder_name = os.path.basename(os.path.dirname(file_path))
                        mod_time = time.strftime("%Y%m%d%H%M", 
                                               time.localtime(os.path.getmtime(file_path)))
                        new_name = f"{file_base} - {folder_name} - 修改时间{mod_time}{file_ext}"
                        target_path = os.path.join(target, new_name)
                    
                    # 根据选择的模式执行操作
                    if self.extract_mode.get() == "move":
                        shutil.move(file_path, target_path)
                    else:
                        shutil.copy2(file_path, target_path)  # copy2保留元数据
                    success_count += 1
                except Exception as e:
                    errors.append(f"{operation}失败 {os.path.basename(file_path)}: {str(e)}")
        
            # 显示结果
            result = f"成功{operation} {success_count} 个文件到目标文件夹"
            if errors:
                result += "\n\n失败项目：\n" + "\n".join(errors)
            
            if success_count > 0:
                answer = messagebox.askyesno("完成", f"{result}\n\n是否打开目标文件夹？")
                if answer:
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(target)
                        else:  # macOS/Linux
                            subprocess.Popen(['open', target] if sys.platform == 'darwin' 
                                           else ['xdg-open', target])
                    except Exception as e:
                        messagebox.showerror("错误", f"打开文件夹失败：{str(e)}")
            else:
                messagebox.showinfo("完成", result)
        
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错：\n{str(e)}")

    def open_folder(self, path):
        """跨平台打开文件夹"""
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', path])
            elif sys.platform == 'win32':  # Windows
                os.startfile(path)
            else:  # Linux
                subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹：{str(e)}")