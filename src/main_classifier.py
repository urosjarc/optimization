from src.app import Plot
from src.optimization import GridOptimizer
from src.math import *
import matplotlib.pyplot as plt

funs = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2 and i==46:
        from gobench import go_benchmark_functions
        space = Space(go_benchmark_functions.Salomon, rand=True)
        plot = Plot(space)
        plot.cmd.penDown = False
        iter = 2000
        opt = GridOptimizer(space, plot.cmd, iter)
        for i in range(iter):
            plot.d2LogAx.set_title(i)
            plot.addPoint(*opt.nextPoint())
            if i%10 == 0:
                plt.pause(0.001)
        plt.close()
