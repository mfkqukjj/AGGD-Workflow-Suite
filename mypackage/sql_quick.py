import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class SqlQuick(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("SQL快捷生成工具")
        self.geometry("800x600")
        self.transient(master)  # 设置为主窗口的子窗口
        self.grab_set()         # 设置为模态窗口
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.center_window()    # 窗口居中
        
        # 添加初始化属性
        self.current_function = None
        self.dialog = None
        
        # 主功能按钮区域
        self.create_function_buttons()
        
    def create_function_buttons(self):
        """创建功能按钮"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        buttons = [
            ("批量查询", self.batch_query, "生成批量查询SQL语句"),
            ("批量录入", self.batch_insert, "生成批量数据录入SQL"),
            ("语句校验", lambda: self.under_construction(), "功能未完成提示"),
            ("功能4", lambda: self.under_construction(), "功能未完成提示"),
            ("功能5", lambda: self.under_construction(), "功能未完成提示"),
            ("功能6", lambda: self.under_construction(), "功能未完成提示"),
            ("功能7", lambda: self.under_construction(), "功能未完成提示"),
            ("功能8", lambda: self.under_construction(), "功能未完成提示")
        ]
        
        for idx, (text, cmd, tooltip) in enumerate(buttons):
            btn = ttk.Button(
                main_frame, 
                text=text,
                width=15,
                command=cmd
            )
            btn.grid(row=idx//4, column=idx%4, padx=10, pady=10, sticky='ew')
            
            # 添加工具提示
            self.create_tooltip(btn, tooltip)
            
    def create_tooltip(self, widget, text):
        """创建悬停提示"""
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, justify=tk.LEFT,
                            background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    # -------------------- 通用方法 --------------------
    def under_construction(self):
        """功能未完成提示"""
        messagebox.showinfo("提示", "功能正在建设中，敬请期待！")

    def create_input_dialog(self, title, has_match_option=False):
        """创建输入弹窗通用组件"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("600x500")
        
        # 确保窗口显示在前面
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入区域", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        txt_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 匹配选项（如果需要）
        if has_match_option:
            match_type = tk.StringVar(value="contain")
            option_frame = ttk.Frame(main_frame)
            option_frame.pack(fill=tk.X, pady=5)
            ttk.Radiobutton(option_frame, text="包含匹配", 
                           variable=match_type,
                           value="contain").pack(side=tk.LEFT, padx=10)
            ttk.Radiobutton(option_frame, text="全等匹配", 
                           variable=match_type,
                           value="exact").pack(side=tk.LEFT)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="生成的SQL", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        txt_output = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        txt_output.config(state=tk.NORMAL)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 使用lambda传递所有必要参数
        if has_match_option:
            ttk.Button(button_frame, text="生成SQL", 
                       command=lambda: self.process_input(
                           txt_input.get("1.0", tk.END).strip(),
                           txt_output,
                           match_type.get()
                       )).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="生成SQL", 
                       command=lambda: self.process_input(
                           txt_input.get("1.0", tk.END).strip(),
                           txt_output,
                           None
                       )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空", 
                   command=lambda: txt_input.delete("1.0", tk.END)
                   ).pack(side=tk.LEFT)
        
        # 复制按钮
        ttk.Button(main_frame, text="复制到剪贴板", 
                   command=lambda: self.copy_result(txt_output)).pack(pady=10)
        
        return dialog

    def process_input(self, raw_text, output_widget, match_type=None):
        """通用文本处理逻辑"""
        try:
            if not raw_text.strip():
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
            
            # SQL注入检查
            if any(self.has_sql_injection(item) for item in unique_data):
                messagebox.showerror("安全警告", "检测到潜在的SQL注入风险！")
                return
                
            # 生成SQL
            if self.current_function == "query":
                self.generate_query_sql(unique_data, output_widget, match_type)
            elif self.current_function == "insert":
                self.generate_insert_sql(unique_data, output_widget)
                
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{str(e)}")
            
    def has_sql_injection(self, text):
        """SQL注入检查"""
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_"]
        return any(char in text for char in dangerous_chars)

    # -------------------- 功能1：批量查询 --------------------
    def batch_query(self):
        """批量查询功能"""
        try:
            self.current_function = "query"
            self.dialog = self.create_input_dialog("批量查询 SQL 生成", has_match_option=True)
            self.status_var.set("批量查询窗口已打开")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开批量查询窗口：{str(e)}")

    def generate_query_sql(self, data, output_widget, match_type):
        """生成查询SQL"""
        if match_type == "contain":
            pattern = '|'.join(data)
            sql = f"[证件号码] REGEXP '({pattern})'"
        else:
            quoted_data = [f"'{item}'" for item in data]
            in_clause = ",".join(quoted_data)
            sql = f"[证件号码] IN ({in_clause})"
        
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, sql)

    # -------------------- 功能2：批量录入 --------------------
    def batch_insert(self):
        """批量录入功能"""
        try:
            self.current_function = "insert"
            self.dialog = self.create_input_dialog("批量录入 SQL 生成")
            self.status_var.set("批量录入窗口已打开")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开批量录入窗口：{str(e)}")
        
    def generate_insert_sql(self, data, output_widget):
        """生成录入SQL"""
        quoted_data = [f"'{item}'" for item in data]
        array_clause = ",".join(quoted_data)
        sql = f"""SELECT DISTINCT '自主录入' AS 类型, 
explode(ARRAY({array_clause})) AS 自录入数据 

FROM  """
        
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, sql)
        
    def center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_closing(self):
        """窗口关闭处理"""
        self.grab_release()
        self.destroy()
        
    def copy_result(self, output_widget):
        """复制结果到剪贴板"""
        result = output_widget.get("1.0", tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            self.status_var.set("已复制到剪贴板！")
        else:
            messagebox.showinfo("提示", "没有可复制的内容！")