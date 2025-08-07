# registration_merger.py
import os
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import platform

class RegistrationMerger(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("注册信息合并工具")
        self.geometry("600x600")
        self.transient(master)
        self.grab_set()
        
        # 变量初始化
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.use_source_dir = tk.BooleanVar(value=True)
        self.processed_files = 0
        self.master = master
        
        # 创建UI
        self.create_widgets()
    
    def create_widgets(self):
        # 输入文件/目录选择
        input_frame = ttk.LabelFrame(self, text="输入选择", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(input_frame, text="选择文件(多选)", command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="选择目录", command=self.select_directory).pack(side=tk.LEFT, padx=5)
        
        # 输入文件列表
        self.file_listbox = tk.Listbox(self, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 输出设置
        output_frame = ttk.LabelFrame(self, text="输出设置", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(output_frame, text="使用源文件目录", variable=self.use_source_dir, 
                       command=self.toggle_output_dir).pack(anchor=tk.W)
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="输出目录:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir, width=40)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="浏览...", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # 进度条
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, expand=True)
        self.status_label = ttk.Label(progress_frame, text="（适用于腾讯调证反馈注册信息等纵向txt合并为csv，以英文:分隔字段名和内容）")
        self.status_label.pack(pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="开始合并", command=self.start_merge).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_list).pack(side=tk.RIGHT, padx=5)
        
        # 关闭按钮
        #ttk.Button(self, text="关闭", command=self.destroy).pack(side=tk.BOTTOM, pady=10)
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择TXT文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if files:
            self.input_files = list(files)
            self.update_file_list()
            if self.use_source_dir.get() and self.input_files:
                common_dir = os.path.commonpath(self.input_files)
                self.output_dir.set(common_dir)
            self.update_status(f"已选择 {len(self.input_files)} 个文件")
    
    def select_directory(self):
        directory = filedialog.askdirectory(title="选择包含TXT文件的目录")
        if directory:
            self.input_files = [
                os.path.join(directory, f) 
                for f in os.listdir(directory) 
                if f.lower().endswith('.txt')
            ]
            self.update_file_list()
            if self.use_source_dir.get() and directory:
                self.output_dir.set(directory)
            self.update_status(f"已从目录添加 {len(self.input_files)} 个文件")
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
            self.use_source_dir.set(False)
            self.update_status(f"输出目录设置为: {directory}")
    
    def toggle_output_dir(self):
        if self.use_source_dir.get() and self.input_files:
            common_dir = os.path.commonpath(self.input_files)
            self.output_dir.set(common_dir)
            self.update_status(f"输出目录设置为源目录: {common_dir}")
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.input_files:
            # 只显示文件名，不显示完整路径（节省空间）
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def clear_list(self):
        self.input_files = []
        self.file_listbox.delete(0, tk.END)
        self.output_dir.set("")
        self.progress['value'] = 0
        self.update_status("已清空文件列表")
    
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.update_idletasks()
    
    def process_txt_file(self, file_path):
        """处理单个TXT文件，返回转置后的字典"""
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        # 如果键已有值，则追加
                        if key in data:
                            data[key] = data[key] + "; " + value.strip()
                        else:
                            data[key] = value.strip()
            
            self.processed_files += 1
            progress_value = (self.processed_files / len(self.input_files)) * 100
            self.progress['value'] = progress_value
            self.update_status(f"处理中: {self.processed_files}/{len(self.input_files)} ({progress_value:.1f}%)")
            self.update_idletasks()
            
            return data
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            self.update_status(f"处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
            return None

    def open_output_dir(self, output_dir):
        """打开输出目录"""
        try:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", output_dir])
            else:
                subprocess.Popen(["xdg-open", output_dir])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录:\n{e}")

    def start_merge(self):
        if not self.input_files:
            messagebox.showwarning("警告", "请先选择输入文件或目录！")
            return
        
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录！")
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.update_status(f"已创建输出目录: {output_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录:\n{e}")
                return
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = os.path.join(output_dir, f'merged_registration_{current_time}.csv')
        
        self.processed_files = 0
        self.progress['value'] = 0
        self.update_status("开始处理文件...")
        
        all_data = []
        for file_path in self.input_files:
            file_data = self.process_txt_file(file_path)
            if file_data:
                # 添加文件名信息
                file_data["来源文件"] = os.path.basename(file_path)
                all_data.append(file_data)
        
        if all_data:
            try:
                df = pd.DataFrame(all_data)
                # 将来源文件列移动到第一列
                cols = df.columns.tolist()
                cols.insert(0, cols.pop(cols.index("来源文件")))
                df = df[cols]
                
                df.to_csv(output_csv, index=False, encoding='utf-8-sig')
                
                self.update_status(f"成功合并 {len(all_data)} 个文件到: {output_csv}")
                
                # 询问是否打开输出目录
                if messagebox.askyesno("完成", 
                                      f"成功合并 {len(all_data)} 个文件到:\n{output_csv}\n\n是否打开输出目录？"):
                    self.open_output_dir(output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"保存CSV文件时出错:\n{e}")
                self.update_status(f"保存失败: {str(e)}")
        else:
            messagebox.showwarning("警告", "没有有效数据可保存！")
            self.update_status("处理完成，但没有有效数据")
        
        self.progress['value'] = 100