import sys
import numpy as np

import dash
from dash.dependencies import Input, Output
from dash.exceptions import DashException
from plotly import graph_objs as go

from src.math.optimization import Function

from src.optimization.triangle import TriangleOptimizer
from src.plot import content
from src.plot.graph import Surface

this = sys.modules[__name__]
this.app = dash.Dash(__name__)
this.app.layout = content.layout


@app.callback(
    Output('graph2D', 'figure'),
    Output('graph2D_zoom', 'figure'),
    Output('graph3D', 'figure'),
    Output('graph3D_zoom', 'figure'),
    Output('interval', 'interval'),
    Output('intervalTime', 'value'),
    Output('info', 'children'),

    Input('function-name', 'value'),
    Input('log', 'value'),
    Input('start', 'n_clicks'),
    Input('intervalTime', 'value'),
    Input('interval', 'n_intervals'),
    Input('evaluations', 'value'),
)
def callback(functionName, log, start, intervalTime, n_intervals, evaluations):
    print(functionName, log, start, intervalTime, n_intervals, evaluations)
    S: Surface = content.surface

    if S.name != functionName:
        f = content.functionsDict.get(functionName, False)
        if f:
            content.function = Function(f, randomize=False)
            S.init(content.function)
            content.points = [[], [], []]
        else:
            raise DashException("Function not found!")

    if start > content.startCount:
        content.startCount = start
        content.running = True
        intervalTime = 1000
        content.optimizer = TriangleOptimizer(content.function, maxEval=2000)
        content.points = [[], [], []]

    if content.running and intervalTime == 1000:
        for i in range(int(evaluations)):
            px, py, pz = content.optimizer.nextPoint()
            content.points[0].append(px)
            content.points[1].append(py)
            content.points[2].append(pz)

    points = content.points
    z = S.z
    zZoom = S.zZoom
    if log == 'Log':
        z = S.zLog
        zZoom = S.zZoomLog
        points = S.log(points)

    figure2D = go.Figure(layout=go.Layout(uirevision=functionName, showlegend=False), layout_xaxis_range=S.bounds[0],
                         layout_yaxis_range=S.bounds[1])
    figure2D.add_scatter(x=points[0], y=points[1], mode='markers', uirevision=functionName),
    figure2D.add_scatter(x=S.xMin, y=S.yMin, mode='markers', fillcolor='red', uirevision=functionName),
    figure2D.add_contour(x=S.x, y=S.y, z=z, showscale=False, uirevision=functionName)

    if content.optimizer is not None:
        tx = []
        ty = []
        for t in content.optimizer.triangles:
            tpx = []
            tpy = []
            for p in t.points:
                tpx.append(p.x)
                tpy.append(p.y)
            tpx +=[t.points[0].x, None]
            tpy +=[t.points[0].y, None]
            tx += tpx
            ty += tpy
        figure2D.add_scatter(x=tx, y=ty,fill="toself", uirevision=functionName)

    figure2D_zoom = go.Figure(layout=go.Layout(uirevision=functionName, showlegend=False),
                              layout_xaxis_range=S.zoomBounds[0], layout_yaxis_range=S.zoomBounds[1])
    figure2D_zoom.add_scatter(x=points[0], y=points[1], mode='markers', uirevision=functionName),
    figure2D_zoom.add_scatter(x=S.xMin, y=S.yMin, mode='markers', fillcolor='red', uirevision=functionName),
    figure2D_zoom.add_contour(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False, uirevision=functionName)

    figure3D = go.Figure(layout=go.Layout(uirevision=functionName, showlegend=False), layout_xaxis_range=S.bounds[0],
                         layout_yaxis_range=S.bounds[1])
    figure3D.add_scatter3d(x=points[0], y=points[1], z=points[2], mode='markers', uirevision=functionName),
    figure3D.add_scatter3d(x=S.xMin, y=S.yMin, z=S.zMin, mode='markers', surfacecolor='red', uirevision=functionName),
    figure3D.add_surface(x=S.x, y=S.y, z=z, showscale=False, uirevision=functionName)

    figure3D_zoom = go.Figure(layout=go.Layout(uirevision=functionName, showlegend=False))
    figure3D_zoom.add_scatter3d(x=points[0], y=points[1], z=points[2], mode='markers', uirevision=functionName),
    figure3D_zoom.add_scatter3d(x=S.xMin, y=S.yMin, z=S.zMin, mode='markers', surfacecolor='red',
                                uirevision=functionName),
    figure3D_zoom.add_surface(x=S.xZoom, y=S.yZoom, z=zZoom, showscale=False, uirevision=functionName)
    figure3D_zoom.update_layout(
        scene=dict(
            xaxis=dict(range=S.zoomBounds[0]),
            yaxis=dict(range=S.zoomBounds[1]),
            zaxis=dict(range=[np.min(S.zZoom), np.max(S.zZoom)])),
    )

    info = 'Evaluation: 0'
    if content.optimizer is not None:
        info = f'Evaluation: {content.optimizer.evaluation}'

    return figure2D, figure2D_zoom, figure3D, figure3D_zoom, intervalTime, intervalTime, [info]


if __name__ == '__main__':
    this.app.run_server(debug=True)
