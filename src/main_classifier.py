import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Path3DCollection

from src.math import *




class Plot:
    def __init__(self, function):
        self.surface: Surface = Surface(function)
        self.scatter = None
        self.scatterLog = None
        self.scatter3D = None
        self.step = 51
        self.fig = None
        self.points = [[],[],[]]
        self.show()

    def show(self):
        zLog = lambda z: np.log2(z - self.surface.min + 1)
        opt = self.surface.opt

        # Creating matrix xx, yy, zz
        x = np.linspace(self.surface.f.bounds[0][0], self.surface.f.bounds[0][1], self.step)
        y = np.linspace(self.surface.f.bounds[1][0], self.surface.f.bounds[1][1], self.step)
        xx, yy = np.meshgrid(x, y, sparse=True)
        zz = np.array([[self.surface(xi, yi) for xi in x] for yi in y])
        zzLog = zLog(zz)

        # Creating points setup
        zMin = np.array([self.surface.min for _ in opt])
        xMin = [o[0] for o in opt]
        yMin = [o[1] for o in opt]
        zMinLog = zLog(zMin)

        # Drawing main figure
        plt.ion()
        gs = gridspec.GridSpec(2, 2)
        fig = plt.figure()
        self.fig = fig
        fig.suptitle(f'{self.surface.name} - {len(self.surface.opt)} min.')

        # Drawing contour bars normal
        ax = fig.add_subplot(gs[0,1])
        cp = ax.contourf(x, y, zz, levels=self.step, cmap="jet")
        ax.scatter(xMin, yMin, marker='*', color='red')
        fig.colorbar(cp)

        # Drawing points
        self.scatter = ax.scatter([], [], marker='x', color='red')

        # Drawing contour bars log
        ax = fig.add_subplot(gs[1,1])
        cp = ax.contourf(x, y, zzLog, levels=self.step, cmap="jet")
        ax.scatter(xMin, yMin, marker = '*', color='red')
        fig.colorbar(cp)

        # Drawing log points
        self.scatterLog = ax.scatter([], [], marker='x', color='red')

        # Drawing surface 3D
        ax = fig.add_subplot(gs[:,0], projection='3d')
        ax.plot_surface(xx, yy, zz, alpha=0.5, cmap="jet", linewidth=0, antialiased=True)
        self.scatter3D = ax.scatter([],[],[], 'o', color='black')
        plt.show()

    def addPoint(self, x, y):
        self.points[0].append(x)
        self.points[1].append(y)
        self.points[2].append(self.surface(x, y))
        self.scatter.set_offsets(np.c_[self.points[0], self.points[1]])
        self.scatterLog.set_offsets(np.c_[self.points[0], self.points[1]])
        self.scatter3D._offsets3d = self.points
        self.fig.canvas.draw_idle()

funs:List[Benchmark] = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2:
        plot = Plot(f)
        plt.savefig(f'../data/functions/{i:03d}_{plot.surface.name}.png')
        plt.waitforbuttonpress()
        plt.close()

