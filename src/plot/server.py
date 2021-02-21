import sys
import json

import dash
from dash.dependencies import Input, Output
from dash.exceptions import DashException
from plotly.graph_objs import Figure

from src.math.optimization import Function
from src.optimization.random import RandomOptimizer
from src.plot import content
from src.plot.graph import Surface

this = sys.modules[__name__]
this.app = dash.Dash(__name__)
this.app.layout = content.layout


@app.callback(
    Output('graph', 'figure'),
    Output('graph_zoom', 'figure'),
    Output('interval', 'interval'),
    Input('log', 'value'),
    Input('function-name', 'value'),
    Input('dimensionality', 'value'),
    Input('start', 'n_clicks'),
    Input('stop', 'n_clicks'),
    Input('intervalTime', 'value'),
    Input('interval', 'n_intervals')
)
def callback(log, functionName, dimensionality, start, stop, intervalTime, nIntervals):
    S: Surface = content.surface

    if S.name != functionName:
        f = content.functionsDict.get(functionName, False)
        if f:
            content.function = Function(f, randomize=False)
            S.init(content.function)
        else:
            raise DashException("Function not found!")

    if start > content.startCount:
        content.startCount = start
        content.start = True
        content.optimizer = RandomOptimizer(content.function, maxEval=2000)
    if stop > content.stopCount:
        content.stopCount = stop
        content.start = False
        content.points = [[],[],[]]

    if content.start:
        px, py, pz = content.optimizer.nextPoint()
        content.points[0].append(px)
        content.points[1].append(py)
        content.points[2].append(pz)

    z = S.z
    zZoom = S.zZoom
    if log == 'Log':
        z = S.zLog
        zZoom = S.zZoomLog

    if dimensionality == '2D':
        graph = Figure()
        graph.add_scatter(x=content.points[0], y=content.points[1], mode='markers')
        graph.add_scatter(x=S.xMin, y=S.yMin, mode='markers', fillcolor='red')
        graph.add_contour(x=S.x, y=S.y, z=z, showscale=False)
        graph_zoom = Figure(layout_xaxis_range=content.surface.zoomBounds[0], layout_yaxis_range=content.surface.zoomBounds[1])
        graph_zoom.add_scatter(x=content.points[0], y=content.points[1], mode='markers')
        graph_zoom.add_scatter(x=S.xMin, y=S.yMin, mode='markers', fillcolor='red')
        graph_zoom.add_contour(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False)
    else:
        graph = Figure()
        graph.add_scatter3d(x=content.points[0], y=content.points[1], z=content.points[2], mode='markers')
        graph.add_scatter3d(x=S.xMin, y=S.yMin, z=S.zMin, mode='markers',surfacecolor='red')
        graph.add_surface(x=S.x, y=S.y, z=z, showscale=False)
        graph_zoom = Figure()
        # graph_zoom.add_scatter3d(x=content.points[0], y=content.points[1], z=content.points[2], mode='markers')
        graph_zoom.add_scatter3d(x=S.xMin, y=S.yMin, z=S.zMin, mode='markers', surfacecolor='red')
        graph_zoom.add_surface(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False)

    return graph, graph_zoom, intervalTime


if __name__ == '__main__':
    this.app.run_server(debug=True)
