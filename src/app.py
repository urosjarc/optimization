import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from matplotlib.axes import Axes

from src.math import *
from src.optimization.triangle import Triangle


class Surface:
    def __init__(self, space: Space, step, zoom):
        self.step = step
        zLog = lambda z: np.log2(z - space.minValue + 1)
        axes = [np.linspace(bound[0], bound[1], step) for bound in space.bounds]
        self.x, self.y = axes[0], axes[1]
        self.xx, self.yy = np.meshgrid(axes[0], axes[1], sparse=True)
        self.zz = np.array([[space(np.array([xi, yi])) for xi in self.x] for yi in self.y])
        self.zzLog = zLog(self.zz)

        XminDiff = abs(-space.bounds[0][0] + space.bounds[0][1]) / zoom
        YminDiff = abs(-space.bounds[1][0] + space.bounds[1][1]) / zoom
        Xaxe = np.linspace(space.minVector[0][0] - XminDiff, space.minVector[0][0] + XminDiff, step)
        Yaxe = np.linspace(space.minVector[0][1] - YminDiff, space.minVector[0][1] + YminDiff, step)
        self.xZoom, self.yZoom = Xaxe, Yaxe
        self.xxZoom, self.yyZoom = np.meshgrid(Xaxe, Yaxe, sparse=True)
        self.zzZoom = np.array([[space(np.array([xi, yi])) for xi in self.xZoom] for yi in self.yZoom])

        self.zMin = np.array([space.minValue for _ in space.minVector])
        self.xMin = [o[0] for o in space.minVector]
        self.yMin = [o[1] for o in space.minVector]
        self.zMinLog = zLog(self.zMin)
        self.points = [[], [], []]


class Plot:

    def __init__(self, space, zoom):
        self.space: Space = space
        self.surface: Surface = Surface(self.space, 201, zoom)
        self.cmd: PlotInterface = PlotInterface(self)
        self.eval = 0
        self.min = None

        self.errAx = None
        self.d2LogAx = None
        self.d2ZoomAx = None
        self.scatterLog = None
        self.d3Ax = None
        self.scatter3D = None
        self.fig = None
        self.show()

    def updateTitle(self):
        self.d3Ax.set_title(f'{self.eval} - {self.min}')

    def show(self):
        # Get surface
        sur = self.surface

        # Drawing main figure
        plt.ion()
        gs = gridspec.GridSpec(2, 2)
        fig = plt.figure(facecolor='gray')
        plt.rcParams['axes.facecolor'] = 'gray'
        self.fig = fig
        fig.suptitle(f'{self.space.name} - {len(self.space.minVector)} min.')

        # Drawing contour bars log
        ax = fig.add_subplot(gs[1, 1])
        self.d2LogAx = ax
        ax.contourf(sur.x, sur.y, sur.zzLog, levels=sur.step, cmap="gray")
        ax.scatter(sur.xMin, sur.yMin, marker='*', color='yellow')
        self.scatterLog = ax.scatter([], [], marker=',', color='red', s=1)
        self.cmd.minimums, = ax.plot([], [], marker='*', color="blue", linestyle='')

        # Drawing contour bars normal
        ax = fig.add_subplot(gs[0, 1])
        self.d2ZoomAx = ax
        ax.contourf(sur.xZoom, sur.yZoom, sur.zzZoom, levels=sur.step, cmap="gray")
        ax.scatter(sur.xMin, sur.yMin, marker='*', color='yellow')
        self.scatter = ax.scatter([], [], marker=',', color='red', s=1)
        self.cmd.minimumsZoom, = ax.plot([], [], marker='*', color="blue", linestyle='')

        # Drawing surface 3D
        ax = fig.add_subplot(gs[0, 0], projection='3d')
        self.d3Ax = ax
        ax.set_axis_off()
        ax.plot_surface(sur.xx, sur.yy, sur.zz, alpha=1, cmap="jet", linewidth=0, antialiased=True)

        # Drawing progress
        ax = fig.add_subplot(gs[1, 0])
        self.errAx = ax
        self.cmd.errLine, = ax.plot([], [], 'r-')

        plt.show()

    def addPoint(self, x, y):
        self.eval += 1
        z = self.space(np.array([x, y]))
        if self.min is None or z < self.min[2]:
            self.min = [x, y, z]
        self.updateTitle()

        self.surface.points[0].append(x)
        self.surface.points[1].append(y)
        self.surface.points[2].append(z)

        self.scatter.set_offsets(np.c_[self.surface.points[0], self.surface.points[1]])
        self.scatterLog.set_offsets(np.c_[self.surface.points[0], self.surface.points[1]])

        self.fig.canvas.draw_idle()


class PlotInterface:
    def __init__(self, plot: Plot):
        self.plot = plot
        self.penDown = True

        self.triangles = None
        self.minimums = None
        self.minimumsZoom = None
        self.errLine = None

    def poligon(self, poligon, permament):
        if self.triangles is None:
            self.triangles, = self.plot.d2LogAx.plot([], [], linewidth=2, color='green')
        if self.penDown:
            poligon.append(poligon[0])
            xs, ys = zip(*poligon)
            if permament:
                self.plot.d2LogAx.plot(xs, ys, linewidth=.01, color='red')
            else:
                self.triangles.set_ydata(ys)
                self.triangles.set_xdata(xs)
            plt.show()

    def drawTriangles(self, triangles: List[Triangle], permament):
        if permament:
            for t in triangles:
                self.poligon([p.vector for p in t.points], permament=permament)
        else:
            vectors = []
            for t in triangles:
                vectors += [p.vector for p in t.points]
            self.poligon(vectors, permament=permament)

    def errs(self, ers):
        self.plot.errAx.set_xlim([0, len(ers)])
        self.plot.errAx.set_ylim([min(ers), max(ers)])
        self.errLine.set_ydata(np.array(ers))
        self.errLine.set_xdata(np.array([i for i in range(len(ers))]))
        plt.show()

    def localMinimum(self, vectors):
        x = [v[0] for v in vectors]
        y = [v[1] for v in vectors]
        self.minimums.set_ydata(np.array(y))
        self.minimums.set_xdata(np.array(x))
        self.minimumsZoom.set_ydata(np.array(y))
        self.minimumsZoom.set_xdata(np.array(x))
        plt.show()
