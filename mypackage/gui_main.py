import tkinter as tk
from tkinter import ttk, messagebox
from .dataconcat import DataConcatTool
from .afileperpeople import BatchGenerator
from .sql_quick import SqlQuick
from .hello import HelloWorld
from .table_split import TableSplitter  # 新增导入

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("AGGD-Workflow-Suite工具箱")
        self.root.geometry("800x600")
        
        # 创建主容器
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建四大功能组
        self.create_file_group()
        self.create_data_group()
        self.create_finance_group()
        self.create_other_group()

    def create_group_frame(self, parent, title):
        """创建带边框的分组框架"""
        frame = ttk.LabelFrame(
            parent,
            text=title,
            padding=15,
            relief="groove",
            borderwidth=2
        )
        return frame

    def create_file_group(self):
        """文件操作功能组"""
        frame = self.create_group_frame(self.main_frame, "文件操作")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("多表合并", self.open_data_merge),
            ("自动分表", self.open_table_split),  # 修改这行
            ("一人一档", self.open_batch_gen)
        ]
        self.add_buttons_to_frame(frame, buttons)

    def create_finance_group(self):
        """资金分析功能组"""
        frame = self.create_group_frame(self.main_frame, "资金分析")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("简单示例", self.open_hello),
            ("简单示例", self.open_hello),
            ("简单示例", self.open_hello)  # 简单示例展示
        ]
        self.add_buttons_to_frame(frame, buttons)

    def create_data_group(self):
        """数据处理功能组"""
        frame = self.create_group_frame(self.main_frame, "数据处理")
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("SQL助手", self.open_sql_quick), 
            ("正在建设", lambda: self.show_feature("正在建设")),
            ("正在建设", lambda: self.show_feature("正在建设"))
        ]
        self.add_buttons_to_frame(frame, buttons)

    def create_other_group(self):
        """其他功能组"""
        frame = self.create_group_frame(self.main_frame, "其他功能")
        frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("系统设置", lambda: self.show_feature("系统设置")),
            ("使用帮助", lambda: self.show_feature("帮助中心")),
            ("关于我们", lambda: self.show_feature("关于页面"))
        ]
        self.add_buttons_to_frame(frame, buttons)

    def add_buttons_to_frame(self, frame, buttons):
        """为指定框架添加按钮"""
        for text, cmd in buttons:
            btn = ttk.Button(
                frame,
                text=text,
                width=18,
                command=cmd,
                style="Function.TButton"
            )
            btn.pack(pady=8, fill=tk.X)

    def show_feature(self, feature_name):
        """默认功能演示窗口（供后续替换）"""
        popup = tk.Toplevel(self.root)
        popup.title(feature_name)
        
        content = ttk.Frame(popup, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content, text=f"这是【{feature_name}】的演示界面",
                 font=('微软雅黑', 14)).pack(pady=10)
        ttk.Label(content, text="后续可以在此处添加实际功能代码",
                 font=('微软雅黑', 10)).pack()
        ttk.Button(content, text="关闭", command=popup.destroy).pack(pady=15)

    def open_data_merge(self):
        """打开数据合并工具"""
        DataConcatTool(self.root)

    def open_sql_quick(self):
        """打开SQL快速生成工具"""
        try:
            SqlQuick(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开SQL工具：{str(e)}")


    def open_batch_gen(self):
        """打开一人一档生成工具"""
        BatchGenerator(self.root) 

    def open_hello(self):
        """打开简单示例"""
        try:
            HelloWorld(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开简单示例：{str(e)}")

    def open_table_split(self):
        """打开自动分表工具"""
        try:
            TableSplitter(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开自动分表工具：{str(e)}")


