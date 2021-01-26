import numpy as np
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


class Surface:

    def __init__(self, f: Benchmark):
        self.f: Benchmark = f()
        self._dim = dimensions(f)
        self.name = str(f).split('.')[-1][:-2]
        self.step = 101
        self.x = []
        self.y = []
        self.z = []
        self.xx = []
        self.yy = []

    def init(self):
        self.x = np.linspace(self.f.bounds[0][0], self.f.bounds[0][1], self.step)
        self.y = np.linspace(self.f.bounds[1][0], self.f.bounds[1][1], self.step)
        self.xx, self.yy = np.meshgrid(self.x, self.y, sparse=True)
        z = []
        for yi in self.y:
            z.append([])
            for xi in self.x:
                z[-1].append(self(xi, yi))
        self.z = np.array(z)

    def __call__(self, x, y):
        vector = [x, y] + [0 for _ in range(self._dim-2)]
        return self.f.fun(np.array(vector))
