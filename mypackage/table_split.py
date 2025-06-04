import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import threading
import re

class TableSplitter(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("自动分表工具")
        self.geometry("900x700")
        self.transient(master)
        self.grab_set()
        
        # 初始化变量
        self.input_files = []
        self.output_dir = ""
        self.split_mode = tk.StringVar(value="row")
        self.output_format = tk.StringVar(value="source")
        self.rows_per_file = tk.StringVar(value="1000")
        self.split_column = tk.StringVar()
        self.folder_mode = tk.StringVar(value="unified")
        self.available_columns = []
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 输入文件选择区域
        input_frame = ttk.LabelFrame(main_frame, text="1. 选择输入文件", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(input_frame, text="选择文件", 
                  command=self.select_files).pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(input_frame, text="未选择文件")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 2. 拆分设置区域
        split_frame = ttk.LabelFrame(main_frame, text="2. 拆分设置", padding="5")
        split_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 拆分模式选择
        mode_frame = ttk.Frame(split_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mode_frame, text="拆分方式：").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="按行数拆分", variable=self.split_mode,
                       value="row", command=self.update_split_options).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="按字段拆分", variable=self.split_mode,
                       value="column", command=self.update_split_options).pack(side=tk.LEFT)
        
        # 拆分参数设置
        self.split_options_frame = ttk.Frame(split_frame)
        self.split_options_frame.pack(fill=tk.X, pady=5)
        self.update_split_options()
        
        # 3. 输出设置区域
        output_frame = ttk.LabelFrame(main_frame, text="3. 输出设置", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输出格式选择
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="输出格式：").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="与源文件一致", variable=self.output_format,
                       value="source").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="Excel", variable=self.output_format,
                       value="excel").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="CSV", variable=self.output_format,
                       value="csv").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="TXT", variable=self.output_format,
                       value="txt").pack(side=tk.LEFT)
        
        # 文件夹组织方式
        folder_frame = ttk.Frame(output_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        ttk.Label(folder_frame, text="存放方式：").pack(side=tk.LEFT)
        ttk.Radiobutton(folder_frame, text="统一存放", variable=self.folder_mode,
                       value="unified").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(folder_frame, text="按源文件分开存放", variable=self.folder_mode,
                       value="separate").pack(side=tk.LEFT)
        
        # 输出目录选择
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Button(dir_frame, text="选择输出目录", 
                  command=self.select_output_dir).pack(side=tk.LEFT, padx=5)
        self.dir_label = ttk.Label(dir_frame, text="默认使用源文件目录")
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 4. 进度显示
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", 
                                      length=200, mode="determinate")
        self.progress.pack(fill=tk.X, pady=10)
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X)
        
        # 5. 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="开始拆分", 
                  command=self.start_split).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT)
        
    def select_files(self):
        """选择输入文件"""
        files = filedialog.askopenfilenames(
            filetypes=[("表格文件", "*.xlsx *.xls *.csv *.txt"),
                      ("Excel文件", "*.xlsx *.xls"),
                      ("CSV文件", "*.csv"),
                      ("文本文件", "*.txt")]
        )
        if files:
            self.input_files = files
            self.file_label.config(text=f"已选择 {len(files)} 个文件")
            # 读取第一个文件的列名
            self.load_columns(files[0])
            
    def load_columns(self, file_path):
        """读取文件列名"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            self.available_columns = df.columns.tolist()
            self.update_split_options()
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{str(e)}")
            
    def update_split_options(self):
        """更新拆分选项"""
        # 清除现有选项
        for widget in self.split_options_frame.winfo_children():
            widget.destroy()
            
        if self.split_mode.get() == "row":
            ttk.Label(self.split_options_frame, 
                     text="每个文件行数：").pack(side=tk.LEFT)
            ttk.Entry(self.split_options_frame, 
                     textvariable=self.rows_per_file,
                     width=10).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Label(self.split_options_frame, 
                     text="拆分字段：").pack(side=tk.LEFT)
            combo = ttk.Combobox(self.split_options_frame, 
                               textvariable=self.split_column,
                               values=self.available_columns,
                               width=20)
            combo.pack(side=tk.LEFT, padx=5)
            if self.available_columns:
                combo.set(self.available_columns[0])
                
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.dir_label.config(text=dir_path)
            
    def start_split(self):
        """开始拆分处理"""
        if not self.input_files:
            messagebox.showwarning("警告", "请先选择输入文件！")
            return
        
        # 在新线程中执行拆分
        threading.Thread(target=self.run_split, daemon=True).start()
        
    def clean_filename(self, filename):
        """清理文件名中的非法字符"""
        # 替换 Windows 和 Unix 系统都不允许的字符
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        clean_name = re.sub(invalid_chars, '_', str(filename))
        # 处理首尾空格和点
        clean_name = clean_name.strip('. ')
        # 如果文件名为空，使用默认名称
        return clean_name or 'unnamed'
        
    def run_split(self):
        """执行拆分操作"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            base_output_dir = self.output_dir or os.path.dirname(self.input_files[0])
            result_dir = os.path.join(base_output_dir, f"文件拆分结果-{timestamp}")
            
            total_files = len(self.input_files)
            self.progress["maximum"] = total_files
            self.progress["value"] = 0
            
            for idx, file_path in enumerate(self.input_files, 1):
                self.status_var.set(f"处理文件 {idx}/{total_files}: {os.path.basename(file_path)}")
                
                # 确定输出目录
                if self.folder_mode.get() == "separate":
                    file_output_dir = os.path.join(result_dir, 
                                                 os.path.splitext(os.path.basename(file_path))[0])
                else:
                    file_output_dir = result_dir
                    
                os.makedirs(file_output_dir, exist_ok=True)
                
                # 读取文件
                df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                
                # 执行拆分
                if self.split_mode.get() == "row":
                    chunks = self.split_by_rows(df)
                else:
                    chunks = self.split_by_column(df)
                
                # 保存拆分结果
                for i, chunk in enumerate(chunks, 1):
                    if self.split_mode.get() == "row":
                        # 按行拆分时使用 part 编号
                        output_name = f"{os.path.splitext(os.path.basename(file_path))[0]}-part{i}"
                    else:
                        # 按字段拆分时使用字段值
                        column = self.split_column.get()
                        key_value = chunk[column].iloc[0]  # 获取该分组的关键字值
                        clean_key = self.clean_filename(key_value)  # 清理关键字中的非法字符
                        output_name = f"{os.path.splitext(os.path.basename(file_path))[0]}-{clean_key}"
                    
                    if self.folder_mode.get() == "unified":
                        output_name = f"{timestamp}-{output_name}"
                    
                    self.save_chunk(chunk, file_output_dir, output_name)
                
                self.progress["value"] = idx
                
            self.status_var.set("拆分完成！")
            messagebox.showinfo("完成", f"文件拆分完成！\n输出目录：{result_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"拆分过程出错：{str(e)}")
            self.status_var.set("处理失败")
            
    def split_by_rows(self, df):
        """按行数拆分"""
        chunk_size = int(self.rows_per_file.get())
        return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        
    def split_by_column(self, df):
        """按字段拆分"""
        column = self.split_column.get()
        return [group for _, group in df.groupby(column)]
        
    def save_chunk(self, df, output_dir, name):
        """保存数据块"""
        if self.output_format.get() == "csv":
            df.to_csv(os.path.join(output_dir, f"{name}.csv"), index=False)
        elif self.output_format.get() == "txt":
            df.to_csv(os.path.join(output_dir, f"{name}.txt"), 
                     index=False, sep='\t')
        else:  # excel or source
            df.to_excel(os.path.join(output_dir, f"{name}.xlsx"), 
                       index=False)