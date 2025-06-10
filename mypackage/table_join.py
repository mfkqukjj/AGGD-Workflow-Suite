import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class TableJoinTool(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("表间关联工具")
        self.geometry("900x700")
        
        # 保持窗口始终在最前
        self.transient(master)
        self.grab_set()
        self.focus_set()
        
        # 初始化变量
        self.left_file = tk.StringVar()
        self.right_file = tk.StringVar()
        self.save_path = tk.StringVar()
        self.use_source_dir = tk.BooleanVar(value=False)
        self.join_type = tk.StringVar(value="left")
        
        # 初始化数据相关变量
        self.left_df = None
        self.right_df = None
        self.left_columns = []
        self.right_columns = []
        
        # 初始化字段选择变量字典
        self.left_fields_vars = {}
        self.right_fields_vars = {}
        
        # 初始化连接条件列表
        self.join_conditions = []
        
        # 创建界面组件
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 左表选择
        left_frame = ttk.Frame(file_frame)
        left_frame.pack(fill=tk.X, pady=5)
        ttk.Label(left_frame, text="左表：").pack(side=tk.LEFT)
        ttk.Entry(left_frame, textvariable=self.left_file, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_frame, text="浏览", command=lambda: self.browse_file("left")).pack(side=tk.LEFT)
        
        # 右表选择
        right_frame = ttk.Frame(file_frame)
        right_frame.pack(fill=tk.X, pady=5)
        ttk.Label(right_frame, text="右表：").pack(side=tk.LEFT)
        ttk.Entry(right_frame, textvariable=self.right_file, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_frame, text="浏览", command=lambda: self.browse_file("right")).pack(side=tk.LEFT)
        
        # 字段选择区域
        fields_frame = ttk.LabelFrame(main_frame, text="字段选择", padding="5")
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 修改左表字段选择区域
        left_fields_frame = ttk.Frame(fields_frame)
        left_fields_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建左表标题行框架
        left_header = ttk.Frame(left_fields_frame)
        left_header.pack(fill=tk.X, pady=(0, 5))
        
        # 左表标题和按钮
        ttk.Label(left_header, text="左表字段", style="Dialog.TLabel").pack(side=tk.LEFT)
        ttk.Button(left_header, text="反选", style="Small.TButton",
                   command=lambda: self.invert_selection('left')).pack(side=tk.RIGHT)
        ttk.Button(left_header, text="全选", style="Small.TButton",
                   command=lambda: self.select_all('left')).pack(side=tk.RIGHT, padx=(0, 2))
        
        # 字段容器
        self.left_fields_container = ttk.Frame(left_fields_frame)
        self.left_fields_container.pack(fill=tk.BOTH, expand=True)
        
        # 修改右表字段选择区域
        right_fields_frame = ttk.Frame(fields_frame)
        right_fields_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建右表标题行框架
        right_header = ttk.Frame(right_fields_frame)
        right_header.pack(fill=tk.X, pady=(0, 5))
        
        # 右表标题和按钮
        ttk.Label(right_header, text="右表字段", style="Dialog.TLabel").pack(side=tk.LEFT)
        ttk.Button(right_header, text="反选", style="Small.TButton",
                   command=lambda: self.invert_selection('right')).pack(side=tk.RIGHT)
        ttk.Button(right_header, text="全选", style="Small.TButton",
                   command=lambda: self.select_all('right')).pack(side=tk.RIGHT, padx=(0, 2))
        
        # 字段容器
        self.right_fields_container = ttk.Frame(right_fields_frame)
        self.right_fields_container.pack(fill=tk.BOTH, expand=True)
        
        # 连接条件区域
        join_frame = ttk.LabelFrame(main_frame, text="连接设置", padding="5")
        join_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接类型选择
        join_type_frame = ttk.Frame(join_frame)
        join_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(join_type_frame, text="连接类型：").pack(side=tk.LEFT)
        ttk.Radiobutton(join_type_frame, text="左连接", variable=self.join_type, 
                       value="left").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(join_type_frame, text="右连接", variable=self.join_type, 
                       value="right").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(join_type_frame, text="内连接", variable=self.join_type, 
                       value="inner").pack(side=tk.LEFT, padx=10)
        
        # 连接条件设置
        self.conditions_frame = ttk.Frame(join_frame)
        self.conditions_frame.pack(fill=tk.X, pady=5)
        self.add_join_condition()
        ttk.Button(join_frame, text="添加条件", 
                  command=self.add_join_condition).pack(pady=5)
        
        # 保存设置区域
        save_frame = ttk.LabelFrame(main_frame, text="保存设置", padding="5")
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 保存路径选择
        save_path_frame = ttk.Frame(save_frame)
        save_path_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(save_path_frame, text="使用源文件目录", 
                       variable=self.use_source_dir).pack(side=tk.LEFT)
        ttk.Entry(save_path_frame, textvariable=self.save_path, 
                 width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_path_frame, text="浏览", 
                  command=self.browse_save_path).pack(side=tk.LEFT)
        
        # 执行按钮
        ttk.Button(main_frame, text="执行关联", 
                  command=self.execute_join).pack(pady=10)
    
    def browse_file(self, side):
        # 修改文件选择方法，确保窗口保持在最前
        self.lift()  # 将窗口提升到最前
        file_path = filedialog.askopenfilename(
            parent=self,  # 指定父窗口
            filetypes=[("Excel files", "*.xlsx *.xls")],
            title="选择Excel文件"
        )
        if file_path:
            if side == "left":
                self.left_file.set(file_path)
                self.load_columns("left")
            else:
                self.right_file.set(file_path)
                self.load_columns("right")
        self.focus_force()  # 强制获取焦点
    
    def load_columns(self, side):
        try:
            file_path = self.left_file.get() if side == "left" else self.right_file.get()
            df = pd.read_excel(file_path)
            
            if side == "left":
                self.left_df = df
                self.left_columns = df.columns.tolist()
                
                # 更新所有关联条件下拉框的值
                for condition in self.join_conditions:
                    condition['left_combo']['values'] = self.left_columns
                
                # 清除现有的字段选择框
                for widget in self.left_fields_container.winfo_children():
                    widget.destroy()
                self.left_fields_vars.clear()
                
                # 创建新的字段选择框
                for col in self.left_columns:
                    var = tk.BooleanVar(value=True)  # 默认选中
                    self.left_fields_vars[col] = var
                    ttk.Checkbutton(self.left_fields_container, 
                                   text=col, 
                                   variable=var).pack(anchor=tk.W)
            else:
                self.right_df = df
                self.right_columns = df.columns.tolist()
                
                # 更新所有关联条件下拉框的值
                for condition in self.join_conditions:
                    condition['right_combo']['values'] = self.right_columns
                
                # 清除现有的字段选择框
                for widget in self.right_fields_container.winfo_children():
                    widget.destroy()
                self.right_fields_vars.clear()
                
                # 创建新的字段选择框
                for col in self.right_columns:
                    var = tk.BooleanVar(value=True)  # 默认选中
                    self.right_fields_vars[col] = var
                    ttk.Checkbutton(self.right_fields_container, 
                                   text=col, 
                                   variable=var).pack(anchor=tk.W)
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败：{str(e)}")
    
    def add_join_condition(self):
        condition_frame = ttk.Frame(self.conditions_frame)
        condition_frame.pack(fill=tk.X, pady=2)
        
        left_combo = ttk.Combobox(condition_frame, values=self.left_columns, width=20)
        left_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(condition_frame, text="=").pack(side=tk.LEFT, padx=5)
        
        right_combo = ttk.Combobox(condition_frame, values=self.right_columns, width=20)
        right_combo.pack(side=tk.LEFT, padx=5)
        
        # 存储关联条件组件
        condition = {
            'frame': condition_frame,
            'left_combo': left_combo,
            'right_combo': right_combo
        }
        self.join_conditions.append(condition)
        
        ttk.Button(condition_frame, text="删除", 
                  command=lambda c=condition: self.remove_condition(c)).pack(side=tk.LEFT)

    def remove_condition(self, condition):
        condition['frame'].destroy()
        self.join_conditions.remove(condition)

    def browse_save_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path.set(path)
    
    def execute_join(self):
        try:
            # 检查数据表是否已加载
            if self.left_df is None or self.right_df is None:
                messagebox.showerror("错误", "请先选择两个数据表！")
                return
            
            # 检查是否有连接条件
            if not self.join_conditions:
                messagebox.showerror("错误", "请添加至少一个连接条件！")
                return
            
            # 检查连接条件是否完整
            join_conditions = []
            for condition in self.join_conditions:
                left_field = condition['left_combo'].get()
                right_field = condition['right_combo'].get()
                if not left_field or not right_field:
                    messagebox.showerror("错误", "请完整填写所有连接条件！")
                    return
                join_conditions.append((left_field, right_field))
            
            # 检查保存路径
            save_dir = self.save_path.get()
            if not self.use_source_dir.get() and not save_dir:
                messagebox.showerror("错误", "请选择保存路径或勾选使用源文件目录！")
                return
            
            # 先执行连接
            result_df = self.left_df.merge(
                self.right_df,
                left_on=[cond[0] for cond in join_conditions],
                right_on=[cond[1] for cond in join_conditions],
                how=self.join_type.get(),
                suffixes=('_表1', '_表2')
            )
            
            # 重命名并选择最终输出的列
            selected_columns = []
            rename_dict = {}
            left_selected = []  # 添加这行，用于记录左表选中的列
            
            # 处理左表选中的列
            for col in self.left_fields_vars:
                if self.left_fields_vars[col].get():
                    left_selected.append(col)  # 记录左表选中的列
                    if col in result_df.columns:
                        selected_columns.append(col)
                    elif f"{col}_表1" in result_df.columns:
                        selected_columns.append(f"{col}_表1")
                        rename_dict[f"{col}_表1"] = col
        
            # 处理右表选中的列
            for col in self.right_fields_vars:
                if self.right_fields_vars[col].get():
                    if col in result_df.columns and col not in left_selected:  # 使用left_selected判断
                        selected_columns.append(col)
                    elif f"{col}_表2" in result_df.columns:
                        selected_columns.append(f"{col}_表2")
                        rename_dict[f"{col}_表2"] = f"{col}_表2"
            
            # 选择并重命名列
            result_df = result_df[selected_columns].rename(columns=rename_dict)
            
            # 修改保存文件名，增加时间后缀
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = self.save_path.get()
            if self.use_source_dir.get():
                save_dir = os.path.dirname(self.left_file.get())
            
            save_path = os.path.join(save_dir, f"表间关联结果_{timestamp}.xlsx")
            save_path = os.path.abspath(save_path)  # 获取绝对路径
            result_df.to_excel(save_path, index=False)
            
            # 修改打开文件夹的方式
            answer = messagebox.askyesno(
                "成功", 
                f"关联结果已保存至：{save_path}\n\n是否打开输出文件夹？"
            )
            if answer:
                import subprocess
                # 使用subprocess替代os.system，并使用正确的命令格式
                subprocess.run(['explorer', '/select,', save_path], shell=True)
            
        except Exception as e:
            messagebox.showerror("错误", f"执行关联失败：{str(e)}")
    
    # 添加全选和反选方法
    def select_all(self, side):
        """全选功能"""
        vars_dict = self.left_fields_vars if side == "left" else self.right_fields_vars
        for var in vars_dict.values():
            var.set(True)

    def invert_selection(self, side):
        """反选功能"""
        vars_dict = self.left_fields_vars if side == "left" else self.right_fields_vars
        for var in vars_dict.values():
            var.set(not var.get())