from src.app import Plot
from src.domain import GridOptimizer
from src.math import *
import matplotlib.pyplot as plt

funs = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2 and i==46:
        from gobench import go_benchmark_functions
        plot = Plot(go_benchmark_functions.Damavandi)
        opt = GridOptimizer(plot.space)
        for i in range(300):
            plot.addPoint(*opt.nextPoint())
            plt.waitforbuttonpress()
        plt.pause(1000)
        plt.close()

