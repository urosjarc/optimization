import random

import dash_core_components as dcc
import dash_html_components as html

from src.math.optimization import functions, function_dim
from src.plot.graph import Surface

surface: Surface = Surface(step=101, zoom=10)
function = None
optimizer = None
points = [[],[],[]]

functionsDict = {name: fun for name, fun in functions().items() if function_dim(fun) == 2}
startCount = 0
stopCount = 0
start = False

layout = html.Div(children=[
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
        html.Button(
            "Stop",
            id='stop',
            n_clicks=0,
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
        dcc.RadioItems(
            id='dimensionality',
            options=[{'label': i, 'value': i} for i in ['3D', '2D']],
            value='3D',
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        ),
        dcc.RadioItems(
            id='log',
            options=[{'label': i, 'value': i} for i in ['Normal', 'Log']],
            value='Normal',
            style={'float': 'left', 'margin-left': '20px', 'margin-top': '7px'}
        )
    ], style={'display': 'inline-block', 'margin-left': '35%'}),

    dcc.Loading(id="loading", children=[
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
    ], type="cube"),
])
