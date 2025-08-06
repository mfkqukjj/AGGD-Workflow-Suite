import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import dash
from dash import html, dcc
import dash_cytoscape as cyto
import threading
import webbrowser
from dash.dependencies import Input, Output, State
import json
import networkx as nx

class MoneyFlowViewer(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("自定义流向图")
        self.geometry("600x500")
        self.grab_set()
        self.df = None
        self.node1_var = tk.StringVar()
        self.node2_var = tk.StringVar()
        self.label_fields = []
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        # 导入文件
        filefrm = ttk.Frame(frm)
        filefrm.pack(fill=tk.X, pady=5)
        ttk.Label(filefrm, text="导入Excel/CSV文件：").pack(side=tk.LEFT)
        ttk.Button(filefrm, text="浏览", command=self.load_file).pack(side=tk.LEFT, padx=5)

        # 字段选择
        self.fields_frame = ttk.LabelFrame(frm, text="请选择节点字段", padding=10)
        self.fields_frame.pack(fill=tk.X, pady=10)

        # 链路备注
        self.label_frame = ttk.LabelFrame(frm, text="链路备注内容（可多选）", padding=10)
        self.label_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 条件区
        self.cond_frame = ttk.LabelFrame(frm, text="条件区", padding=10)
        self.cond_frame.pack(fill=tk.X, pady=5)

        # 生成按钮
        ttk.Button(frm, text="生成流向图", command=self.generate_flow).pack(pady=10)

        # 排除自身
        self.exclude_self_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.cond_frame, text="排除流向自身", variable=self.exclude_self_var).grid(row=0, column=0, sticky="w")

    def load_file(self):
        filetypes = [("Excel/CSV", "*.xlsx *.xls *.csv"), ("所有文件", "*.*")]
        filename = filedialog.askopenfilename(title="选择数据文件", filetypes=filetypes)
        if not filename:
            return
        try:
            if filename.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(filename, dtype=str)
            elif filename.endswith('.csv'):
                self.df = pd.read_csv(filename, dtype=str)
            else:
                messagebox.showerror("错误", "仅支持Excel或CSV文件")
                return
            self.df.fillna("", inplace=True)
            self.show_field_selectors()
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{e}")

    def show_field_selectors(self):
        # 清空旧内容
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        columns = list(self.df.columns)
        if len(columns) < 2:
            messagebox.showerror("错误", "数据字段不足")
            return

        # 节点字段选择
        ttk.Label(self.fields_frame, text="节点字段1（起点）：").grid(row=0, column=0, sticky="w")
        node1_cb = ttk.Combobox(self.fields_frame, values=columns, textvariable=self.node1_var, state="readonly")
        node1_cb.grid(row=0, column=1, padx=5)
        node1_cb.current(0)

        ttk.Label(self.fields_frame, text="节点字段2（终点）：").grid(row=1, column=0, sticky="w")
        node2_cb = ttk.Combobox(self.fields_frame, values=columns, textvariable=self.node2_var, state="readonly")
        node2_cb.grid(row=1, column=1, padx=5)
        node2_cb.current(1)

        # 动态下拉框区域
        self.label_selectors = []
        self.label_selector_vars = []
        self.add_label_selector(columns)

    def add_label_selector(self, columns):
        idx = len(self.label_selectors)
        var = tk.StringVar()
        cb = ttk.Combobox(self.label_frame, values=self.get_available_label_fields(), textvariable=var, state="readonly")
        cb.grid(row=idx, column=0, sticky="w", pady=2)
        self.label_selectors.append(cb)
        self.label_selector_vars.append(var)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_label_selected(idx))

    def on_label_selected(self, idx):
        # 如果最后一个下拉框被选择，则添加新下拉框
        if idx == len(self.label_selectors) - 1 and self.label_selector_vars[idx].get():
            if len(self.get_available_label_fields()) > 0:
                self.add_label_selector(self.df.columns)
        # 更新所有下拉框的可选内容
        self.update_label_selectors()

    def get_available_label_fields(self):
        # 返回未被选择的字段
        selected = [v.get() for v in self.label_selector_vars if v.get()]
        return [c for c in self.df.columns if c not in selected]

    def update_label_selectors(self):
        selected = [v.get() for v in self.label_selector_vars if v.get()]
        for i, cb in enumerate(self.label_selectors):
            current = self.label_selector_vars[i].get()
            values = [c for c in self.df.columns if c not in selected or c == current]
            cb['values'] = values

    def generate_flow(self):
        if self.df is None:
            messagebox.showerror("错误", "请先导入数据文件")
            return
        df = self.df.copy()
        # 条件过滤
        
        # 排除流向自身
        if self.exclude_self_var.get():
            node1 = self.node1_var.get()
            node2 = self.node2_var.get()
            df = df[df[node1] != df[node2]]
        
        # 后续生成elements逻辑同前
        node1 = self.node1_var.get()
        node2 = self.node2_var.get()
        if not node1 or not node2 or node1 == node2:
            messagebox.showerror("错误", "请选择不同的节点字段")
            return
        label_fields = [v.get() for v in self.label_selector_vars if v.get()]
        if not label_fields:
            messagebox.showerror("错误", "请至少选择一个链路备注字段")
            return

        # 构造节点和边
        nodes = set(df[node1].tolist() + df[node2].tolist())
        elements = [{'data': {'id': n, 'label': n}} for n in nodes]
        for _, row in df.iterrows():
            label = ", ".join([f"{f}:{row[f]}" for f in label_fields])
            elements.append({
                'data': {
                    'source': row[node1],
                    'target': row[node2],
                    'label': label
                }
            })
        self.show_dash(elements)

    def show_dash(self, elements):
        def run_dash():
            def filter_components(run_clicks, reset_clicks, n_value, stored_elements, current_elements):
                ctx = dash.callback_context
                if not ctx.triggered:
                    return dash.no_update, dash.no_update
                
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                
                # 重置逻辑
                if trigger_id == 'reset-btn':
                    return stored_elements, stored_elements
                
                # 筛选逻辑
                if trigger_id == 'run-filter-btn' and n_value:
                    # 创建图结构
                    G = nx.Graph()
                    node_map = {}
                    
                    # 添加节点和边
                    for elem in stored_elements:
                        if 'source' in elem['data']:  # 边
                            source = elem['data']['source']
                            target = elem['data']['target']
                            G.add_edge(source, target)
                        else:  # 节点
                            node_id = elem['data']['id']
                            G.add_node(node_id)
                            node_map[node_id] = elem
                    
                    # 获取连通子图并排序
                    components = list(nx.connected_components(G))
                    sorted_components = sorted(components, 
                                            key=lambda x: len(x), 
                                            reverse=True)[:int(n_value)]
                    
                    # 构建新元素集
                    new_elements = []
                    selected_nodes = set()
                    
                    # 添加选中的节点
                    for comp in sorted_components:
                        selected_nodes.update(comp)
                        for node in comp:
                            new_elements.append(node_map[node])
                    
                    # 添加关联的边
                    for elem in stored_elements:
                        if 'source' in elem['data']:
                            source = elem['data']['source']
                            target = elem['data']['target']
                            if source in selected_nodes and target in selected_nodes:
                                new_elements.append(elem)
                    
                    return new_elements, stored_elements
                
                return current_elements, stored_elements

            import dash
            from dash import html, dcc, Output, Input, State, callback_context
            import dash_cytoscape as cyto

            app = dash.Dash()
            # 初始参数
            default_layout = {'name': 'breadthfirst'}
            default_edge_style = 'bezier'
            default_font_size = 16
            default_edge_width = 2
            default_edge_color = '#888'  # 默认线条颜色
            default_font_color = '#000'  # 默认字体颜色
            default_node_color = '#000'  # 默认节点颜色

            app.layout = html.Div([
                html.Div([
                    html.Button("一键重新分布", id="btn-layout", n_clicks=0, style={"marginRight": "10px"}),
                    # 新增的"切换布局样式"按钮
                    html.Button("切换布局样式", id="btn-layout-style", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("切换链路样式", id="btn-style", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体放大", id="btn-font-up", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体缩小", id="btn-font-down", n_clicks=0, style={"marginRight": "10px"}),
                    # 复制按钮
                    dcc.Clipboard(
                        id="cytoscape-copy",
                        title="复制图表信息",
                        style={
                            "display": "inline-block",
                            "fontSize": 20,
                            "verticalAlign": "top",
                            "cursor": "pointer",
                            "marginRight": "10px"
                        }
                    ),
                    # 新增按钮
                    html.Button("线条加粗", id="btn-line-thicker", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("线条变细", id="btn-line-thinner", n_clicks=0, style={"marginRight": "10px"}),
                ], style={"marginBottom": "10px", "display": "flex", "flexWrap": "wrap", "alignItems": "center"}),
                
                # 新增组件：链路组数筛选
                html.Div([
                    dcc.Input(
                        id='component-limit-input',
                        type='number',
                        min=1,
                        placeholder='限定链路数量（按长度）',
                        style={'width': '180px', 'marginRight': '10px'}
                    ),
                    html.Button('运行', id='run-filter-btn', n_clicks=0, style={'marginRight': '10px'}),
                    html.Button('重置', id='reset-btn', n_clicks=0)
                ], style={'marginBottom': '10px'}),
                
                dcc.Store(id='original-elements-store', data=elements),  # 存储原始数据
                
                # 颜色控制区域
                html.Div([
                    # 线条颜色
                    html.Div([
                        html.Label("线条颜色: ", style={'marginRight': '5px'}),
                        dcc.Input(
                            id='edge-color-picker',
                            type='text',
                            value=default_edge_color,
                            style={'width': '80px', 'marginRight': '10px'}
                        ),
                        html.Div(
                            id='edge-color-preview',
                            style={
                                'width': '30px',
                                'height': '20px',
                                'background': default_edge_color,
                                'display': 'inline-block',
                                'border': '1px solid #000',
                                'verticalAlign': 'middle'
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '20px'}),
                    
                    # 字体颜色
                    html.Div([
                        html.Label("字体颜色: ", style={'marginRight': '5px'}),
                        dcc.Input(
                            id='font-color-picker',
                            type='text',
                            value=default_font_color,
                            style={'width': '80px', 'marginRight': '10px'}
                        ),
                        html.Div(
                            id='font-color-preview',
                            style={
                                'width': '30px',
                                'height': '20px',
                                'background': default_font_color,
                                'display': 'inline-block',
                                'border': '1px solid #000',
                                'verticalAlign': 'middle'
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '20px'}),
                    
                    # 节点颜色
                    html.Div([
                        html.Label("节点颜色: ", style={'marginRight': '5px'}),
                        dcc.Input(
                            id='node-color-picker',
                            type='text',
                            value=default_node_color,
                            style={'width': '80px', 'marginRight': '10px'}
                        ),
                        html.Div(
                            id='node-color-preview',
                            style={
                                'width': '30px',
                                'height': '20px',
                                'background': default_node_color,
                                'display': 'inline-block',
                                'border': '1px solid #000',
                                'verticalAlign': 'middle'
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={"marginBottom": "10px"}),
                
                cyto.Cytoscape(
                    id='cytoscape',
                    elements=elements,
                    layout=default_layout,
                    style={'width': '100%', 'height': '600px'},
                    stylesheet=[
                        {
                            'selector': 'edge',
                            'style': {
                                'curve-style': default_edge_style,
                                'target-arrow-shape': 'triangle',
                                'label': 'data(label)',
                                'font-size': '12px',
                                'width': default_edge_width,
                                'line-color': default_edge_color,
                                'color': default_font_color  # 边标签字体颜色
                            }
                        },
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)',
                                'font-size': f'{default_font_size}px',
                                'background-color': default_node_color,  # 节点背景色
                                'color': default_font_color  # 节点标签字体颜色
                            }
                        }
                    ]
                )
            ])

            # 状态变量
            edge_styles = ['bezier', 'straight', 'taxi', 'unbundled-bezier', 'haystack']
            layout_types = ['breadthfirst', 'circle', 'grid', 'cose', 'concentric', 'random']  # 增加random布局
            font_size = [default_font_size]
            edge_style_idx = [0]
            layout_idx = [0]  # 用于"一键重新分布"的布局索引
            layout_style_idx = [0]  # 用于"切换布局样式"的新布局索引
            edge_width = [default_edge_width]  # 线条粗细状态
            edge_color = [default_edge_color]   # 线条颜色状态
            font_color = [default_font_color]   # 字体颜色状态
            node_color = [default_node_color]   # 节点颜色状态

            @app.callback(
                Output('cytoscape', 'layout'),
                Input('btn-layout', 'n_clicks'),
                prevent_initial_call=True
            )
            def update_layout(n_clicks):
                layout_idx[0] = (layout_idx[0] + 1) % len(layout_types)
                return {
                    'name': layout_types[layout_idx[0]],
                    'animate': True,  # 启用动画
                    'animationDuration': 500  # 动画持续时间500ms
                }

            # 新增的布局样式切换回调
            @app.callback(
                Output('cytoscape', 'layout', allow_duplicate=True),
                Input('btn-layout-style', 'n_clicks'),
                prevent_initial_call=True
            )
            def update_layout_style(n_clicks):
                # 循环切换布局类型
                layout_style_idx[0] = (layout_style_idx[0] + 1) % len(layout_types)
                new_layout = layout_types[layout_style_idx[0]]
                
                # 添加动画效果（平滑过渡）
                return {
                    'name': new_layout,
                    'animate': True,  # 启用动画
                    'animationDuration': 500,  # 动画持续时间500ms
                    'fit': True,  # 自动适应视图
                    'padding': 30  # 布局内边距
                }

            @app.callback(
                Output('cytoscape', 'stylesheet'),
                Input('btn-style', 'n_clicks'),
                Input('btn-font-up', 'n_clicks'),
                Input('btn-font-down', 'n_clicks'),
                Input('btn-line-thicker', 'n_clicks'),
                Input('btn-line-thinner', 'n_clicks'),
                Input('edge-color-picker', 'value'),
                Input('font-color-picker', 'value'),
                Input('node-color-picker', 'value'),
                State('cytoscape', 'stylesheet'),
                prevent_initial_call=True
            )
            def update_style(n_style, n_up, n_down, n_thicker, n_thinner, 
                            edge_color_value, font_color_value, node_color_value, stylesheet):
                ctx = callback_context
                if not ctx.triggered:
                    return stylesheet
                
                btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
                updated = False
                
                # 切换链路样式
                if btn_id == 'btn-style':
                    edge_style_idx[0] = (edge_style_idx[0] + 1) % len(edge_styles)
                    updated = True
                
                # 字体放大
                elif btn_id == 'btn-font-up':
                    font_size[0] = min(font_size[0] + 2, 40)
                    updated = True
                
                # 字体缩小
                elif btn_id == 'btn-font-down':
                    font_size[0] = max(font_size[0] - 2, 8)
                    updated = True
                
                # 线条加粗
                elif btn_id == 'btn-line-thicker':
                    edge_width[0] = min(edge_width[0] + 1, 10)  # 最大宽度为10
                    updated = True
                
                # 线条变细
                elif btn_id == 'btn-line-thinner':
                    edge_width[0] = max(edge_width[0] - 1, 1)  # 最小宽度为1
                    updated = True
                
                # 颜色更新
                elif btn_id == 'edge-color-picker':
                    edge_color[0] = edge_color_value
                    updated = True
                elif btn_id == 'font-color-picker':
                    font_color[0] = font_color_value
                    updated = True
                elif btn_id == 'node-color-picker':
                    node_color[0] = node_color_value
                    updated = True
                
                if updated:
                    # 更新节点样式
                    for style in stylesheet:
                        if style['selector'] == 'node':
                            style['style']['font-size'] = f'{font_size[0]}px'
                            style['style']['color'] = font_color[0]
                            style['style']['background-color'] = node_color[0]
                    
                    # 更新边样式
                    for style in stylesheet:
                        if style['selector'] == 'edge':
                            style['style']['curve-style'] = edge_styles[edge_style_idx[0]]
                            style['style']['width'] = edge_width[0]
                            style['style']['line-color'] = edge_color[0]
                            style['style']['color'] = font_color[0]
                
                updated_stylesheet = stylesheet.copy()
                return updated_stylesheet

            @app.callback(
                [Output('cytoscape', 'elements'), Output('original-elements-store', 'data')],
                [Input('run-filter-btn', 'n_clicks'), Input('reset-btn', 'n_clicks')],
                [State('component-limit-input', 'value'), 
                 State('original-elements-store', 'data'),
                 State('cytoscape', 'elements')],
                prevent_initial_call=True
            )
            def update_elements(run_clicks, reset_clicks, n_value, stored_elements, current_elements):
                return filter_components(run_clicks, reset_clicks, n_value, stored_elements, current_elements)

            @app.callback(
                [Output('edge-color-preview', 'style'), 
                 Output('font-color-preview', 'style'),
                 Output('node-color-preview', 'style')],
                [Input('edge-color-picker', 'value'),
                 Input('font-color-picker', 'value'),
                 Input('node-color-picker', 'value')]
            )
            def update_color_previews(edge_color, font_color, node_color):
                edge_style = {
                    'width': '30px',
                    'height': '20px',
                    'background': edge_color,
                    'display': 'inline-block',
                    'border': '1px solid #000',
                    'verticalAlign': 'middle'
                }
                font_style = {
                    'width': '30px',
                    'height': '20px',
                    'background': font_color,
                    'display': 'inline-block',
                    'border': '1px solid #000',
                    'verticalAlign': 'middle'
                }
                node_style = {
                    'width': '30px',
                    'height': '20px',
                    'background': node_color,
                    'display': 'inline-block',
                    'border': '1px solid #000',
                    'verticalAlign': 'middle'
                }
                return edge_style, font_style, node_style

            app.run(debug=False)

        # 在新线程中运行Dash应用
        threading.Thread(target=run_dash, daemon=True).start()
        webbrowser.open_new_tab('http://127.0.0.1:8050/')

