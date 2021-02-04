from src.app import Plot
from src.optimization import GridOptimizer
from src.math import *
import matplotlib.pyplot as plt

funs = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2 and i==46:
        from gobench import go_benchmark_functions
        plot = Plot(go_benchmark_functions.Damavandi)
        plot.cmd.penDown = False
        opt = GridOptimizer(plot.space, plot.cmd, 500)
        for i in range(400):
            plot.d2LogAx.set_title(i)
            plot.addPoint(*opt.nextPoint())
            # plt.pause(0.1)
        plt.pause(100)
        plt.close()
