from src.app import Plot
from src.domain import Optimizer
from src.math import *
import matplotlib.pyplot as plt

funs = functions()
for i, f in enumerate(funs):
    if dimensions(f) == 2:
        plot = Plot(f)
        opt = Optimizer(plot.space)
        for i in range(500):
            plot.addPoint(*opt.nextPoint())
            plt.pause(0.1)
        plt.waitforbuttonpress()
        plt.close()

