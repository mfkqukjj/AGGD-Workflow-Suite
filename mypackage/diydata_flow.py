import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_cytoscape as cyto
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime

class DataSelector:
    def __init__(self):
        self.df = None
        self.selected_data = None
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title('资金流向数据选择器')
        self.root.geometry('600x400')
        
        # 添加导入按钮
        tk.Button(self.root, text='导入Excel/CSV', command=self.import_file).pack(pady=10)
        
        # 创建筛选框架
        self.filter_frame = ttk.LabelFrame(self.root, text='数据筛选', padding=10)
        self.filter_frame.pack(fill='x', padx=10, pady=5)
        
        # 创建变量
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.label_var = tk.StringVar()
        self.label_pattern = tk.StringVar(value='{上级}-{下级}')  # 添加默认格式
        
        # 添加筛选控件
        self.create_filter_widgets()
        
        # 添加确认按钮
        tk.Button(self.root, text='确认选择', command=self.confirm_selection).pack(pady=10)

    def import_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Excel files', '*.xlsx *.xls'), ('CSV files', '*.csv')]
        )
        if file_path:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            self.update_dropdown_options()
    
    def create_filter_widgets(self):
        # 上级选择
        tk.Label(self.filter_frame, text='选择上级列：').grid(row=0, column=0, pady=5)
        self.source_combo = ttk.Combobox(self.filter_frame, textvariable=self.source_var)
        self.source_combo.grid(row=0, column=1, pady=5)
        
        # 下级选择
        tk.Label(self.filter_frame, text='选择下级列：').grid(row=1, column=0, pady=5)
        self.target_combo = ttk.Combobox(self.filter_frame, textvariable=self.target_var)
        self.target_combo.grid(row=1, column=1, pady=5)
        
        # 关联备注选择
        tk.Label(self.filter_frame, text='选择关联备注列：').grid(row=2, column=0, pady=5)
        self.label_combo = ttk.Combobox(self.filter_frame, textvariable=self.label_var)
        self.label_combo.grid(row=2, column=1, pady=5)
        
        # 修改关联备注选择部分
        label_frame = ttk.LabelFrame(self.filter_frame, text='关联备注设置')
        label_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')
        
        ttk.Label(label_frame, text='备注格式：').grid(row=0, column=0, pady=5)
        self.label_entry = ttk.Entry(label_frame, textvariable=self.label_pattern, width=30)
        self.label_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(label_frame, text='可用字段：').grid(row=1, column=0, pady=5)
        self.available_fields = ttk.Label(label_frame, text='使用 {字段名} 格式引用列数据')
        self.available_fields.grid(row=1, column=1, pady=5)

    def update_dropdown_options(self):
        if self.df is not None:
            columns = self.df.columns.tolist()
            for combo in [self.source_combo, self.target_combo]:
                combo['values'] = columns
            # 更新可用字段提示
            fields_text = '可用字段：' + '、'.join([f'{{{col}}}' for col in columns])
            self.available_fields.config(text=fields_text)

    def confirm_selection(self):
        try:
            # 修改验证逻辑，只检查必要的字段
            if self.source_var.get() and self.target_var.get():
                # 获取必要的列
                columns = [self.source_var.get(), self.target_var.get()]
                
                # 如果用户没有选择标签列，就只使用必要的列
                self.selected_data = self.df[columns]
                
                # 在销毁窗口前打印确认信息
                print(f"已选择数据：上级列-{self.source_var.get()}, 下级列-{self.target_var.get()}")
                
                self.root.quit()  # 先退出mainloop
                self.root.destroy()  # 再销毁窗口
            else:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("警告", "请至少选择上级列和下级列！")
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", f"选择数据时发生错误：{str(e)}")
            print(f"错误详情：{str(e)}")  # 打印错误详情
    
    def get_label_text(self, row):
        """根据模板生成关联备注文本"""
        try:
            text = self.label_pattern.get()
            # 获取所有可用的列
            available_columns = self.df.columns

            # 替换所有可用的列名
            for col in available_columns:
                placeholder = '{' + col + '}'
                if placeholder in text:
                    # 获取值并进行类型处理
                    value = row[col]  # 使用直接索引替代 get()
                    
                    # 处理不同类型的值
                    if pd.isna(value):
                        formatted_value = ''
                    elif isinstance(value, (int, float)):
                        # 数值类型特殊处理，去除小数点后多余的0
                        formatted_value = f"{value:,.2f}".rstrip('0').rstrip('.')
                    else:
                        formatted_value = str(value)
                    
                    text = text.replace(placeholder, formatted_value)

            return text if text else '无备注'
        except Exception as e:
            print(f"备注生成错误: {str(e)}")  # 添加调试信息
            print(f"当前模板: {text}")
            print(f"当前行数据: {row}")
            return f'格式错误: {str(e)}'

    def get_elements(self):
        if self.selected_data is None:
            return []
        
        nodes = []
        edges = []
        unique_names = set()
        
        # 收集唯一节点
        for _, row in self.selected_data.iterrows():
            unique_names.add(row[self.source_var.get()])
            unique_names.add(row[self.target_var.get()])
        
        # 创建节点
        for name in unique_names:
            nodes.append({'data': {'id': str(name), 'label': str(name)}})
        
        # 使用模板格式创建边
        for _, row in self.selected_data.iterrows():
            edges.append({
                'data': {
                    'source': str(row[self.source_var.get()]),
                    'target': str(row[self.target_var.get()]),
                    'label': self.get_label_text(row)  # 使用模板生成标签
                }
            })
        
        return nodes + edges

class DataApp:
    def __init__(self):
        # 先创建 Dash 应用
        self.app = dash.Dash(__name__)
        # 初始化数据
        self.elements = []
        # 设置布局
        self.setup_layout()
        self.setup_callbacks()
        # 最后再获取数据
        self.elements = self.get_initial_data()
        
    def get_initial_data(self):
        # 在主线程中运行 Tkinter
        selector = DataSelector()
        selector.root.mainloop()
        return selector.get_elements()
    
    def setup_layout(self):
        self.app.layout = html.Div([
            html.H1('资金流向关系图', style={'textAlign': 'center'}),
            html.Div([
                html.Label('选择布局方式：', style={'marginRight': '10px'}),
                dcc.Dropdown(
                    id='layout-select',
                    options=[
                        {'label': '分层布局', 'value': 'breadthfirst'},
                        {'label': '网格布局', 'value': 'grid'},
                        {'label': '圆形布局', 'value': 'circle'},
                        {'label': '同心圆', 'value': 'concentric'},
                        {'label': '力导向图', 'value': 'cose'}
                    ],
                    value='breadthfirst',
                    style={'width': '200px', 'display': 'inline-block'}
                ),
                html.Button(
                    '导入新数据', 
                    id='refresh-button', 
                    n_clicks=0,
                    style={'marginLeft': '20px'}
                )
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'marginBottom': '20px'}),
            
            cyto.Cytoscape(
                id='cytoscape',
                elements=self.elements,
                layout={
                    'name': 'breadthfirst',
                    'animate': True,
                    'animationDuration': 1000,
                    'fit': True
                },
                style={'width': '100%', 'height': '800px', 'backgroundColor': '#ffffff'},
                stylesheet=[
                    {
                        'selector': 'edge',
                        'style': {
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'label': 'data(label)',
                            'font-size': '12px',
                            'text-rotation': 'autorotate',
                            'line-color': '#666',
                            'target-arrow-color': '#666',
                            'width': 1,
                            'text-outline-color': '#ffffff',
                            'text-outline-width': 2
                        }
                    },
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'font-size': '16px',
                            'background-color': '#95c8ed',
                            'width': 30,
                            'height': 30,
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'text-outline-color': '#ffffff',
                            'text-outline-width': 2
                        }
                    }
                ]
            )
        ])
    
    def setup_callbacks(self):
        @self.app.callback(
            Output('cytoscape', 'layout'),
            Input('layout-select', 'value')
        )
        def update_layout(layout):
            return {
                'name': layout,
                'animate': True,
                'animationDuration': 1000,
                'fit': True
            }
        
        @self.app.callback(
            Output('cytoscape', 'elements'),
            Input('refresh-button', 'n_clicks')
        )
        def refresh_data(n_clicks):
            if n_clicks is None:
                # 初始加载时返回当前元素
                return self.elements
            
            # 创建新的数据选择器
            selector = DataSelector()
            selector.root.mainloop()
            new_elements = selector.get_elements()
            
            if new_elements:
                self.elements = new_elements
            return self.elements
    
    def run(self):
        self.app.run(
            debug=False,  # 关闭调试模式
            host='127.0.0.1',
            port=8050
        )

if __name__ == '__main__':
    app = DataApp()
    app.run()