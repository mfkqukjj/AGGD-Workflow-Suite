import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from sqlparse import format as sql_format



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
        
        # 添加数据库连接配置
        self.hive_config = {
            'host': 'localhost',
            'port': 10000,
            'database': 'default'
        }
        self.mysql_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'db': 'test'
        }
        
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
            ("SQL格式化", self.sql_formatter, "SQL语句格式美化"),
            ("经纬度计算", self.geo_distance, "计算两点间距离"),
            ("批量CASE", self.case_builder, "生成CASE WHEN语句"),  # 修改这行
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
            

    def sql_formatter(self):
        """SQL语句格式化功能"""
        try:
            self.current_function = "formatter"
            dialog = tk.Toplevel(self)
            dialog.title("SQL语句格式化")
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            
            # 保存对话框引用
            self.dialog = dialog
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 格式化选项
            options_frame = ttk.LabelFrame(main_frame, text="格式化选项", padding="5")
            options_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 关键字大小写选择
            case_frame = ttk.Frame(options_frame)
            case_frame.pack(fill=tk.X, pady=5)
            ttk.Label(case_frame, text="关键字格式：").pack(side=tk.LEFT)
            case_var = tk.StringVar(value="upper")
            ttk.Radiobutton(case_frame, text="大写", variable=case_var, 
                           value="upper").pack(side=tk.LEFT, padx=10)
            ttk.Radiobutton(case_frame, text="小写", variable=case_var, 
                           value="lower").pack(side=tk.LEFT)
            
            # 缩进选项
            indent_frame = ttk.Frame(options_frame)
            indent_frame.pack(fill=tk.X, pady=5)
            ttk.Label(indent_frame, text="缩进空格数：").pack(side=tk.LEFT)
            indent_var = tk.StringVar(value="4")
            ttk.Entry(indent_frame, textvariable=indent_var, width=5).pack(side=tk.LEFT, padx=5)
            
            # SQL输入区域
            input_frame = ttk.LabelFrame(main_frame, text="输入SQL", padding="5")
            input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            sql_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
            sql_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 解除默认的粘贴绑定
            sql_input.unbind('<Command-v>')
            sql_input.unbind('<<Paste>>')
            
            # 重新绑定粘贴功能
            def custom_paste(event=None):
                try:
                    # 如果有选中的文本，先删除
                    try:
                        sql_input.delete("sel.first", "sel.last")
                    except tk.TclError:
                        pass
                    # 获取剪贴板内容并插入
                    sql_input.insert(tk.INSERT, self.clipboard_get())
                except Exception as e:
                    print(f"粘贴错误: {str(e)}")
                return "break"
            
            # 只保留一个绑定
            sql_input.bind('<<Paste>>', custom_paste)
            
            # 格式化结果区域
            result_frame = ttk.LabelFrame(main_frame, text="格式化结果", padding="5")
            result_frame.pack(fill=tk.BOTH, expand=True)
            result_output = scrolledtext.ScrolledText(result_frame, height=10, wrap=tk.WORD)
            result_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            def format_sql():
                try:
                    sql = sql_input.get("1.0", tk.END).strip()
                    if not sql:
                        messagebox.showwarning("警告", "请输入SQL语句！")
                        return
                    
                    # 获取缩进空格数
                    indent_spaces = max(2, min(8, int(indent_var.get())))
                    
                    # 格式化SQL
                    formatted_sql = sql_format(
                        sql,
                        reindent=True,
                        indent_width=indent_spaces,
                        keyword_case=case_var.get(),
                        indent_after_first=True,
                        comma_first=False,
                        use_space_around_operators=True
                    )
                    
                    # 显示结果
                    result_output.delete("1.0", tk.END)
                    result_output.insert(tk.END, formatted_sql)
                    
                except Exception as e:
                    messagebox.showerror("错误", f"格式化失败：{str(e)}")
            
            # 按钮区域
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            # 格式化按钮
            ttk.Button(button_frame, 
                      text="格式化", 
                      command=format_sql
                      ).pack(side=tk.LEFT, padx=5)
            
            # 清空按钮
            ttk.Button(button_frame, 
                      text="清空", 
                      command=lambda: sql_input.delete("1.0", tk.END)
                      ).pack(side=tk.LEFT)
            
            # 复制结果按钮
            ttk.Button(button_frame, 
                      text="复制结果", 
                      command=lambda: self.copy_result(result_output)
                      ).pack(side=tk.LEFT, padx=5)
            
            # 添加窗口关闭处理
            dialog.protocol("WM_DELETE_WINDOW", 
                           lambda: self._close_formatter_dialog(dialog))
            
        except Exception as e:
            messagebox.showerror("错误", f"无法打开SQL格式化窗口：{str(e)}")

    def _close_formatter_dialog(self, dialog):
        """关闭格式化窗口"""
        dialog.grab_release()
        dialog.destroy()
        self.status_var.set("SQL格式化窗口已关闭")

    def geo_distance(self):
        """经纬度距离计算功能"""
        try:
            self.current_function = "geo_distance"
            dialog = tk.Toplevel(self)
            dialog.title("经纬度距离计算")
            dialog.geometry("600x400")
            dialog.transient(self)
            dialog.grab_set()
            
            # 添加 create_entry 函数定义
            def create_entry(parent, var):
                entry = ttk.Entry(parent, textvariable=var, width=15)
                
                def custom_paste(event=None):
                    try:
                        entry.delete(0, tk.END)
                        entry.insert(0, self.clipboard_get())
                    except Exception as e:
                        print(f"粘贴错误: {str(e)}")
                    return "break"
                
                # 绑定粘贴事件
                entry.bind('<<Paste>>', custom_paste)
                entry.bind('<Command-v>', custom_paste)
                return entry
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 第一组坐标输入
            frame1 = ttk.LabelFrame(main_frame, text="起点坐标", padding="5")
            frame1.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(frame1, text="经度1:").pack(side=tk.LEFT, padx=(5, 2))
            lat1_var = tk.StringVar()
            create_entry(frame1, lat1_var).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(frame1, text="纬度1:").pack(side=tk.LEFT, padx=(5, 2))
            lon1_var = tk.StringVar()
            create_entry(frame1, lon1_var).pack(side=tk.LEFT)
            
            # 第二组坐标输入
            frame2 = ttk.LabelFrame(main_frame, text="终点坐标", padding="5")
            frame2.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(frame2, text="经度2:").pack(side=tk.LEFT, padx=(5, 2))
            lat2_var = tk.StringVar()
            create_entry(frame2, lat2_var).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(frame2, text="纬度2:").pack(side=tk.LEFT, padx=(5, 2))
            lon2_var = tk.StringVar()
            create_entry(frame2, lon2_var).pack(side=tk.LEFT)
            
            # SQL结果显示区域
            result_frame = ttk.LabelFrame(main_frame, text="距离计算SQL", padding="5")
            result_frame.pack(fill=tk.BOTH, expand=True)
            result_text = scrolledtext.ScrolledText(result_frame, height=6, wrap=tk.WORD)
            result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            def generate_sql():
                try:
                    # 获取输入值并验证
                    coords = [
                        lat1_var.get().strip(),
                        lon1_var.get().strip(),
                        lat2_var.get().strip(),
                        lon2_var.get().strip()
                    ]
                    
                    if not all(coords):
                        messagebox.showwarning("警告", "请填写所有经纬度值！")
                        return
                    
                    # SQL模板
                    sql_template = """round((6378.138*2*ASIN(SQRT(POW(SIN(({lat1}*PI()/180-{lat2}*PI()/180)/2),2)+COS({lat1}*PI()/180)*COS({lat2}*PI()/180)*POW(SIN(({lon1}*PI()/180-{lon2}*PI()/180)/2),2)))*1000)"""
                    
                    # 替换参数
                    sql = sql_template.format(
                        lat1=coords[0],
                        lon1=coords[1],
                        lat2=coords[2],
                        lon2=coords[3]
                    )
                    
                    # 显示结果
                    result_text.delete('1.0', tk.END)
                    result_text.insert('1.0', sql)
                    
                except Exception as e:
                    messagebox.showerror("错误", f"生成SQL时发生错误：{str(e)}")
            
            # 按钮区域
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="生成SQL", 
                      command=generate_sql).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="复制", 
                      command=lambda: self.copy_result(result_text)).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="关闭", 
                      command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            # 添加说明文字
            ttk.Label(main_frame, text="注：计算结果单位为米", 
                     foreground="gray").pack(pady=(5, 0))
            
        except Exception as e:
            messagebox.showerror("错误", f"无法打开经纬度计算窗口：{str(e)}")


    class CaseBuilder(tk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.title("批量CASE WHEN生成器")
            self.geometry("800x600")
            self.transient(master)
            self.grab_set()
            self.create_widgets()

        def create_widgets(self):
            main_frame = ttk.Frame(self, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # 字段名和匹配方式选择区域
            config_frame = ttk.Frame(main_frame)
            config_frame.pack(fill=tk.X, pady=(0, 10))

            # 字段名输入
            field_frame = ttk.Frame(config_frame)
            field_frame.pack(side=tk.LEFT, padx=(0, 20))
            ttk.Label(field_frame, text="字段名：").pack(side=tk.LEFT)
            self.field_var = tk.StringVar()
            ttk.Entry(field_frame, textvariable=self.field_var, width=20).pack(side=tk.LEFT)

            # 匹配方式选择
            match_frame = ttk.Frame(config_frame)
            match_frame.pack(side=tk.LEFT)
            ttk.Label(match_frame, text="匹配方式：").pack(side=tk.LEFT)
            self.match_type = tk.StringVar(value="equals")
            ttk.Radiobutton(match_frame, text="全等匹配", variable=self.match_type, 
                        value="equals").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(match_frame, text="正则匹配", variable=self.match_type, 
                        value="regexp").pack(side=tk.LEFT)

            # 输入区域
            input_frame = ttk.LabelFrame(main_frame, text="输入数据（每行: 匹配值 结果值）", padding="5")
            input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            self.input_text = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
            self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 结果区域
            result_frame = ttk.LabelFrame(main_frame, text="生成结果", padding="5")
            result_frame.pack(fill=tk.BOTH, expand=True)
            self.result_text = scrolledtext.ScrolledText(result_frame, height=10, wrap=tk.WORD)
            self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 按钮区域
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            ttk.Button(button_frame, text="生成", 
                    command=self.generate_case).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="复制", 
                    command=self.copy_result).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="关闭", 
                    command=self.destroy).pack(side=tk.LEFT, padx=5)

        def generate_case(self):
            try:
                field_name = self.field_var.get().strip()
                if not field_name:
                    messagebox.showwarning("警告", "请输入字段名！")
                    return

                input_text = self.input_text.get("1.0", tk.END).strip()
                if not input_text:
                    messagebox.showwarning("警告", "请输入待处理的数据！")
                    return

                # 解析输入行
                lines = [line.strip() for line in input_text.split('\n') if line.strip()]
                case_parts = []
                
                is_regexp = self.match_type.get() == "regexp"
                
                if is_regexp:
                    # 使用字典收集相同结果值的匹配条件
                    result_patterns = {}
                    
                    for line in lines:
                        parts = re.split(r'\s+', line, maxsplit=1)
                        if len(parts) != 2:
                            messagebox.showwarning("警告", f"无效的输入行：{line}")
                            continue
                            
                        match_value, result = parts
                        
                        # 将相同结果的匹配模式收集到一起
                        if result in result_patterns:
                            result_patterns[result].append(match_value)
                        else:
                            result_patterns[result] = [match_value]
                    
                    # 生成合并后的WHEN子句
                    for result, patterns in result_patterns.items():
                        # 将多个模式用|连接
                        combined_pattern = '|'.join(patterns)
                        when_clause = f"WHEN {field_name} REGEXP '{combined_pattern}' THEN '{result}'"
                        case_parts.append(when_clause)
                        
                else:
                    # 全等匹配保持原有逻辑
                    for line in lines:
                        parts = re.split(r'\s+', line, maxsplit=1)
                        if len(parts) != 2:
                            messagebox.showwarning("警告", f"无效的输入行：{line}")
                            continue
                            
                        match_value, result = parts
                        when_clause = f"WHEN {field_name} = '{match_value}' THEN '{result}'"
                        case_parts.append(when_clause)

                # 构建完整的CASE语句
                if case_parts:
                    case_sql = "(CASE\n  " + "\n  ".join(case_parts) + "\nEND)"
                    txt_output.delete("1.0", tk.END)
                    txt_output.insert("1.0", case_sql)
                else:
                    messagebox.showwarning("警告", "没有有效的数据行！")

            except Exception as e:
                messagebox.showerror("错误", f"生成CASE语句时发生错误：{str(e)}")

        def copy_result(self):
            result = self.result_text.get("1.0", tk.END).strip()
            if result:
                self.clipboard_clear()
                self.clipboard_append(result)
                messagebox.showinfo("提示", "已复制到剪贴板！")
            else:
                messagebox.showwarning("警告", "没有可复制的内容！")

    def case_builder(self):
        """批量CASE WHEN生成器"""
        try:
            self.current_function = "case_builder"
            dialog = tk.Toplevel(self)
            dialog.title("批量CASE WHEN生成器")
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # 字段名和匹配方式选择区域
            config_frame = ttk.Frame(main_frame)
            config_frame.pack(fill=tk.X, pady=(0, 10))

            # 字段名输入
            field_frame = ttk.Frame(config_frame)
            field_frame.pack(side=tk.LEFT, padx=(0, 20))
            ttk.Label(field_frame, text="字段名：").pack(side=tk.LEFT)
            field_var = tk.StringVar()
            ttk.Entry(field_frame, textvariable=field_var, width=20).pack(side=tk.LEFT)

            # 匹配方式选择
            match_frame = ttk.Frame(config_frame)
            match_frame.pack(side=tk.LEFT)
            ttk.Label(match_frame, text="匹配方式：").pack(side=tk.LEFT)
            match_type = tk.StringVar(value="equals")
            ttk.Radiobutton(match_frame, text="全等匹配", variable=match_type, 
                        value="equals").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(match_frame, text="正则匹配", variable=match_type, 
                        value="regexp").pack(side=tk.LEFT)

            # 输入区域
            input_frame = ttk.LabelFrame(main_frame, text="输入数据（每行: 匹配值 结果值）", padding="5")
            input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            txt_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
            txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 添加粘贴功能
            def custom_paste(event=None):
                try:
                    txt_input.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                txt_input.insert(tk.INSERT, self.clipboard_get())
                return "break"  # 重要：阻止事件继续传播

            # 解除默认绑定
            txt_input.unbind('<<Paste>>')
            txt_input.unbind('<Command-v>')
            
            # 重新绑定粘贴事件（只使用一种绑定）
            txt_input.bind('<<Paste>>', custom_paste)

            # 结果区域
            result_frame = ttk.LabelFrame(main_frame, text="生成结果", padding="5")
            result_frame.pack(fill=tk.BOTH, expand=True)
            txt_output = scrolledtext.ScrolledText(result_frame, height=10, wrap=tk.WORD)
            txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            def generate_case():
                try:
                    field_name = field_var.get().strip()
                    if not field_name:
                        messagebox.showwarning("警告", "请输入字段名！")
                        return

                    input_text = txt_input.get("1.0", tk.END).strip()
                    if not input_text:
                        messagebox.showwarning("警告", "请输入待处理的数据！")
                        return

                    # 解析输入行
                    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
                    case_parts = []
                    
                    is_regexp = match_type.get() == "regexp"
                    
                    if is_regexp:
                        # 使用字典收集相同结果值的匹配条件
                        result_patterns = {}
                        
                        for line in lines:
                            parts = re.split(r'\s+', line, maxsplit=1)
                            if len(parts) != 2:
                                messagebox.showwarning("警告", f"无效的输入行：{line}")
                                continue
                                
                            match_value, result = parts
                            
                            # 将相同结果的匹配模式收集到一起
                            if result in result_patterns:
                                result_patterns[result].append(match_value)
                            else:
                                result_patterns[result] = [match_value]
                        
                        # 生成合并后的WHEN子句
                        for result, patterns in result_patterns.items():
                            # 将多个模式用|连接
                            combined_pattern = '|'.join(patterns)
                            when_clause = f"WHEN {field_name} REGEXP ('{combined_pattern}') THEN '{result}'"
                            case_parts.append(when_clause)
                            
                    else:
                        # 全等匹配保持原有逻辑
                        for line in lines:
                            parts = re.split(r'\s+', line, maxsplit=1)
                            if len(parts) != 2:
                                messagebox.showwarning("警告", f"无效的输入行：{line}")
                                continue
                                
                            match_value, result = parts
                            when_clause = f"WHEN {field_name} = '{match_value}' THEN '{result}'"
                            case_parts.append(when_clause)

                    # 构建完整的CASE语句
                    if case_parts:
                        case_sql = "(CASE\n  " + "\n  ".join(case_parts) + "\nEND)"
                        txt_output.delete("1.0", tk.END)
                        txt_output.insert("1.0", case_sql)
                    else:
                        messagebox.showwarning("警告", "没有有效的数据行！")

                except Exception as e:
                    messagebox.showerror("错误", f"生成CASE语句时发生错误：{str(e)}")

            # 按钮区域
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            ttk.Button(button_frame, text="生成SQL", 
                    command=generate_case).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="复制", 
                    command=lambda: self.copy_result(txt_output)).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="关闭", 
                    command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"无法打开CASE WHEN生成器：{str(e)}")