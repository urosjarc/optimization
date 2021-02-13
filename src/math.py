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

def normalizeVector(vector):
    return vector / np.linalg.norm(vector)

def angle(v1, v2):
    v1_u = normalizeVector(v1)
    v2_u = normalizeVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

class Space:
    def __init__(self, f: Benchmark, rand=True):
        self.f: Benchmark = f()
        self._dim = dimensions(f)
        self.rand=rand
        self.minValue = np.nan_to_num(self.f.fglob)
        self.name = str(f).split('.')[-1][:-2]
        self.minVector = self.f.global_optimum
        self.bounds = []
        self.eval = 0
        self.init()

    def init(self):
        for i, b in enumerate(self.f.bounds):
            b = list(b)
            if self.rand:
                diff = abs(b[0] - b[1])
                b[0] += diff/30 * (1+random())
                b[1] -= diff/30 * (1+random())
            self.bounds.append(b)


        if self.name == 'ZeroSum':
            self.minVector = [[0, 0]]

    def __call__(self, vector):
        self.eval += 1
        return np.nan_to_num(self.f.fun(np.array(vector)))

