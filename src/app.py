import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.collections import PatchCollection

from src.math import *
from matplotlib.patches import Polygon


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

        # Drawing contour bars normal
        ax = fig.add_subplot(gs[0, 1])
        self.d2ZoomAx = ax
        ax.contourf(sur.xZoom, sur.yZoom, sur.zzZoom, levels=sur.step, cmap="gray")
        ax.scatter(sur.xMin, sur.yMin, marker='*', color='yellow')
        self.scatter = ax.scatter([], [], marker=',', color='red', s=1)

        # Drawing surface 3D
        ax = fig.add_subplot(gs[0, 0], projection='3d')
        self.d3Ax = ax
        ax.set_axis_off()
        ax.plot_surface(sur.xx, sur.yy, sur.zz, alpha=1, cmap="jet", linewidth=0, antialiased=True)

        # Drawing progress
        ax = fig.add_subplot(gs[1, 0])
        self.errAx = ax

        plt.show()
        self.cmd.init()

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
        self.unactivePoints = None
        self.minimumsZoom = None
        self.errLine = None

        self.poligons = []
        self.patchCollections = []

    def init(self):
        self.unactivePoints = self.plot.d2LogAx.scatter([], [], marker=',', color='black')
        self.minimums = self.plot.d2LogAx.scatter([], [], marker='*', color="blue")
        self.errLine, = self.plot.errAx.plot([], [], 'r-')
        self.minimumsZoom = self.plot.d2ZoomAx.scatter([], [], marker='*', color="blue")

    def drawTriangles(self, triangles, permament):
        patches = []
        for t in triangles:
            polygon = Polygon([p.vector for p in t.points], True)
            patches.append(polygon)
        for p in self.patchCollections:
            p.remove()
        self.patchCollections = []
        p = PatchCollection(patches, alpha=.8)
        self.patchCollections.append(p)
        self.plot.d2LogAx.add_collection(p)
        plt.show()

    def drawPoligon(self, vectors, permament):
        patches = []
        polygon = Polygon([v for v in vectors], True)
        patches.append(polygon)
        for p in self.patchCollections:
            p.remove()
        self.patchCollections = []
        p = PatchCollection(patches, alpha=.8)
        self.patchCollections.append(p)
        self.plot.d2LogAx.add_collection(p)
        plt.show()

    def errs(self, ers):
        self.plot.errAx.set_xlim([0, len(ers)])
        self.plot.errAx.set_ylim([min(ers), max(ers)])
        self.errLine.set_ydata(np.array(ers))
        self.errLine.set_xdata(np.array([i for i in range(len(ers))]))
        plt.show()

    def localMinimums(self, vectors, colour=[]):
        x = [v[0] for v in vectors]
        y = [v[1] for v in vectors]
        self.minimums.set_offsets(np.c_[x, y])
        # self.minimums.set_color(['gray' for v in vectors])
        self.minimumsZoom.set_offsets(np.c_[x, y])
        plt.show()

    def deactivatedPoints(self, vectors):
        x = [v[0] for v in vectors]
        y = [v[1] for v in vectors]
        self.unactivePoints.set_offsets(np.c_[x, y])
        plt.show()

