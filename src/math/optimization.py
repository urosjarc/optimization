import inspect
from random import random

import go_benchmark_functions
from go_benchmark_functions.go_benchmark import Benchmark
import numpy as np


def functions():
    funs = {}
    for funName, fun in go_benchmark_functions.__dict__.items():
        if inspect.isclass(fun):
            if issubclass(fun, Benchmark) and funName not in ['Benchmark']:
                funs[funName] = fun
    return funs

def function_dim(fun: Benchmark) -> int:
    signature = inspect.signature(fun.__init__)
    parameters = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    return parameters.get('dimensions')

class Function:
    def __init__(self, f: Benchmark, randomize=True):
        self.benchmark: Benchmark = f()
        self.dimensions = function_dim(f)
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
