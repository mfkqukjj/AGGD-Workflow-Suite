import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import datetime
import subprocess
import math  # 导入math模块用于向上取整

class FileSplitDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("文件分切")
        self.geometry("500x250")
        self.grab_set()
        self.files = []
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="请选择要分切的文件（可多选）：").pack(anchor="w")
        ttk.Button(frm, text="浏览", command=self.select_files).pack(anchor="w", pady=5)

        frm2 = ttk.Frame(frm)
        frm2.pack(fill=tk.X, pady=10)
        ttk.Label(frm2, text="分切后单文件大小（MB）：").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="80")
        ttk.Entry(frm2, textvariable=self.size_var, width=8).pack(side=tk.LEFT)

        ttk.Button(frm, text="开始分切", command=self.split_files).pack(pady=15)

    def select_files(self):
        filetypes = [("数据文件", "*.csv *.txt *.xls *.xlsx"), ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(title="选择文件", filetypes=filetypes)
        if files:
            self.files = files
            messagebox.showinfo("已选择", f"共选择{len(files)}个文件")

    def split_files(self):
        if not self.files:
            messagebox.showerror("错误", "请先选择文件")
            return
        try:
            size_mb = float(self.size_var.get())
            if size_mb <= 0:
                raise ValueError
        except:
            messagebox.showerror("错误", "请输入有效的分切大小")
            return

        result_dirs = []
        for src in self.files:
            try:
                ext = os.path.splitext(src)[1].lower()
                if ext in ('.xls', '.xlsx'):
                    df = pd.read_excel(src, dtype=str)
                elif ext == '.csv':
                    df = pd.read_csv(src, dtype=str, encoding='utf-8')
                elif ext == '.txt':
                    df = pd.read_csv(src, sep=None, engine='python', dtype=str, encoding='utf-8')
                else:
                    continue

                # 获取源文件大小（字节）
                src_size = os.path.getsize(src)
                total_rows = len(df)
                
                # 计算目标分片数（向上取整）
                target_parts = max(1, math.ceil(src_size / (size_mb * 1024 * 1024)))
                
                # 计算每个文件的目标大小（总大小/份数）
                target_size_per_file = src_size / target_parts
                
                # 计算平均每行字节数
                avg_bytes_per_row = src_size / total_rows
                
                # 计算每份应该包含的行数（向上取整）
                rows_per_file = math.ceil(target_size_per_file / avg_bytes_per_row)

                # 结果文件夹加时间戳
                base_dir = os.path.dirname(src)
                base_name = os.path.splitext(os.path.basename(src))[0]
                now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                out_dir = os.path.join(base_dir, f"{base_name}_文件分切结果_{now_str}")
                os.makedirs(out_dir, exist_ok=True)
                result_dirs.append(out_dir)

                # 计算实际分片数（基于行数）
                actual_parts = math.ceil(total_rows / rows_per_file)
                
                for i in range(actual_parts):
                    start = i * rows_per_file
                    end = min((i + 1) * rows_per_file, total_rows)
                    part = df.iloc[start:end]
                    out_path = os.path.join(out_dir, f"{base_name}_part{i+1}{ext}")
                    
                    if ext in ('.xls', '.xlsx'):
                        part.to_excel(out_path, index=False)
                    elif ext == '.csv':
                        part.to_csv(out_path, index=False, encoding='utf-8')
                    elif ext == '.txt':
                        part.to_csv(out_path, index=False, sep='\t', encoding='utf-8')
                
                messagebox.showinfo("分切完成", 
                                   f"{os.path.basename(src)} 已分切到 {out_dir}\n"
                                   f"源文件大小: {src_size/(1024*1024):.2f}MB\n"
                                   f"目标大小: {size_mb}MB/文件\n"
                                   f"分切份数: {actual_parts}\n"
                                   f"每份大小: {target_size_per_file/(1024*1024):.2f}MB")
            except Exception as e:
                messagebox.showerror("分切失败", f"{os.path.basename(src)}: {e}")

        # 分切全部完成后，询问是否打开结果目录
        if result_dirs:
            if messagebox.askyesno("完成", "所有文件分切完成，是否打开结果文件夹？"):
                # 打开第一个结果目录
                try:
                    os.startfile(result_dirs[0])
                except Exception:
                    # 兼容Linux/Mac
                    try:
                        subprocess.Popen(['open', result_dirs[0]])
                    except Exception:
                        try:
                            subprocess.Popen(['xdg-open', result_dirs[0]])
                        except Exception:
                            messagebox.showinfo("提示", f"请手动打开目录：{result_dirs[0]}")