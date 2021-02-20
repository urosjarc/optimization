from dash import dash
from dash.dependencies import Input, Output
from src.plot import layout

app = dash.Dash(__name__)
app.layout = layout.div

@app.callback(
    Output('graph', 'figure'),
    Output('graph_zoom', 'figure'),
    Input('function-name', 'value'),
    Input('dimensionality', 'value'),
)
def callback(*args):
    layout.callback(*args)

def run():
    app.run_server(debug=True)

if __name__ == '__main__':
    run()
