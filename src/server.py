# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from gobench import go_benchmark_functions
from gobench.go_benchmark_functions import Benchmark

from src.app import Surface, Space, functions

functionsDict = {}
for f in functions():
    name = str(f).split('.')[-1][:-2]
    functionsDict[name] = f

space = Space(go_benchmark_functions.Damavandi)
surface = Surface(space, step=101, zoom=10)

countour2D = go.Figure()
countour2D.add_contour(x=surface.x, y=surface.y, z=surface.zz)
countour2D.add_scatter(x=[1, 2, 3], y=[1, 2, 3])

countour2D_zoom = go.Figure()
countour2D_zoom.add_contour(x=surface.xZoom, y=surface.yZoom, z=surface.zzZoom)
countour2D_zoom.add_scatter(x=[1, 2, 3], y=[1, 2, 3])

surface3D = go.Figure()
surface3D.add_surface(x=surface.x, y=surface.y, z=surface.zz)
surface3D.add_scatter3d(x=[1, 2, 3], y=[1, 2, 3], z=[1, 2, 3])

app = dash.Dash(__name__)
app.layout = html.Div(children=[

    html.Div([
        dcc.Dropdown(
            id='function-name',
            options=[{'label': str(i), 'value': str(i)} for i in list(functionsDict.keys())],
            value='Test function',
            style={'width': '300px', 'float': 'left'}
        ),
        dcc.RadioItems(
            id='dimensionality',
            options=[{'label': i, 'value': i} for i in ['3D', '2D']],
            value='2D',
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
        dcc.RadioItems(
            id='drawing-style',
            options=[{'label': i, 'value': i} for i in ['WIRES', 'POINTS']],
            value='POINTS',
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
    ], style={'display': 'inline-block', 'margin-left': '35%'}),

    html.Div(children=[
        dcc.Graph(
            id='countour2d_zoom',
            figure=countour2D_zoom,
            style={'float': 'right', 'width': '50%', 'height': '100%'}
        ),
        dcc.Graph(
            id='countour2d',
            figure=countour2D,
            style={'float': 'left', 'width': '50%', 'height': '100%'},
        )
    ], style={'height': '90vh'})
])

@app.callback(
    Output('countour2d', 'figure'),
    Input('function-name', 'value'),
    Input('dimensionality', 'value'),
    Input('drawing-style', 'value'))
def update_graph(functionName, dimensionality, drawingStyle):
    print(functionName, dimensionality, drawingStyle)
    countour2D = go.Figure()
    countour2D.add_contour(x=surface.x, y=surface.y, z=surface.zz)
    countour2D.add_scatter(x=[1, 2, 3], y=[1, 2, 3])
    return countour2D
if __name__ == '__main__':
    app.run_server(debug=True)
