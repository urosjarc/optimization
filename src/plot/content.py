import random

import dash_core_components as dcc
import dash_html_components as html

from src.math.optimization import functions, function_dim, Function
from src.plot.graph import Surface

surface: Surface = Surface(step=51, zoom=10)
function: Function = None
optimizer = None
points = [[], [], []]

functionsDict = {name: fun for name, fun in functions().items() if function_dim(fun) == 2}
dimensionality = '3D'
log = 'Normal'
startCount = 0
stopCount = 0
running = False

layout = html.Div(children=[

    dcc.Interval(id='interval'),

    html.Div([
        dcc.Dropdown(
            id='function-name',
            options=[{'label': str(key), 'value': str(key)} for key, val in functionsDict.items()],
            value=random.choice(list(functionsDict.keys())),
            style={'width': '300px', 'float': 'left'}
        ),
        html.Button(
            "Star",
            id='start',
            n_clicks=0,
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
        dcc.RadioItems(
            id='log',
            options=[{'label': i, 'value': i} for i in ['Normal', 'Log']],
            value=log,
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
        dcc.RadioItems(
            id='intervalTime',
            value=3600 * 1000,
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'},
            options=[
                {'label': 'Play', 'value': 1000},
                {'label': 'Pause', 'value': 60 * 60 * 1000}  # or just every hour
            ]),
        dcc.Dropdown(
            id='evaluations',
            options=[{'label': str(val)+'E', 'value': str(val)} for val in [1, 10, 20, 50, 100]],
            value='10',
            style={'width': '200px', 'float': 'left', 'margin-left': '20px'}
        ),

        html.Div(id="info", children=['Evaluation: 0'], style={'width': '200px', 'float': 'right', 'margin-top': '7px'}),

    ], style={'position': 'fixed', 'padding': '10px', 'left': '0', 'width': '100%', 'top': '0', 'z-index': '999', 'background-color': '#cccccc'}),

    html.Div(children=[
        dcc.Graph(id='graph2D', style={'float': 'right', 'height': '90vh', 'width': '50%'}),
        dcc.Graph(id='graph3D', style={'float': 'left', 'height': '90vh', 'width': '50%'}),
        dcc.Graph(id='graph2D_zoom', style={'float': 'right', 'height': '90vh', 'width': '50%'}),
        dcc.Graph(id='graph3D_zoom', style={'float': 'left', 'height': '90vh', 'width': '50%'})
    ])
])
