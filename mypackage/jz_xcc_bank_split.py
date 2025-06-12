import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import subprocess
import time
from datetime import datetime

class TableBankSplitter(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("财务表格分表工具")
        self.geometry("800x600")
        self.transient(master)
        self.grab_set()
        
        # 初始化变量
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.use_source_dir = tk.BooleanVar(value=True)
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 输入文件选择
        input_frame = ttk.LabelFrame(main_frame, text="1. 选择输入文件", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(input_frame, textvariable=self.input_file,
                 width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="浏览",
                  command=self.select_input_file).pack(side=tk.LEFT)
        
        # 2. 输出设置
        output_frame = ttk.LabelFrame(main_frame, text="2. 输出设置", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 在源文件夹创建选项
        ttk.Checkbutton(output_frame, text="在源文件位置创建输出文件夹",
                       variable=self.use_source_dir,
                       command=self.toggle_output_dir).pack(anchor=tk.W, pady=5)
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)
        self.output_entry = ttk.Entry(output_path_frame,
                                    textvariable=self.output_dir, width=60)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        self.browse_btn = ttk.Button(output_path_frame, text="浏览",
                                   command=self.select_output_dir)
        self.browse_btn.pack(side=tk.LEFT)
        
        # 3. 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        ttk.Button(btn_frame, text="开始处理",
                  command=self.start_split).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭",
                  command=self.destroy).pack(side=tk.LEFT)
        
        # 4. 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).pack(fill=tk.X)
    
    def select_input_file(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xls *.xlsx")]
        )
        if file_path:
            self.input_file.set(file_path)
            if self.use_source_dir.get():
                self.update_output_dir()
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
    
    def toggle_output_dir(self):
        """切换输出目录选择"""
        if self.use_source_dir.get():
            self.output_entry.configure(state='disabled')
            self.browse_btn.configure(state='disabled')
            self.update_output_dir()
        else:
            self.output_entry.configure(state='normal')
            self.browse_btn.configure(state='normal')
    
    def update_output_dir(self):
        """更新输出目录"""
        if self.input_file.get():
            # 生成时间戳文件夹名
            timestamp = datetime.now().strftime('%Y%m%d-%H%M')
            folder_name = f"输出结果-{timestamp}"
            
            output_dir = os.path.join(
                os.path.dirname(self.input_file.get()),
                folder_name
            )
            self.output_dir.set(output_dir)
    
    def start_split(self):
        """开始处理"""
        if not self.input_file.get():
            messagebox.showwarning("警告", "请先选择输入文件！")
            return
            
        try:
            # 创建输出目录
            output_dir = self.output_dir.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # 读取Excel文件
            df = pd.read_excel(self.input_file.get(), header=1)
            original_title = pd.read_excel(self.input_file.get(), nrows=1).iloc[0, 0]
            
            # 获取唯一银行列表
            banks = df['所属银行'].unique()
            
            # 处理每个银行的数据
            for bank in banks:
                self.status_var.set(f"正在处理: {bank}")
                self.update()
                
                # 过滤并复制该银行的数据
                bank_df = df[df['所属银行'] == bank].copy()
                
                # 重置序号列（第一列）
                bank_df.iloc[:, 0] = range(1, len(bank_df) + 1)
                
                # 删除所属银行列
                bank_df = bank_df.drop('所属银行', axis=1)
                
                # 保存文件
                output_file = os.path.join(output_dir, f"附表-{bank}.xls")
                
                with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                    # 写入数据（但不包含表头）
                    bank_df.to_excel(writer, index=False, sheet_name='Sheet1', startrow=1, header=False)
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    
                    # 设置格式
                    formats = self.create_formats(workbook)
                    
                    # 写入标题（修改为"附表-银行名"格式）
                    new_title = f"附表-{bank}"
                    worksheet.merge_range(0, 0, 0, len(bank_df.columns)-1, new_title, formats['title'])
                    
                    # 写入表头
                    for col, value in enumerate(bank_df.columns):
                        worksheet.write(1, col, value, formats['header'])
                    
                    # 写入数据
                    for row in range(2, len(bank_df)+2):
                        for col in range(len(bank_df.columns)):
                            value = bank_df.iloc[row-2, col]
                            format_key = f'col_{chr(65+col)}'  # A, B, C, D
                            worksheet.write(row, col, value, formats[format_key])
                    
                    # 设置行高
                    worksheet.set_row(0, 31)  # 第一行高度31
                    for i in range(1, len(bank_df)+2):
                        worksheet.set_row(i, 30)  # 其他行高度30
                    
                    # 其他设置
                    worksheet.set_column('A:A', 12.68)
                    worksheet.set_column('B:B', 22.13)
                    worksheet.set_column('C:C', 19.5)
                    worksheet.set_column('D:D', 31)
                    
                    # 设置页脚
                    worksheet.set_footer('&R第 &P 页，共 &N 页')
                    worksheet.repeat_rows(1)
                
            self.status_var.set("处理完成！")
            
            # 询问是否打开输出文件夹
            if messagebox.askyesno("完成", "处理完成！是否打开输出文件夹？"):
                self.open_output_folder()
                
        except Exception as e:
            messagebox.showerror("错误", f"处理过程出错：{str(e)}")
            self.status_var.set("处理失败")
    
    def create_formats(self, workbook):
        """创建Excel格式"""
        return {
            'title': workbook.add_format({
                'font_name': '宋体', 'font_size': 18, 'bold': True,
                'align': 'left', 'valign': 'vcenter'
            }),
            'header': workbook.add_format({
                'font_name': '宋体', 'font_size': 12, 'bold': True,
                'align': 'center', 'valign': 'vcenter', 'border': 1
            }),
            'col_A': workbook.add_format({
                'font_name': '宋体', 'font_size': 11, 'bold': True,
                'align': 'center', 'valign': 'vcenter', 'border': 1
            }),
            'col_B': workbook.add_format({
                'font_name': '宋体', 'font_size': 12,
                'align': 'center', 'valign': 'vcenter', 'border': 1
            }),
            'col_C': workbook.add_format({
                'font_name': '宋体', 'font_size': 11,
                'align': 'center', 'valign': 'vcenter', 'border': 1
            }),
            'col_D': workbook.add_format({
                'font_name': '宋体', 'font_size': 13, 'bold': True,
                'align': 'center', 'valign': 'vcenter', 'border': 1
            })
        }
    
    def open_output_folder(self):
        """打开输出文件夹"""
        try:
            output_dir = os.path.abspath(self.output_dir.get())
            subprocess.run(['explorer', output_dir])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹：{str(e)}")