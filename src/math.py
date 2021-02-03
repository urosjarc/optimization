import numpy as np
from random import random
from typing import List, Tuple, Callable
import inspect
from gobench import go_benchmark_functions
from gobench.go_benchmark_functions import Benchmark

def functions() -> List[Tuple[Callable, int]]:
    funs = []
    for name, fun in go_benchmark_functions.__dict__.items():
        if inspect.isclass(fun):
            if issubclass(fun, Benchmark) and name not in ['Benchmark']:
                funs.append(fun)
    return funs

def dimensions(fun: Benchmark) -> int:
    signature = inspect.signature(fun.__init__)
    parameters = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    return parameters.get('dimensions')


class Space:
    def __init__(self, f: Benchmark, rand=True):
        self.f: Benchmark = f()
        self._dim = dimensions(f)
        self.min = np.nan_to_num(self.f.fglob)
        self.name = str(f).split('.')[-1][:-2]
        self.opt = self.f.global_optimum
        self.rand = rand

        if self.name == 'ZeroSum':
            self.opt = [[0,0]]

    def __call__(self, vector):
        if self.rand:
            vector[0] += max(self.f.bounds[0])/20 * random()
            vector[1] += max(self.f.bounds[0])/20 * random()
        return np.nan_to_num(self.f.fun(vector))

