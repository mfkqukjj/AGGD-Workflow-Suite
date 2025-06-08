import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import glob
import re

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
            ("批量修改文件名", self.create_rename_window)
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

    # 添加清除方法
    def clear_folders(self):
        """清除已选择的文件夹"""
        self.selected_folders = []
        self.folder_label.config(text="已选择文件夹：0")
        messagebox.showinfo("提示", "已清除所有选择的文件夹")
    
    def copy_results(self):
        """复制结果到剪贴板"""
        content = self.result_text.get('1.0', tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("成功", "结果已复制到剪贴板！")
        else:
            messagebox.showwarning("警告", "没有可复制的内容！")
    
    def read_current_files(self):
        """读取当前选择文件夹中的文件名"""
        folder = self.target_folder.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择目标文件夹！")
            return
        
        try:
            # 获取文件列表
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    # 排除临时文件
                    if not (filename.startswith('~') or 
                           filename.startswith('.') or 
                           filename.endswith('.tmp') or 
                           filename.endswith('.temp') or 
                           '~$' in filename):
                        # 获取相对路径
                        rel_path = os.path.relpath(os.path.join(root, filename), folder)
                        files.append(rel_path)
            
            # 清空并显示结果
            self.preview_text.delete('1.0', tk.END)
            
            # 按文件夹层级显示
            current_folder = ""
            for file_path in sorted(files):
                folder_path = os.path.dirname(file_path)
                if folder_path and folder_path != current_folder:
                    current_folder = folder_path
                    self.preview_text.insert(tk.END, f"\n[{folder_path}]\n")
                
                file_name = os.path.basename(file_path)
                indent = "    " if folder_path else ""
                self.preview_text.insert(tk.END, f"{indent}{file_name}\n")
            
            messagebox.showinfo("完成", f"成功读取 {len(files)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件列表时出错：\n{str(e)}")

    def copy_results(self, text_widget):
        """复制文本框内容到剪贴板"""
        content = text_widget.get('1.0', tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("成功", "内容已复制到剪贴板！")
        else:
            messagebox.showwarning("警告", "没有可复制的内容！")