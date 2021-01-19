import random

import matplotlib.pyplot as plt
from matplotlib import cm
from src.math import *


# run()

class Plot:

    def __init__(self, surface: Surface):
        self.fun: Surface = surface
        self.fig = None
        self.scatter = None
        self.init()

    def init(self):
        self.fun.init()
        plt.ion()
        self.fig, ax = plt.subplots(1, 1)
        cp = ax.contourf(self.fun.x, self.fun.y, self.fun.z, levels=100, cmap="seismic")
        self.fig.colorbar(cp)

        m = self.fun.min
        plt.scatter([m[0][0]], [m[0][1]], color='w')

        self.scatter = ax.scatter([0], [0], color='y')
        self.scatter._x = []
        self.scatter._y = []

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_surface(self.fun.xx, self.fun.yy, self.fun.z,cmap=cm.coolwarm, linewidth=0, antialiased=False)

        plt.show()

    def addPoint(self, x, y):
        self.scatter._x.append(x)
        self.scatter._y.append(y)
        self.scatter.set_offsets(np.c_[self.scatter._x, self.scatter._y])
        self.fig.canvas.draw_idle()

for n, f in fun.__dict__.items():
    if n not in ['__module__'] and not str(n).startswith('_'):
        try:
            plot = Plot(f)
        except Exception:
            pass
exit()

# plot = Plot(fun.rastigin)
# for i in range(1000):
#     plot.addPoint(random.random()*100, random.random()*100)
#     plt.pause(0.1)
# plot.init()
