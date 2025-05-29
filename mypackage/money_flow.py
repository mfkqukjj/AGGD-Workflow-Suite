import dash
from dash import html
import dash_cytoscape as cyto

app = dash.Dash(__name__)
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=[
            # 节点
            {'data': {'id': '周大', 'label': '周大'}},
            {'data': {'id': '张三', 'label': '张三'}},
            {'data': {'id': '李四', 'label': '李四'}},
            {'data': {'id': '赵六', 'label': '赵六'}},
            {'data': {'id': '钱七', 'label': '钱七'}},
            {'data': {'id': '孙八', 'label': '孙八'}},
           
            # 边（资金流向）
            {'data': {
                'source': '周大', 
                'target': '张三',
                'label': '3笔,共2000元'
            }},
            {'data': {
                'source': '张三', 
                'target': '李四',
                'label': '5笔,共1500元'
            }},
            {'data': {
                'source': '李四', 
                'target': '张三',
                'label': '1000元'
            }},
            {'data': {
                'source': '赵六', 
                'target': '孙八',
                'label': '1000元'
            }},
            {'data': {
                'source': '李四', 
                'target': '钱七',
                'label': '1000元'
            }},{'data': {
                'source': '张三', 
                'target': '孙八',
                'label': '1000元'
            }},{'data': {
                'source': '李四', 
                'target': '张三',
                'label': '2000元'
            }},
            
        ],
        layout={'name': 'breadthfirst'},
        style={'width': '100%', 'height': '600px'},
        stylesheet=[
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'label': 'data(label)',
                    'font-size': '12px'
                }
            },
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'font-size': '16px'
                }
            }
        ]
    )
])

if __name__ == '__main__':
    app.run(debug=True)