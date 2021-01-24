import numpy as np
from typing import Callable


class Surface:

    def __init__(self, f: Callable, min, range=None, xrange=None, yrange=None, step=400):
        self.min = [min] if isinstance(min, tuple) else min
        self.xrange = xrange if range is None else range
        self.yrange = yrange if range is None else range
        self.f = f
        self.step = step
        self.x = []
        self.y = []
        self.z = []

    def init(self):
        self.x = np.linspace(self.xrange[0], self.xrange[1], self.step)
        self.y = np.linspace(self.yrange[0], self.yrange[1], self.step)
        self.xx, self.yy = np.meshgrid(self.x, self.y, sparse=True)
        self.z = self.f(self.xx, self.yy)

    def __call__(self, x, y, norm=True):
        return self.f(x, y)


class fun:
    # https://en.wikipedia.org/wiki/Test_functions_for_optimization
    _rastrigin = lambda x, y: 10 * 2 + (x ** 2 - 10 * np.cos(2 * np.pi * x)) + (y ** 2 - 10 * np.cos(2 * np.pi * y))
    _ackley = lambda x, y: -20 * np.exp(-0.2 * np.sqrt(0.5 * (x ** 2 + y ** 2))) - np.exp(
        0.5 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y))) + np.exp(1) + 20
    _sphere = lambda x, y: x ** 2 + y ** 2
    _rosenbrock = lambda x, y: 100 * (y - x ** 2) ** 2 + (1 - x) ** 2
    _beale = lambda x, y: (1.5 - x + x * y) ** 2 + (2.25 - x + x * y ** 2) ** 2 + (2.625 - x + x * y ** 3) ** 2
    _goldsteinPrice = lambda x, y: (1 + (x + y + 1) ** 2 * (19 - 14 * x + 3 * x ** 2 - 14 * y + 6 * x * y + 3 * y ** 2)) * (
            30 + (2 * x - 3 * y) ** 2 * (18 - 32 * x + 12 * x ** 2 + 48 * y - 36 * x * y + 27 * y ** 2))
    _booth = lambda x, y: (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2
    _bukin6 = lambda x, y: 100 * np.sqrt(np.abs(y - 0.01 * x ** 2)) + 0.01 * np.abs(x + 10)
    _matyas = lambda x, y: 0.26 * (x ** 2 + y ** 2) - 0.48 * x * y
    _levi13 = lambda x, y: np.sin(3 * np.pi * x) ** 2 + (x - 1) ** 2(1 + np.sin(3 * np.pi * y) ** 2) + (y - 1) ** 2 * (
                1 + np.sin(2 * np.pi * y) ** 2)
    _himmelblaus = lambda x, y: (x ** 2 + y - 11) ** 2 + (x + y ** 2 - y) ** 2
    _threeHumpCamel = lambda x, y: 2 * x ** 2 - 1.05 * x ** 4 + (x / 6.0) ** 6 + x * y + y ** 2
    _easom = lambda x, y: -np.cos(x) * np.cos(y) * np.exp(-((x - np.pi) ** 2 + (y - np.pi) ** 2))
    _crossInTray = lambda x, y: -0.0001(
        np.abs(np.sin(x) * np.sin(y) * np.exp(np.abs(100 - np.sqrt(x ** 2 + y ** 2) / np.pi))) + 1) ** 0.1
    _eggholder = lambda x, y: -(y + 47) * np.sin(np.sqrt(np.abs(x / 2 + (y + 47)))) - x * np.sin(
        np.sqrt(np.abs(x - (y + 47))))
    _holderTable = lambda x, y: -np.abs(np.sin(x) * np.cos(y) * np.exp(np.abs(1 - np.sqrt(x ** 2 + y ** 2) / np.pi)))
    _mcCormick = lambda x, y: np.sin(x+y)+(x-y)**2-1.5*x+2.5*y+1
    _schaffer2 = lambda x, y: .5 + (np.sin(x**2-y**2)**2 -.5)/(1+0.001(x**2+y**2))**2
    _schaffer4 = lambda x, y: .5 + (np.cos(np.sin(np.abs(x**2-y**2)))**2 -.5)/(1+0.001(x**2+y**2))**2
    _styblinskiTang = lambda x, y: (x**4-16*x**2 + 5*x)/2 + (y**4-16*y**2 + 5*y)/2

    rastigin = Surface(_rastrigin, min=(0, 0, 0), range=(-5.12, 5.12))
    ackley = Surface(_ackley, min=(0, 0, 0), range=(-5, 5))
    sphere = Surface(_sphere, min=(0, 0, 0), range=(-np.inf, np.inf))
    rosenbrock = Surface(_rosenbrock, min=(1, 1, 0), range=(-np.inf, np.inf))
    beale = Surface(_beale, min=(3, .5, 0), range=(-4.5, 4.5))
    goldsteinPrice = Surface(_goldsteinPrice, min=(0, -1, 3), range=(-2, 2))
    booth = Surface(_booth, min=(1, 3, 0), range=(-10, 10))
    bukin6 = Surface(_bukin6, min=(-10, 1, 0), xrange=(-15, -5), yrange=(-3, 3))
    matyas = Surface(_matyas, min=(0, 0, 0), range=(-10, 10))
    levi = Surface(_levi13, min=(1, 1, 0), range=(-10, 10))
    himmelblaus = Surface(_himmelblaus, min=[(3, 2, 0), (-2.805118, 3.131312, 0), (-3.779310, -3.283186, 0),
                                             (3.584428, -1.848126, 0)], range=(-5, 5))
    treehumpcamel = Surface(_threeHumpCamel, min=(0, 0, 0), range=(-5, 5))
    easom = Surface(_easom, min=(np.pi, np.pi, -1), range=(-100, 100))
    crossintray = Surface(_crossInTray, min=[(1.34941, -1.34941, -2.06261), (1.34941, 1.34941, -2.06261),
                                             (-1.34941, 1.34941, -2.06261), (-1.34941, -1.34941, -2.06261)],
                          range=(-10, 10))
    eggholder = Surface(_eggholder, min=(512, 404.2319, -959.6407), range=(-512, 512))
    holdertable = Surface(_holderTable, min=[(8.04402, 9.66459, -19.2085), (-8.04402, 9.66459, -19.2085),
                                             (8.04402, -9.66459, -19.2085), (-8.04402, -9.66459, -19.2085)],
                          range=(-10, 10))
    mccormick = Surface(_mcCormick, min=(-0.54719,-1.54719, -1.9133), xrange=(-1.5, 4), yrange=(-3, 4))
    schaffer2 = Surface(_schaffer2, min=(0,0,0), range=(-100, 100))
    schaffer4 = Surface(_schaffer4, min=[(0,1.25313,0.292579), (0,-1.25313,0.292579)], range=(-100, 100))
    styblinskiTang = Surface(_styblinskiTang, min=(-2.903534,-2.903534,-39.16616*2), range=(-5, 5))
