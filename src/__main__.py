from src.app import Plot
from src.optimization.triangle import *
from src.math import *
import matplotlib.pyplot as plt
from gobench import go_benchmark_functions
import random

random.seed(1)
space = Space(go_benchmark_functions.Easom, rand=True
    )
plot = Plot(space, zoom=100)
plot.cmd.penDown = True
iter = 2000
opt = TriangleOptimizer(space, plot.cmd, iter)
for i in range(iter):
    plot.d2LogAx.set_title(i)
    plot.addPoint(*opt.nextPoint())
    plt.waitforbuttonpress()
    if i%10==0:
        plt.pause(0.001)
plt.pause(1000)
plt.close()
