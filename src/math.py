import numpy as np
from typing import Callable


class Surface:

    def __init__(self, f: Callable, min, range, step=400):
        self.min = min
        self.range = range
        self.f = f
        self.step = step
        self.x = []
        self.y = []
        self.z = []

    def init(self):
        self.x = np.linspace(self.range[0], self.range[1], self.step)
        self.y = np.linspace(self.range[0], self.range[1], self.step)
        xx, yy = np.meshgrid(self.x, self.y, sparse=True)
        self.z = self.f(xx, yy)

    def __call__(self, x, y, norm=True):
        return self.f(x, y)

class fun:
    _rastrigin = lambda x, y: ((x ** 2 - 10 * np.cos(2 * np.pi * x)) + (y ** 2 - 10 * np.cos(2 * np.pi * y)) + 20)
    _eggholder = lambda x, y: (
            -(y + 47) * np.sin(np.sqrt(abs(x / 2 + (y + 47)))) - x * np.sin(np.sqrt(abs(x - (y + 47)))))

    rastigin = Surface(_rastrigin, min=(0, 0, 0), range=(-5.12, 5.12))
    eggholder = Surface(_eggholder, min=(512, 404.2319, -959.6407), range=(-512, 512))
