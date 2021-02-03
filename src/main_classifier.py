from src.app import Plot
from src.optimization import GridOptimizer
from src.math import *
import matplotlib.pyplot as plt

funs = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2 and i==46:
        from gobench import go_benchmark_functions
        plot = Plot(go_benchmark_functions.XinSheYang03)
        plot.cmd.penDown = True
        opt = GridOptimizer(plot.space, plot.cmd, 300)
        for i in range(300):
            plot.d2LogAx.set_title(i)
            plot.addPoint(*opt.nextPoint())
            plt.waitforbuttonpress()
        plt.pause(1000)
        plt.close()
