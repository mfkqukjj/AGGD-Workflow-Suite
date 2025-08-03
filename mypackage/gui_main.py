import tkinter as tk
from tkinter import ttk, messagebox
from .dataconcat import DataConcatTool
from .afileperpeople import BatchGenerator
from .sql_quick副本 import SqlQuick
from .hello import HelloWorld
from .table_split import TableSplitter
from .jz_xcc_bank_split import TableBankSplitter
from .excel_table_join import TableJoinTool 
from .fund_flow_analysis import FundFlowAnalysis
from .about_viewer import AboutViewer
from .file_split import FileSplitDialog
from .file_format_convert import FileFormatConvertDialog
from .file_tools import FileExplorerDialog, BatchRenameDialog


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("AGGD-Workflow-Suite工具箱")
        self.root.geometry("1280x800")  # 调整默认窗口大小
        
        # 创建主容器
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重，使布局更均匀
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        
        # 创建六大功能组
        self.create_file_group()
        self.create_data_group()
        self.create_finance_group()
        self.create_sql_group() 
        self.create_tools_group() 
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
            ("文件遍历", lambda: FileExplorerDialog(self.root)),
            ("批量重命名", lambda: BatchRenameDialog(self.root)),
            ("文件提取", lambda: self.show_feature("待开发")),
            ("格式转换", lambda: self.show_feature("待开发")),
            ("文件分切", self.open_file_split),
            ("批量文件操作", self.open_file_operations),
            ("文件加密", lambda: self.show_feature("文件加密"))
        ]
        self.add_buttons_to_frame(frame, buttons, "3x2")  # 使用3x2布局

    def create_data_group(self):
        """数据处理功能组"""
        frame = self.create_group_frame(self.main_frame, "数据处理")
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("多表合并", self.open_data_merge),
            ("自动分表", self.open_table_split),
            ("表间关联", self.open_table_join),  
            ("数据格式转换", self.open_file_format_convert),
            ("数据可视化", lambda: self.show_feature("数据可视化")),
            ("数据导出", lambda: self.show_feature("数据导出"))
        ]
        self.add_buttons_to_frame(frame, buttons)

    def create_finance_group(self):
        """资金分析功能组"""
        frame = self.create_group_frame(self.main_frame, "资金分析")
        frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("格式归一", lambda: self.show_feature("待开发")),
            ("JZD资金分析", self.open_fund_flow), 
            ("账户自析", lambda: self.show_feature("待开发")),
            ("抽佣分成", lambda: self.show_feature("待开发")),
            ("资金链条", lambda: self.show_feature("待开发")),
            ("资金流向图", lambda: self.show_feature("待开发")),
            ("报表生成", lambda: self.show_feature("待开发"))
        ]
        self.add_buttons_to_frame(frame, buttons)

    def create_sql_group(self):
        """SQL建模助手功能组"""
        frame = self.create_group_frame(self.main_frame, "建模助手")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("SQL生成器", self.open_sql_quick),
            ("SQL格式化", lambda: self.open_sql_with_feature("sql_formatter")),
            ("CASE生成", lambda: self.open_sql_with_feature("case_builder")),
            ("距离计算", lambda: self.open_sql_with_feature("geo_distance")),
            ("批量查询", lambda: self.open_sql_with_feature("batch_query")),
            ("批量录入", lambda: self.open_sql_with_feature("batch_insert"))
        ]
        self.add_buttons_to_frame(frame, buttons, "3x2")  # 使用3x2布局

    def create_tools_group(self):
        """效率工具"""
        frame = self.create_group_frame(self.main_frame, "场景效率工具")
        frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("一人一档", self.open_batch_gen),
            ("JZ_XCC分表", self.open_bank_split),
            ("人员架构", lambda: self.show_feature("待开发")),
            ("bu云关系", lambda: self.show_feature("待开发")),
            ("档案逆向Excel", lambda: self.show_feature("待开发"))
        ]
        self.add_buttons_to_frame(frame, buttons, "2x2")  # 使用2x2布局

    def create_other_group(self):
        """设置和帮助"""
        frame = self.create_group_frame(self.main_frame, "设置和帮助")
        frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        
        buttons = [
            ("系统设置", lambda: self.show_feature("系统设置")),
            ("使用帮助", lambda: self.show_feature("帮助中心")),
            ("授权管理", lambda: self.show_feature("授权管理")),
            ("关于我们", self.show_about)
        ]
        self.add_buttons_to_frame(frame, buttons)

    def add_buttons_to_frame(self, frame, buttons, layout="3x2"):
        """为指定框架添加按钮
        Args:
            frame: 按钮容器
            buttons: 按钮配置列表
            layout: 布局方式 "3x2"或"2x2"
        """
        # 配置列权重
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        if layout == "3x2":
            # 3行2列布局
            for i, (text, cmd) in enumerate(buttons):
                row = i // 2    # 计算行号
                col = i % 2     # 计算列号
                btn = ttk.Button(
                    frame,
                    text=text,
                    command=cmd,
                    style="Function.TButton"
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        else:
            # 2行2列布局
            for i, (text, cmd) in enumerate(buttons):
                row = i // 2    # 计算行号
                col = i % 2     # 计算列号
                btn = ttk.Button(
                    frame,
                    text=text,
                    command=cmd,
                    style="Function.TButton"
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

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

    def open_bank_split(self):
        """打开财务表格分表工具"""
        try:
            TableBankSplitter(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开财务表格分表工具：{str(e)}")


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

    def open_file_operations(self):
        """打开批量文件操作工具"""
        try:
            from .file_operations import FileOperations
            FileOperations(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开批量文件操作工具：{str(e)}")

    def open_table_join(self):
        """打开表间关联工具"""
        try:
            TableJoinTool(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开表间关联工具：{str(e)}")

    def open_file_split(self):
        """打开文件分割工具"""
        FileSplitDialog(self.root)

    def open_file_format_convert(self):
        """打开文件格式转换工具"""
        try:
            FileFormatConvertDialog(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件格式转换工具：{str(e)}")

    def open_sql_with_feature(self, feature_type):
        """打开SQL工具并直接调用指定功能"""
        try:
            sql_tool = SqlQuick(self.root)
            if feature_type == "sql_formatter":
                sql_tool.sql_formatter()
            elif feature_type == "case_builder":
                sql_tool.case_builder()
            elif feature_type == "geo_distance":
                sql_tool.geo_distance()
            elif feature_type == "batch_query":
                sql_tool.batch_query()
            elif feature_type == "batch_insert":
                sql_tool.batch_insert()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开{feature_type}功能：{str(e)}")

    def show_about(self):
        """显示关于我们页面"""
        try:
            AboutViewer(self.root)
        except Exception as e:
            messagebox.showerror("开发中", f"页面建设中：{str(e)}")

    def open_fund_flow(self):
        """打开资金流向分析工具"""
        try:
            from . import fund_flow_analysis
            fund_flow_analysis.FundFlowAnalysis(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开资金流向分析工具：{str(e)}")


class SqlFeatures:
    def create_dialog(self, title, size="600x500"):
        """创建通用对话框"""
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.geometry(size)
        dialog.transient(self.master)
        dialog.grab_set()
        return dialog


