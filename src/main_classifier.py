import matplotlib.pyplot as plt
import numpy as np
from src.math import *
from gobench import go_benchmark_functions


class Plot:
    def __init__(self, function):
        self.surface: Surface = Surface(function)
        self.scatter = None
        self.scatterLog = None
        self.step = 51
        self.fig = None

        self.show()

    def show(self):
        # Creating matrix xx, yy, zz
        x = np.linspace(self.surface.f.bounds[0][0], self.surface.f.bounds[0][1], self.step)
        y = np.linspace(self.surface.f.bounds[1][0], self.surface.f.bounds[1][1], self.step)
        xx, yy = np.meshgrid(x, y, sparse=True)
        zz = np.array([[self.surface(xi, yi) for xi in x] for yi in y])
        zzLog = np.log2(zz - self.surface.min + 1)

        # Creating points setup
        opt = self.surface.opt
        zMin = np.array([self.surface.min for _ in opt])
        xMin = [o[0] for o in opt]
        yMin = [o[1] for o in opt]
        zMinLog = np.log2(zMin - self.surface.min + 1)

        # Drawing main figure
        plt.ion()
        fig = plt.figure()
        self.fig = fig
        fig.suptitle(f'{self.surface.name} - {len(self.surface.opt)} min.')

        # Drawing contour bars normal
        ax = fig.add_subplot(2, 2, 2)
        cp = ax.contourf(x, y, zz, levels=self.step, cmap="jet")
        ax.scatter(xMin, yMin, marker='*', color='red')
        fig.colorbar(cp)

        # Drawing points
        self.scatter = ax.scatter([], [], marker='x', color='red')
        self.scatter._x = []
        self.scatter._y = []

        # Drawing contour bars log
        ax = fig.add_subplot(2, 2, 4)
        cp = ax.contourf(x, y, zzLog, levels=self.step, cmap="jet")
        ax.scatter(xMin, yMin, marker = '*', color='red')
        fig.colorbar(cp)

        # Drawing log points
        self.scatterLog = ax.scatter([], [], marker='x', color='red')

        # Drawing surface 3D
        ax = fig.add_subplot(2, 2, 1, projection='3d')
        ax.plot_surface(xx, yy, zz,cmap="jet", linewidth=0, antialiased=True)
        ax.scatter(xMin, yMin, zMin, color='red')
        ax = fig.add_subplot(2, 2, 3, projection='3d')
        ax.scatter(xMin, yMin, zMinLog, color='red')
        ax.plot_surface(xx, yy, zzLog, cmap="jet", linewidth=0, antialiased=True)
        plt.show()

    def addPoint(self, x, y):
        self.scatter._x.append(x)
        self.scatter._y.append(y)
        self.scatter.set_offsets(np.c_[self.scatter._x, self.scatter._y])
        self.scatterLog.set_offsets(np.c_[self.scatter._x, self.scatter._y])
        self.fig.canvas.draw_idle()

funs:List[Benchmark] = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2:
        plot = Plot(f)
        for i in range(10):
            import random
            plot.addPoint(random.random()*10 - 5,random.random()*10 - 5)
        print(i, plot.surface.name)
        plt.savefig(f'../data/functions/{i:03d}_{plot.surface.name}.png')
        # plt.close()

        plt.waitforbuttonpress()