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

    def __init__(self, f: Benchmark, hardness=-1, randomize=False):
        self.benchmark: Benchmark = f()
        self.hardness = hardness
        self.dimensions = self.__function_dim(f)
        self.randomize = randomize
        self.name = str(f).split('.')[-1][:-2]
        self.minValue = np.nan_to_num(self.benchmark.fglob)
        self.minVectors = [list(ele) for ele in self.benchmark.global_optimum]
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
            self.minVectors = [[0, 0]]

    def __call__(self, vector):
        self.evaluation += 1
        return np.nan_to_num(self.benchmark.fun(np.array(vector)))


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
