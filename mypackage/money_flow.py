import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import dash
from dash import html
import dash_cytoscape as cyto
import threading
import webbrowser

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
        ttk.Label(self.fields_frame, text="节点字段1（起点").grid(row=0, column=0, sticky="w")
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
            import dash
            from dash import html, dcc, Output, Input, State, callback_context
            import dash_cytoscape as cyto

            app = dash.Dash(__name__)
            # 初始参数
            default_layout = {'name': 'breadthfirst'}
            default_edge_style = 'bezier'
            default_font_size = 16

            app.layout = html.Div([
                html.Div([
                    html.Button("一键重新分布", id="btn-layout", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("切换链路样式", id="btn-style", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体放大", id="btn-font-up", n_clicks=0, style={"marginRight": "10px"}),
                    html.Button("字体缩小", id="btn-font-down", n_clicks=0),
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
                                'font-size': '12px'
                            }
                        },
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)',
                                'font-size': f'{default_font_size}px'
                            }
                        }
                    ]
                )
            ])

            # 状态变量
            edge_styles = ['bezier', 'straight', 'taxi', 'unbundled-bezier', 'haystack']
            layout_types = ['breadthfirst', 'circle', 'grid', 'cose', 'concentric']
            font_size = [default_font_size]
            edge_style_idx = [0]
            layout_idx = [0]

            @app.callback(
                Output('cytoscape', 'layout'),
                Input('btn-layout', 'n_clicks'),
                prevent_initial_call=True
            )
            def update_layout(n_clicks):
                layout_idx[0] = (layout_idx[0] + 1) % len(layout_types)
                return {'name': layout_types[layout_idx[0]]}

            @app.callback(
                Output('cytoscape', 'stylesheet'),
                Input('btn-style', 'n_clicks'),
                Input('btn-font-up', 'n_clicks'),
                Input('btn-font-down', 'n_clicks'),
                State('cytoscape', 'stylesheet'),
                prevent_initial_call=True
            )
            def update_style(n_style, n_up, n_down, stylesheet):
                ctx = callback_context
                if not ctx.triggered:
                    raise dash.exceptions.PreventUpdate
                btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
                # 当前样式
                edge_style = edge_styles[edge_style_idx[0]]
                node_font = font_size[0]
                edge_font = 12
                if btn_id == 'btn-style':
                    edge_style_idx[0] = (edge_style_idx[0] + 1) % len(edge_styles)
                    edge_style = edge_styles[edge_style_idx[0]]
                elif btn_id == 'btn-font-up':
                    font_size[0] = min(font_size[0] + 2, 40)
                    node_font = font_size[0]
                elif btn_id == 'btn-font-down':
                    font_size[0] = max(font_size[0] - 2, 8)
                    node_font = font_size[0]
                return [
                    {
                        'selector': 'edge',
                        'style': {
                            'curve-style': edge_style,
                            'target-arrow-shape': 'triangle',
                            'label': 'data(label)',
                            'font-size': f'{edge_font}px'
                        }
                    },
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'font-size': f'{node_font}px'
                        }
                    }
                ]

            threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8050")).start()
            app.run(debug=False, port=8050, use_reloader=False)
        threading.Thread(target=run_dash, daemon=True).start()
        messagebox.showinfo("提示", "流向图将在浏览器中打开！")