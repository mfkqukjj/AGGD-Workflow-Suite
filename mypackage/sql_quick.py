import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from sqlparse import format as sql_format

class BatchQueryDialog(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("批量查询 SQL 生成")
        self.geometry("600x500")
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入区域", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.txt_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 匹配选项
        self.match_type = tk.StringVar(value="contain")
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(option_frame, text="包含匹配", 
                       variable=self.match_type,
                       value="contain").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(option_frame, text="全等匹配", 
                       variable=self.match_type,
                       value="exact").pack(side=tk.LEFT)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="生成的SQL", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_output = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="生成SQL", 
                   command=self.generate_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", 
                   command=self.clear_input).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="复制结果", 
                   command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                   command=self.destroy).pack(side=tk.LEFT, padx=5)

    def generate_sql(self):
        try:
            raw_text = self.txt_input.get("1.0", tk.END).strip()
            if not raw_text:
                messagebox.showerror("错误", "输入内容不能为空！")
                return
                
            # 数据清洗
            data_list = re.split(r'[\s,，、；;]+', raw_text)
            data_list = [item.strip() for item in data_list if item.strip()]
            
            if not data_list:
                messagebox.showerror("错误", "未找到有效数据！")
                return
            
            # 去重
            unique_data = list(set(data_list))
            
            if self.match_type.get() == "contain":
                pattern = '|'.join(unique_data)
                sql = f"[证件号码] REGEXP '({pattern})'"
            else:
                quoted_data = [f"'{item}'" for item in unique_data]
                in_clause = ",".join(quoted_data)
                sql = f"[证件号码] IN ({in_clause})"
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, sql)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成SQL失败：{str(e)}")

    def clear_input(self):
        self.txt_input.delete("1.0", tk.END)

    def copy_result(self):
        result = self.txt_output.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("提示", "已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")

# 其他功能类似地分别创建独立的Dialog类
class SqlFormatterDialog(tk.Toplevel):
    """SQL格式化工具"""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("SQL 格式化")
        self.geometry("800x600")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入SQL", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.txt_input = scrolledtext.ScrolledText(input_frame, height=12, wrap=tk.WORD)
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 选项区域
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        # 缩进选项
        ttk.Label(options_frame, text="缩进空格:").pack(side=tk.LEFT, padx=5)
        self.indent_var = tk.StringVar(value="4")
        indent_entry = ttk.Entry(options_frame, textvariable=self.indent_var, width=5)
        indent_entry.pack(side=tk.LEFT, padx=5)
        
        # 大小写选项
        self.case_var = tk.StringVar(value="upper")
        ttk.Radiobutton(options_frame, text="大写", 
                       variable=self.case_var,
                       value="upper").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(options_frame, text="小写", 
                       variable=self.case_var,
                       value="lower").pack(side=tk.LEFT)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="格式化结果", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_output = scrolledtext.ScrolledText(output_frame, height=12, wrap=tk.WORD)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="格式化", 
                  command=self.format_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", 
                  command=self.clear_input).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="复制结果", 
                  command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def format_sql(self):
        try:
            sql = self.txt_input.get("1.0", tk.END).strip()
            if not sql:
                messagebox.showerror("错误", "请输入SQL语句！")
                return
            
            # 获取选项
            indent = int(self.indent_var.get())
            keyword_case = self.case_var.get()
            
            # 格式化SQL
            formatted_sql = sql_format(
                sql,
                reindent=True,
                indent_width=indent,
                keyword_case=keyword_case
            )
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, formatted_sql)
            
        except Exception as e:
            messagebox.showerror("错误", f"格式化失败：{str(e)}")

    def clear_input(self):
        self.txt_input.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)

    def copy_result(self):
        result = self.txt_output.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("提示", "已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")

class CaseBuilderDialog(tk.Toplevel):
    """CASE语句生成器"""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("CASE 语句生成器")
        self.geometry("700x600")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="字段名:").pack(side=tk.LEFT, padx=5)
        self.field_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.field_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # 映射输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入映射关系（每行一个，格式：原值=目标值）", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.txt_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="生成的CASE语句", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_output = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="生成CASE", 
                  command=self.generate_case).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", 
                  command=self.clear_input).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="复制结果", 
                  command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def generate_case(self):
        try:
            field = self.field_var.get().strip()
            if not field:
                messagebox.showerror("错误", "请输入字段名！")
                return
                
            mappings = self.txt_input.get("1.0", tk.END).strip().split('\n')
            if not mappings or not mappings[0]:
                messagebox.showerror("错误", "请输入映射关系！")
                return
            
            # 生成CASE语句
            case_parts = ["CASE " + field]
            for mapping in mappings:
                if "=" in mapping:
                    source, target = mapping.split('=', 1)
                    source = source.strip()
                    target = target.strip()
                    case_parts.append(f"    WHEN '{source}' THEN '{target}'")
            
            case_parts.append("    ELSE " + field)
            case_parts.append("END")
            
            case_sql = '\n'.join(case_parts)
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, case_sql)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成CASE语句失败：{str(e)}")

    def clear_input(self):
        self.field_var.set("")
        self.txt_input.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)

    def copy_result(self):
        result = self.txt_output.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("提示", "已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")

class GeoDistanceDialog(tk.Toplevel):
    """经纬度距离计算SQL生成器"""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("经纬度距离计算SQL")
        self.geometry("700x500")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置字段", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行
        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="表1字段:").pack(side=tk.LEFT, padx=5)
        self.lat1_var = tk.StringVar(value="lat1")
        self.lng1_var = tk.StringVar(value="lng1")
        ttk.Entry(row1, textvariable=self.lat1_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Entry(row1, textvariable=self.lng1_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 第二行
        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="表2字段:").pack(side=tk.LEFT, padx=5)
        self.lat2_var = tk.StringVar(value="lat2")
        self.lng2_var = tk.StringVar(value="lng2")
        ttk.Entry(row2, textvariable=self.lat2_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Entry(row2, textvariable=self.lng2_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="生成的距离计算SQL", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_output = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="生成SQL", 
                  command=self.generate_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制结果", 
                  command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def generate_sql(self):
        try:
            lat1 = self.lat1_var.get().strip()
            lng1 = self.lng1_var.get().strip()
            lat2 = self.lat2_var.get().strip()
            lng2 = self.lng2_var.get().strip()
            
            if not all([lat1, lng1, lat2, lng2]):
                messagebox.showerror("错误", "请填写所有字段名！")
                return
            
            # 生成Haversine公式SQL
            sql = f"""
ROUND(
    6371 * 2 * ASIN(
        SQRT(
            POWER(
                SIN(({lat2} - {lat1}) * PI() / 180 / 2),
                2
            ) + COS({lat1} * PI() / 180) * COS({lat2} * PI() / 180) * POWER(
                SIN(({lng2} - {lng1}) * PI() / 180 / 2),
                2
            )
        )
    )
, 2) AS distance_km"""
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, sql.strip())
            
        except Exception as e:
            messagebox.showerror("错误", f"生成SQL失败：{str(e)}")

    def copy_result(self):
        result = self.txt_output.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("提示", "已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")

class BatchInsertDialog(tk.Toplevel):
    """批量数据录入SQL生成器"""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("批量数据录入SQL")
        self.geometry("800x600")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表名配置
        config_frame = ttk.Frame(main_frame)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="表名:").pack(side=tk.LEFT, padx=5)
        self.table_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.table_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # 字段配置
        field_frame = ttk.LabelFrame(main_frame, text="字段配置（每行一个字段名）", padding="5")
        field_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.txt_fields = scrolledtext.ScrolledText(field_frame, height=5, wrap=tk.WORD)
        self.txt_fields.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 数据输入
        data_frame = ttk.LabelFrame(main_frame, text="输入数据（每行一条记录，字段间用逗号分隔）", padding="5")
        data_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.txt_data = scrolledtext.ScrolledText(data_frame, height=8, wrap=tk.WORD)
        self.txt_data.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="生成的INSERT语句", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_output = scrolledtext.ScrolledText(output_frame, height=8, wrap=tk.WORD)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="生成SQL", 
                  command=self.generate_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", 
                  command=self.clear_input).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="复制结果", 
                  command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def generate_sql(self):
        try:
            table_name = self.table_var.get().strip()
            if not table_name:
                messagebox.showerror("错误", "请输入表名！")
                return
            
            # 获取字段列表
            fields = self.txt_fields.get("1.0", tk.END).strip().split('\n')
            fields = [f.strip() for f in fields if f.strip()]
            if not fields:
                messagebox.showerror("错误", "请输入字段名！")
                return
            
            # 获取数据
            data_lines = self.txt_data.get("1.0", tk.END).strip().split('\n')
            data_lines = [line.strip() for line in data_lines if line.strip()]
            if not data_lines:
                messagebox.showerror("错误", "请输入数据！")
                return
            
            # 生成INSERT语句
            field_list = ", ".join([f"[{f}]" for f in fields])
            values_list = []
            
            for line in data_lines:
                values = line.split(',')
                values = [v.strip() for v in values]
                if len(values) != len(fields):
                    raise ValueError(f"数据字段数量不匹配: {line}")
                values = [f"'{v}'" for v in values]
                values_list.append("(" + ", ".join(values) + ")")
            
            sql = f"INSERT INTO [{table_name}] ({field_list})\nVALUES\n"
            sql += ",\n".join(values_list) + ";"
            
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, sql)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成SQL失败：{str(e)}")

    def clear_input(self):
        self.table_var.set("")
        self.txt_fields.delete("1.0", tk.END)
        self.txt_data.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)

    def copy_result(self):
        result = self.txt_output.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("提示", "已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")

# 提供快捷函数用于在gui_main中调用
def open_batch_query(master):
    return BatchQueryDialog(master)

def open_sql_formatter(master):
    return SqlFormatterDialog(master)

def open_geo_distance(master):
    return GeoDistanceDialog(master)

def open_case_builder(master):
    return CaseBuilderDialog(master)

def open_batch_insert(master):
    return BatchInsertDialog(master)