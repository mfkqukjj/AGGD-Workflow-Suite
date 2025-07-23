import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import datetime
import threading
import subprocess

class FileFormatConvertDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("文件格式转换")
        self.geometry("540x340")
        self.grab_set()
        self.result_dir = tk.StringVar()
        self.use_src_subdir = tk.BooleanVar(value=True)
        self.selected_files = []  # 存储多个文件路径
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        # 选择文件
        ttk.Label(frm, text="请选择要转换的文件（可多选）：").pack(anchor="w")
        filefrm = ttk.Frame(frm)
        filefrm.pack(fill=tk.X, pady=2)
        self.file_entry = ttk.Entry(filefrm, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(filefrm, text="浏览", command=self.select_file).pack(side=tk.LEFT, padx=5)

        # 选择结果目录
        ttk.Label(frm, text="选择结果文件生成目录：").pack(anchor="w", pady=(10,0))
        dirfrm = ttk.Frame(frm)
        dirfrm.pack(fill=tk.X, pady=2)
        self.dir_entry = ttk.Entry(dirfrm, textvariable=self.result_dir, width=40)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dirfrm, text="浏览", command=self.select_dir).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(frm, text="在源文件目录自动生成子目录", variable=self.use_src_subdir, command=self.toggle_dir_entry).pack(anchor="w", pady=(2,8))

        # 目标格式
        frm2 = ttk.Frame(frm)
        frm2.pack(fill=tk.X, pady=10)
        ttk.Label(frm2, text="目标格式：").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="excel")
        ttk.Radiobutton(frm2, text="Excel", variable=self.format_var, value="excel").pack(side=tk.LEFT)
        ttk.Radiobutton(frm2, text="CSV", variable=self.format_var, value="csv").pack(side=tk.LEFT)
        ttk.Radiobutton(frm2, text="TXT", variable=self.format_var, value="txt").pack(side=tk.LEFT)

        # 进度条
        self.progress = ttk.Progressbar(frm, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # 转换按钮
        ttk.Button(frm, text="开始转换", command=self.start_convert).pack(pady=8)

    def toggle_dir_entry(self):
        if self.use_src_subdir.get():
            self.dir_entry.configure(state='disabled')
        else:
            self.dir_entry.configure(state='normal')

    def select_file(self):
        filetypes = [("数据文件", "*.csv *.txt *.xls *.xlsx"), ("所有文件", "*.*")]
        filenames = filedialog.askopenfilenames(title="选择文件", filetypes=filetypes)
        if filenames:
            self.selected_files = list(filenames)
            self.file_entry.delete(0, tk.END)
            # 显示选中的文件数量
            self.file_entry.insert(0, f"已选择 {len(self.selected_files)} 个文件")
            # 如果选择了多个文件，则禁用自动子目录选项
            if len(self.selected_files) > 1:
                self.use_src_subdir.set(False)
                self.toggle_dir_entry()  # 更新目录输入框状态
            else:
                # 单个文件保持原逻辑
                if self.use_src_subdir.get():
                    src_dir = os.path.dirname(self.selected_files[0])
                    now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                    subdir = os.path.join(src_dir, f"格式转换结果_{now_str}")
                    self.result_dir.set(subdir)

    def select_dir(self):
        dirname = filedialog.askdirectory(title="选择结果目录")
        if dirname:
            self.result_dir.set(dirname)

    def start_convert(self):
        # 禁用按钮，防止重复点击
        self.progress["value"] = 0
        self.update_idletasks()
        threading.Thread(target=self.convert, daemon=True).start()

    def convert(self):
        if not self.selected_files:
            messagebox.showerror("错误", "请选择有效的文件")
            return

        target_fmt = self.format_var.get()
        # 结果目录处理
        if self.use_src_subdir.get() and len(self.selected_files) == 1:
            # 单个文件使用源目录子目录
            result_dir = self.result_dir.get()
            if not os.path.exists(result_dir):
                os.makedirs(result_dir, exist_ok=True)
        else:
            # 批量文件必须指定结果目录
            result_dir = self.result_dir.get()
            if not result_dir or not os.path.exists(result_dir):
                messagebox.showerror("错误", "请选择有效的结果目录")
                return

        total_files = len(self.selected_files)
        success_count = 0
        error_messages = []
        step = 100 / total_files if total_files > 0 else 100
        current_progress = 0

        for i, src in enumerate(self.selected_files):
            try:
                if not os.path.exists(src):
                    error_messages.append(f"文件不存在: {src}")
                    continue

                # 读取数据
                if src.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(src, dtype=str)
                elif src.endswith('.csv'):
                    df = pd.read_csv(src, dtype=str, encoding='utf-8')
                elif src.endswith('.txt'):
                    df = pd.read_csv(src, sep=None, engine='python', dtype=str, encoding='utf-8')
                else:
                    error_messages.append(f"不支持的文件格式: {src}")
                    continue
                
                # 所有列强制为文本
                for col in df.columns:
                    df[col] = df[col].astype(str)

                # 生成目标文件名
                base_name = os.path.splitext(os.path.basename(src))[0]
                ext_map = {"excel": ".xlsx", "csv": ".csv", "txt": ".txt"}
                out_path = os.path.join(result_dir, base_name + ext_map[target_fmt])

                # 保存文件
                if target_fmt == "excel":
                    df.to_excel(out_path, index=False)
                elif target_fmt == "csv":
                    df.to_csv(out_path, index=False, encoding='utf-8')
                elif target_fmt == "txt":
                    df.to_csv(out_path, index=False, sep='\t', encoding='utf-8')

                success_count += 1
            except Exception as e:
                error_messages.append(f"转换失败 {os.path.basename(src)}: {str(e)}")
            
            # 更新进度
            current_progress += step
            self.progress["value"] = current_progress
            self.update_idletasks()

        # 完成处理
        self.progress["value"] = 100
        self.update_idletasks()
        
        if error_messages:
            error_report = "\n".join(error_messages)
            messagebox.showerror(
                "部分文件转换失败", 
                f"成功转换: {success_count}/{total_files} 个文件\n\n失败详情:\n{error_report}"
            )
        else:
            messagebox.showinfo("成功", f"全部 {total_files} 个文件转换成功")
        
        # 完成后询问是否打开目录
        if success_count > 0 and messagebox.askyesno("完成", "是否打开结果目录？"):
            try:
                os.startfile(result_dir)
            except Exception:
                try:
                    subprocess.Popen(['open', result_dir])
                except Exception:
                    try:
                        subprocess.Popen(['xdg-open', result_dir])
                    except Exception:
                        messagebox.showinfo("提示", f"请手动打开目录：{result_dir}")
        
        # 重置进度条
