import numpy as np
from typing import Callable


class fun:
    rastrigin = lambda x, y: ((x ** 2 - 10 * np.cos(2 * np.pi * x)) + (y ** 2 - 10 * np.cos(2 * np.pi * y)) + 20)
    eggholder = lambda x, y: (
            -(y + 47) * np.sin(np.sqrt(abs(x / 2 + (y + 47)))) - x * np.sin(np.sqrt(abs(x - (y + 47)))))


def normalize(matrix, minV, maxV):
    ave = (minV + maxV) / 2
    dy = maxV - ave
    matrix -= ave
    matrix /= dy
    return matrix


class Surface:
    def __init__(self, f: Callable, range=(-10, 10), step=400):
        self.range = range
        self.f = f
        self.x = np.linspace(range[0], range[1], step)
        self.y = np.linspace(range[0], range[1], step)
        xx, yy = np.meshgrid(self.x, self.y, sparse=True)
        self.z = self.f(xx, yy)

    def __call__(self, x, y, norm=True):
        return self.f(x, y)
