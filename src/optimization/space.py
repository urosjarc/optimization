import csv
import inspect
from random import random
from typing import List

import go_benchmark_functions
from go_benchmark_functions.go_benchmark import Benchmark
import numpy as np

from src import utils


class Function:

    @staticmethod
    def __function_dim(fun: Benchmark) -> int:
        signature = inspect.signature(fun.__init__)
        parameters = {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
        return parameters.get('dimensions')

    def __init__(self, f: Benchmark, hardness=-1, randomize=True):
        self.benchmark: Benchmark = f()
        self.hardness = hardness
        self.dimensions = self.__function_dim(f)
        self.randomize = randomize
        self.name = str(f).split('.')[-1][:-2]
        self.minValue = np.nan_to_num(self.benchmark.fglob)
        self.minVector = self.benchmark.global_optimum
        self.bounds = []
        self.evaluation = 0
        self.init()

    def init(self):
        for i, b in enumerate(self.benchmark.bounds):
            b = list(b)
            if self.randomize:
                diff = abs(b[0] - b[1])
                b[0] += diff / 50 * (1 + random())
                b[1] -= diff / 10 * (1 + random())
            self.bounds.append(b)

        if self.name == 'ZeroSum':
            self.minVector = [[0, 0]]

    def __call__(self, vector):
        self.evaluation += 1
        return np.nan_to_num(self.benchmark.fun(np.array(vector)))


class Mesh:
    def __init__(self, step, zoom):
        self.function = None
        self.name = None
        self.step = step
        self.zoom = zoom

        self.x = None
        self.y = None
        self.z = None
        self.zLog = None

        self.xZoom = None
        self.yZoom = None
        self.zZoom = None
        self.zZoomLog = None

        self.xMin = None
        self.yMin = None
        self.zMin = None
        self.zMinLog = None

        self.bounds = None
        self.zoomBounds = None

    def logZ(self, array):
        return np.log2(array - self.function.minValue + 1)

    def init(self, function: Function):
        self.function = function
        self.bounds = function.bounds
        self.name = function.name

        axes = [np.linspace(bound[0], bound[1], self.step).tolist() for bound in function.bounds]
        self.x, self.y = axes[0], axes[1]
        self.z = [[function(np.array([xi, yi])) for xi in self.x] for yi in self.y]
        self.zLog = self.logZ(self.z)

        XminDiff = abs(-function.bounds[0][0] + function.bounds[0][1]) / self.zoom
        YminDiff = abs(-function.bounds[1][0] + function.bounds[1][1]) / self.zoom
        self.zoomBounds = [
            [function.minVector[0][0] - XminDiff, function.minVector[0][0] + XminDiff],
            [function.minVector[0][1] - YminDiff, function.minVector[0][1] + YminDiff]
        ]
        Xaxe = np.linspace(*self.zoomBounds[0], self.step).tolist()
        Yaxe = np.linspace(*self.zoomBounds[1], self.step).tolist()
        self.xZoom, self.yZoom = Xaxe, Yaxe
        self.zZoom = [[function(np.array([xi, yi])) for xi in self.xZoom] for yi in self.yZoom]
        self.zZoomLog = self.logZ(self.zZoom)

        self.xMin = [o[0] for o in function.minVector]
        self.yMin = [o[1] for o in function.minVector]
        self.zMin = [function.minValue for _ in function.minVector]
        self.zMinLog = self.logZ(self.zMin)


def functions(dim) -> List[Function]:
    gbfh = {}
    with open(utils.getPath(__file__, '../../data/go_benchmark_functions_hardness.csv')) as f:
        csvf = csv.DictReader(f)
        for row in csvf:
            gbfh[row['name']] = {'hardness': 100 - float(row['hardness']), 'dim': int(row['dim'])}

    funs = []
    for funName, benchmark in go_benchmark_functions.__dict__.items():
        if inspect.isclass(benchmark):
            if issubclass(benchmark, Benchmark) and funName not in ['Benchmark']:
                info = gbfh.get(funName, {})
                fun = Function(
                    f=benchmark,
                    hardness=info.get('hardness', -1)
                )

                if fun.dimensions == dim:
                    funs.append(fun);

    return sorted(funs, key=lambda f: f.hardness, reverse=True)