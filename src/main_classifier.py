import matplotlib.pyplot as plt
import numpy as np
from src.math import *
from gobench import go_benchmark_functions


class Plot:
    def __init__(self, function):
        self.surface: Surface = Surface(function)
        self.fig = None
        self.fig3D = None
        self.scatter = None
        self.step = 100

    def init(self):
        self.surface.init()

    def show(self):
        plt.ion()
        z = self.surface.z
        zLog = np.log2(z - np.min(z) + 1)
        zOpt = self.surface.f.fglob
        zOptLog = np.log2(zOpt - np.min(z) + 1)
        xyOpt = self.surface.f.global_optimum

        # Drawing main figure
        self.fig = plt.figure()
        self.fig.suptitle(f'{self.surface.name}[{self.surface._dim}]  {len(self.surface.f.global_optimum)}')

        # Drawing contour bars
        ax = self.fig.add_subplot(2, 2, 2)
        cp = ax.contourf(self.surface.x, self.surface.y, z, levels=100, cmap="jet")
        ax.scatter([m[0] for m in xyOpt], [m[1] for m in xyOpt], color='black')
        self.fig.colorbar(cp)
        ax = self.fig.add_subplot(2, 2, 4)
        cp = ax.contourf(self.surface.x, self.surface.y, zLog, levels=100, cmap="jet")
        ax.scatter([m[0] for m in xyOpt], [m[1] for m in xyOpt], color='black')
        self.fig.colorbar(cp)

        # Draw global optimums

        # Drawing points
        self.scatter = ax.scatter([], [], color='y')
        self.scatter._x = []
        self.scatter._y = []

        # Drawing surface 3D
        ax = self.fig.add_subplot(2, 2, 1, projection='3d')
        ax.plot_surface(self.surface.xx, self.surface.yy, z,cmap="jet", linewidth=0, antialiased=True, rcount=100, ccount=100)
        ax.scatter([m[0] for m in xyOpt], [m[1] for m in xyOpt], [zOpt for _ in xyOpt], color='black')
        ax = self.fig.add_subplot(2, 2, 3, projection='3d')
        ax.scatter([m[0] for m in xyOpt], [m[1] for m in xyOpt], zOptLog, color='black')
        ax.plot_surface(self.surface.xx, self.surface.yy, zLog, cmap="jet", linewidth=0, antialiased=True)
        plt.show()

    def addPoint(self, x, y):
        self.scatter._x.append(x)
        self.scatter._y.append(y)
        self.scatter.set_offsets(np.c_[self.scatter._x, self.scatter._y])
        self.fig.canvas.draw_idle()

def evaluate():
    import csv
    with open('test_functions.csv', 'a', newline='') as f:
        w = csv.DictWriter(f, ['rate', 'function'])
        funs = functions()
        # w.writeheader()
        for i, f in enumerate(funs):
            if i <146:
                continue
            plot = Plot(f)
            plot.init()
            plot.show()
            plt.waitforbuttonpress()
            plt.close()
            w.writerow({
                'rate': float(input(f"{plot.surface.name}:")),
                'function': plot.surface.name
            })

plot = Plot(go_benchmark_functions.Damavandi)
plot.init()
plot.show()
plt.waitforbuttonpress()
# plt.close()
input("")
