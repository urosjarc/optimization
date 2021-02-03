import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from matplotlib.axes import Axes

from src.math import *


class Surface:
    def __init__(self, space: Space, step):
        self.step = step
        zLog = lambda z: np.log2(z - space.min + 1)
        axes = [np.linspace(bound[0], bound[1], step) for bound in space.f.bounds]
        self.x, self.y = axes[0], axes[1]
        self.xx, self.yy = np.meshgrid(axes[0], axes[1], sparse=True)
        self.zz = np.array([[space(np.array([xi, yi])) for xi in self.x] for yi in self.y])
        self.zzLog = zLog(self.zz)

        self.zMin = np.array([space.min for _ in space.opt])
        self.xMin = [o[0] for o in space.opt]
        self.yMin = [o[1] for o in space.opt]
        self.zMinLog = zLog(self.zMin)
        self.points = [[], [], []]

class Plot:

    def __init__(self, function):
        self.space: Space = Space(function)
        self.surface: Surface = Surface(self.space, 51)
        self.cmd: PlotInterface = PlotInterface(self)
        self.eval = 0
        self.min = None

        self.d2Ax = None
        self.scatter = None
        self.d2LogAx = None
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
        fig = plt.figure()
        self.fig = fig
        fig.suptitle(f'{self.space.name} - {len(self.space.opt)} min.')

        # Drawing contour bars normal
        ax = fig.add_subplot(gs[0,1])
        self.d2Ax = ax
        cp = ax.contourf(sur.x, sur.y, sur.zz, levels=sur.step, cmap="jet")
        ax.scatter(sur.xMin, sur.yMin, marker='*', color='red')
        fig.colorbar(cp)

        # Drawing points
        self.scatter = ax.scatter([], [], marker='x', color='red')

        # Drawing contour bars log
        ax = fig.add_subplot(gs[1,1])
        self.d2LogAx = ax
        cp = ax.contourf(sur.x, sur.y, sur.zzLog, levels=sur.step, cmap="jet")
        ax.scatter(sur.xMin, sur.yMin, marker = '*', color='red')
        fig.colorbar(cp)

        # Drawing log points
        self.scatterLog = ax.scatter([], [], marker='x', color='red')

        # Drawing surface 3D
        ax = fig.add_subplot(gs[:,0], projection='3d')
        self.d3Ax = ax
        ax.plot_surface(sur.xx, sur.yy, sur.zz, alpha=0.5, cmap="jet", linewidth=0, antialiased=True)
        self.scatter3D = ax.scatter([],[],[], 'o', color='black')
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
        self.scatter3D._offsets3d = self.surface.points

        self.fig.canvas.draw_idle()

class PlotInterface:
    def __init__(self, plot: Plot):
        self.plot = plot
        self.penDown = True

    def poligon(self, poligon):
        if self.penDown:
            poligon.append(poligon[0])
            xs, ys = zip(*poligon)
            self.plot.d2LogAx.plot(xs,ys)
            plt.show()
