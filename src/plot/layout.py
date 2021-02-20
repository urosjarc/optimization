import sys

from src.math.optimization import functions, Function
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from src.plot.graph import Surface
from gobench import go_benchmark_functions

this = sys.modules[__name__]
surface = None
this.surface = surface

def callback(functionName, dimensionality):
    if this.surface != functionName:
        fun = functions(functionName)
        optFun = Function(go_benchmark_functions.Damavandi,randomize=False)
        this.surface = Surface(optFun, step=101, zoom=10)

    if dimensionality == '2D':
        countour2D = go.Figure()
        countour2D.add_contour(x=surface.x, y=surface.y, z=surface.z)
        countour2D.add_scatter(x=[1, 2, 3], y=[1, 2, 3])
        countour2D_zoom = go.Figure()
        countour2D_zoom.add_contour(x=surface.xZoom, y=surface.yZoom, z=surface.zZoom)
        countour2D_zoom.add_scatter(x=[1, 2, 3], y=[1, 2, 3])
        return countour2D, countour2D_zoom
    else:
        surface3D = go.Figure()
        surface3D.add_surface(x=surface.x, y=surface.y, z=surface.z)
        surface3D.add_scatter3d(x=[1, 2, 3], y=[1, 2, 3], z=[1, 2, 3])
        surface3D_zoom = go.Figure()
        surface3D_zoom.add_surface(x=surface.xZoom, y=surface.yZoom, z=surface.zZoom)
        surface3D_zoom.add_scatter3d(x=[1, 2, 3], y=[1, 2, 3], z=[1, 2, 3])
        return surface3D, surface3D_zoom

div = html.Div(children=[

    html.Div([
        dcc.Dropdown(
            id='function-name',
            options=[{'label': str(i), 'value': str(i)} for i in list(functions().keys())],
            style={'width': '300px', 'float': 'left'}
        ),
        dcc.RadioItems(
            id='dimensionality',
            options=[{'label': i, 'value': i} for i in ['3D', '2D']],
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        )
    ], style={'display': 'inline-block', 'margin-left': '35%'}),

    html.Div(children=[
        dcc.Graph(
            id='graph_zoom',
            style={'float': 'right', 'width': '50%', 'height': '100%'}
        ),
        dcc.Graph(
            id='graph',
            style={'float': 'left', 'width': '50%', 'height': '100%'},
        )
    ], style={'height': '90vh'}),
])