import sys

from dash import dash
from dash.dependencies import Input, Output
from dash.exceptions import DashException
from plotly.graph_objs import Figure

from src.math.optimization import Function
from src.optimization.triangle import TriangleOptimizer, Point
from src.plot import content

this = sys.modules[__name__]
this.app = dash.Dash(__name__)
this.app.layout = content.layout


@app.callback(
    Output('graph', 'figure'),
    Output('graph_zoom', 'figure'),
    Input('log', 'value'),
    Input('function-name', 'value'),
    Input('dimensionality', 'value'),
    Input('start', 'n_clicks')
)
def callback(log, functionName, dimensionality, start):
    S = content.surface

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
        content.optimizer = TriangleOptimizer(content.function, maxEval=2000)
    if start > content.startCount:
        content.startCount = start
        content.start = False
        print("STOP")

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
        countour2D = Figure()
        countour2D.add_scatter(x=content.points[0], y=content.points[1])
        countour2D.add_contour(x=S.x, y=S.y, z=z, showscale=False)
        countour2D_zoom = Figure()
        countour2D_zoom.add_scatter(x=content.points[0], y=content.points[1])
        countour2D_zoom.add_contour(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False)
        return countour2D, countour2D_zoom
    else:
        surface3D = Figure()
        surface3D.add_scatter3d(x=content.points[0], y=content.points[1], z=content.points[2])
        surface3D.add_surface(x=S.x, y=S.y, z=z, showscale=False)
        surface3D_zoom = Figure()
        surface3D_zoom.add_scatter3d(x=content.points[0], y=content.points[1], z=content.points[2])
        surface3D_zoom.add_surface(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False)
        return surface3D, surface3D_zoom


if __name__ == '__main__':
    this.app.run_server(debug=True)
