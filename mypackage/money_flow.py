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
import re
import networkx as nx

class MoneyFlowViewer(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("自定义流向图")
        self.geometry("650x550")
        self.grab_set()
        self.df = None
        self.node1_var = tk.StringVar()
        self.node2_var = tk.StringVar()
        self.node1_custom_var = tk.StringVar()
        self.node2_custom_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="normal")
        self.label_fields = []
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        # 主框架使用垂直堆叠布局
        main_frame = ttk.Frame(frm)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件导入区
        filefrm = ttk.Frame(main_frame)
        filefrm.pack(fill=tk.X, pady=5)
        ttk.Label(filefrm, text="导入Excel/CSV文件：").pack(side=tk.LEFT)
        ttk.Button(filefrm, text="浏览", command=self.load_file).pack(side=tk.LEFT, padx=5)
        
        # 模式选择区
        mode_frame = ttk.LabelFrame(main_frame, text="选择节点模式", padding=5)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            mode_frame, text="普通模式", 
            variable=self.mode_var, value="normal",
            command=self.toggle_mode
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            mode_frame, text="自定义模式", 
            variable=self.mode_var, value="custom",
            command=self.toggle_mode
        ).pack(side=tk.LEFT, padx=10)
        
        self.mode_hint = ttk.Label(mode_frame, text="(普通模式: 直接选择字段作为节点)")
        self.mode_hint.pack(side=tk.LEFT, padx=5)
        
        # 节点字段容器 - 关键修改点
        self.node_fields_container = ttk.Frame(main_frame)
        self.node_fields_container.pack(fill=tk.X, pady=5)
        
        # 普通模式字段区
        self.fields_frame = ttk.LabelFrame(self.node_fields_container, text="请选择节点字段", padding=10)
        self.fields_frame.pack(fill=tk.X)
        
        # 自定义模式字段区
        self.custom_fields_frame = ttk.LabelFrame(self.node_fields_container, text="自定义节点格式", padding=10)
        
        # 链路备注区
        self.label_frame = ttk.LabelFrame(main_frame, text="链路备注内容（可多选）", padding=10)
        self.label_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 条件区
        self.cond_frame = ttk.LabelFrame(main_frame, text="条件区", padding=10)
        self.cond_frame.pack(fill=tk.X, pady=5)

        # 生成按钮
        ttk.Button(main_frame, text="生成流向图", command=self.generate_flow).pack(pady=10)

        # 排除自身选项
        self.exclude_self_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.cond_frame, text="排除流向自身", variable=self.exclude_self_var).grid(row=0, column=0, sticky="w")
        
        # 初始显示普通模式
        self.toggle_mode()

    def toggle_mode(self):
        mode = self.mode_var.get()
        
        # 清空容器内的所有控件
        for widget in self.node_fields_container.winfo_children():
            widget.pack_forget()
        
        if mode == "normal":
            self.mode_hint.config(text="(普通模式: 直接选择字段作为节点)")
            self.fields_frame.pack(fill=tk.X)  # 在容器内显示普通模式
        else:
            self.mode_hint.config(text="(自定义模式: 使用{}包含字段名，如 '{姓名} ({身份证号})')")
            self.setup_custom_fields()
            self.custom_fields_frame.pack(fill=tk.X)  # 在容器内显示自定义模式
            
        # 如果已加载文件，更新字段选择器
        if self.df is not None:
            self.show_field_selectors()

    def setup_custom_fields(self):
        for widget in self.custom_fields_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.custom_fields_frame, text="节点1格式（起点）：").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        node1_entry = ttk.Entry(self.custom_fields_frame, textvariable=self.node1_custom_var, width=40)
        node1_entry.grid(row=0, column=1, padx=5, pady=2, sticky="we")
        
        ttk.Label(self.custom_fields_frame, text="节点2格式（终点）：").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        node2_entry = ttk.Entry(self.custom_fields_frame, textvariable=self.node2_custom_var, width=40)
        node2_entry.grid(row=1, column=1, padx=5, pady=2, sticky="we")
        
        fields_info = ttk.Label(
            self.custom_fields_frame, 
            text="提示: 使用大括号{}包裹字段名，如 '{姓名}（身份证号:{身份证号}）'"
        )
        fields_info.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

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
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        columns = list(self.df.columns)
        if len(columns) < 2:
            messagebox.showerror("错误", "数据字段不足")
            return

        mode = self.mode_var.get()
        
        if mode == "normal":
            ttk.Label(self.fields_frame, text="节点字段1（起点）：").grid(row=0, column=0, sticky="w")
            node1_cb = ttk.Combobox(self.fields_frame, values=columns, textvariable=self.node1_var, state="readonly")
            node1_cb.grid(row=0, column=1, padx=5, sticky="we")
            node1_cb.current(0)

            ttk.Label(self.fields_frame, text="节点字段2（终点）：").grid(row=1, column=0, sticky="w")
            node2_cb = ttk.Combobox(self.fields_frame, values=columns, textvariable=self.node2_var, state="readonly")
            node2_cb.grid(row=1, column=1, padx=5, sticky="we")
            node2_cb.current(1 if len(columns) > 1 else 0)
            
            ttk.Label(self.fields_frame, 
                     text="提示: 直接选择字段作为节点").grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        self.label_selectors = []
        self.label_selector_vars = []
        self.add_label_selector(columns)
        
        hint_label = ttk.Label(
            self.label_frame,
            text="提示: 选择要显示在边上的备注信息（可多选）"
        )
        hint_label.pack(anchor="w", padx=5, pady=2)

    def add_label_selector(self, columns):
        idx = len(self.label_selectors)
        var = tk.StringVar()
        
        row_frame = ttk.Frame(self.label_frame)
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(row_frame, text=f"备注字段 {idx+1}:").pack(side=tk.LEFT, padx=(0, 5))
        cb = ttk.Combobox(row_frame, values=self.get_available_label_fields(), textvariable=var, state="readonly", width=30)
        cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if idx > 0:
            del_btn = ttk.Button(
                row_frame, text="×", width=2,
                command=lambda idx=idx: self.remove_label_selector(idx)
            )
            del_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.label_selectors.append(cb)
        self.label_selector_vars.append(var)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_label_selected(idx))

    def remove_label_selector(self, idx):
        self.label_selectors[idx].destroy()
        self.label_selector_vars.pop(idx)
        self.label_selectors.pop(idx)
        
        self.update_label_selectors()
        
        if len(self.label_selectors) == 1 and not self.label_selector_vars[0].get():
            self.add_label_selector(self.df.columns)

    def on_label_selected(self, idx):
        if idx == len(self.label_selectors) - 1 and self.label_selector_vars[idx].get():
            if len(self.get_available_label_fields()) > 0:
                self.add_label_selector(self.df.columns)
        self.update_label_selectors()

    def get_available_label_fields(self):
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
        mode = self.mode_var.get()
        
        if mode == "normal":
            node1_field = self.node1_var.get()
            node2_field = self.node2_var.get()
            
            if not node1_field or not node2_field or node1_field == node2_field:
                messagebox.showerror("错误", "请选择不同的节点字段")
                return
                
            node1_values = df[node1_field].astype(str)
            node2_values = df[node2_field].astype(str)
            
        else:
            node1_format = self.node1_custom_var.get().strip()
            node2_format = self.node2_custom_var.get().strip()
            
            if not node1_format or not node2_format:
                messagebox.showerror("错误", "自定义节点格式不能为空")
                return
                
            node1_values = df.apply(lambda row: self.format_custom_node(row, node1_format), axis=1)
            node2_values = df.apply(lambda row: self.format_custom_node(row, node2_format), axis=1)
            
            node1_field = "__node1_custom"
            node2_field = "__node2_custom"
            df[node1_field] = node1_values
            df[node2_field] = node2_values

        if self.exclude_self_var.get():
            df = df[df[node1_field] != df[node2_field]]
        
        label_fields = [v.get() for v in self.label_selector_vars if v.get()]
        if not label_fields:
            messagebox.showerror("错误", "请至少选择一个链路备注字段")
            return

        nodes = set(df[node1_field].tolist() + df[node2_field].tolist())
        elements = [{'data': {'id': n, 'label': n}} for n in nodes]
        
        for _, row in df.iterrows():
            label = ", ".join([f"{f}:{row[f]}" for f in label_fields])
            elements.append({
                'data': {
                    'source': row[node1_field],
                    'target': row[node2_field],
                    'label': label
                }
            })
            
        self.show_dash(elements)

    def format_custom_node(self, row, pattern):
        matches = re.findall(r'\{([^{}]+)\}', pattern)
        
        formatted = pattern
        for field in matches:
            if field in row:
                formatted = formatted.replace(f'{{{field}}}', str(row[field]))
        
        return formatted

    def show_dash(self, elements):
        def run_dash():
            def filter_components(run_clicks, reset_clicks, n_value, stored_elements, current_elements):
                ctx = dash.callback_context
                if not ctx.triggered:
                    return dash.no_update, dash.no_update
                
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                
                if trigger_id == 'reset-btn':
                    return stored_elements, stored_elements
                
                if trigger_id == 'run-filter-btn' and n_value:
                    G = nx.Graph()
                    node_map = {}
                    
                    for elem in stored_elements:
                        if 'source' in elem['data']:
                            source = elem['data']['source']
                            target = elem['data']['target']
                            G.add_edge(source, target)
                        else:
                            node_id = elem['data']['id']
                            G.add_node(node_id)
                            node_map[node_id] = elem
                    
                    components = list(nx.connected_components(G))
                    sorted_components = sorted(components, 
                                            key=lambda x: len(x), 
                                            reverse=True)[:int(n_value)]
                    
                    new_elements = []
                    selected_nodes = set()
                    
                    for comp in sorted_components:
                        selected_nodes.update(comp)
                        for node in comp:
                            new_elements.append(node_map[node])
                    
                    for elem in stored_elements:
                        if 'source' in elem['data']:
                            source = elem['data']['source']
                            target = elem['data']['target']
                            if source in selected_nodes and target in selected_nodes:
                                new_elements.append(elem)
                    
                    return new_elements, stored_elements
                
                return current_elements, stored_elements

            default_layout = {'name': 'breadthfirst'}
            default_edge_style = 'bezier'
            default_font_size = 16
            default_edge_width = 2
            default_edge_color = '#888'
            default_font_color = '#000'
            default_node_color = '#000'

            app = dash.Dash()
            app.layout = html.Div([
                html.Div([
                    html.Button("一键重新分布", id="btn-layout", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("切换链路样式", id="btn-style", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体放大", id="btn-font-up", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体缩小", id="btn-font-down", n_clicks=0, style={"marginRight": "10px"}),
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
                    html.Button("线条加粗", id="btn-line-thicker", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("线条变细", id="btn-line-thinner", n_clicks=0, style={"marginRight": "10px"}),
                ], style={"marginBottom": "10px", "display": "flex", "flexWrap": "wrap", "alignItems": "center"}),
                
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
                
                dcc.Store(id='original-elements-store', data=elements),
                
                html.Div([
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
                                'color': default_font_color
                            }
                        },
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)',
                                'font-size': f'{default_font_size}px',
                                'background-color': default_node_color,
                                'color': default_font_color
                            }
                        }
                    ]
                )
            ])
            
            edge_styles = ['bezier', 'straight', 'taxi', 'unbundled-bezier', 'haystack']
            layout_types = ['breadthfirst', 'circle', 'grid', 'cose', 'concentric']
            font_size = [default_font_size]
            edge_style_idx = [0]
            layout_idx = [0]
            edge_width = [default_edge_width]
            edge_color = [default_edge_color]
            font_color = [default_font_color]
            node_color = [default_node_color]
            
            @app.callback(
                Output('cytoscape', 'layout'),
                Output('original-elements-store', 'data'),
                Input('btn-layout', 'n_clicks'),
                State('original-elements-store', 'data'),
                prevent_initial_call=True
            )
            def update_layout(n_clicks, stored_elements):
                layout_idx[0] = (layout_idx[0] + 1) % len(layout_types)
                return {'name': layout_types[layout_idx[0]]}, stored_elements
            
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
                ctx = dash.callback_context
                if not ctx.triggered:
                    return stylesheet
                
                btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
                updated = False
                
                if btn_id == 'btn-style':
                    edge_style_idx[0] = (edge_style_idx[0] + 1) % len(edge_styles)
                    updated = True
                
                elif btn_id == 'btn-font-up':
                    font_size[0] = min(font_size[0] + 2, 40)
                    updated = True
                
                elif btn_id == 'btn-font-down':
                    font_size[0] = max(font_size[0] - 2, 8)
                    updated = True
                
                elif btn_id == 'btn-line-thicker':
                    edge_width[0] = min(edge_width[0] + 1, 10)
                    updated = True
                
                elif btn_id == 'btn-line-thinner':
                    edge_width[0] = max(edge_width[0] - 1, 1)
                    updated = True
                
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
                    new_stylesheet = [
                        {
                            'selector': 'edge',
                            'style': {
                                'curve-style': edge_styles[edge_style_idx[0]],
                                'target-arrow-shape': 'triangle',
                                'label': 'data(label)',
                                'font-size': '12px',
                                'width': edge_width[0],
                                'line-color': edge_color[0],
                                'color': font_color[0]
                            }
                        },
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)',
                                'font-size': f'{font_size[0]}px',
                                'background-color': node_color[0],
                                'color': font_color[0]
                            }
                        }
                    ]
                    return new_stylesheet
                
                return stylesheet
            
            @app.callback(
                Output('cytoscape', 'elements'),
                Output('original-elements-store', 'data', allow_duplicate=True),
                Input('run-filter-btn', 'n_clicks'),
                Input('reset-btn', 'n_clicks'),
                State('component-limit-input', 'value'),
                State('original-elements-store', 'data'),
                State('cytoscape', 'elements'),
                prevent_initial_call=True
            )
            def update_filter(run_clicks, reset_clicks, n_value, stored_elements, current_elements):
                return filter_components(run_clicks, reset_clicks, n_value, stored_elements, current_elements)
            
            @app.callback(
                Output('edge-color-preview', 'style'),
                Input('edge-color-picker', 'value')
            )
            def update_edge_color_preview(color):
                return {'background': color, 'width': '30px', 'height': '20px', 'display': 'inline-block', 'border': '1px solid #000', 'verticalAlign': 'middle'}
            
            @app.callback(
                Output('font-color-preview', 'style'),
                Input('font-color-picker', 'value')
            )
            def update_font_color_preview(color):
                return {'background': color, 'width': '30px', 'height': '20px', 'display': 'inline-block', 'border': '1px solid #000', 'verticalAlign': 'middle'}
            
            @app.callback(
                Output('node-color-preview', 'style'),
                Input('node-color-picker', 'value')
            )
            def update_node_color_preview(color):
                return {'background': color, 'width': '30px', 'height': '20px', 'display': 'inline-block', 'border': '1px solid #000', 'verticalAlign': 'middle'}
            
            port = 8050
            webbrowser.open(f"http://localhost:{port}")
            app.run(port=port)

        threading.Thread(target=run_dash, daemon=True).start()