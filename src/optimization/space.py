import csv
import inspect
from random import random
from statistics import mean
from typing import List

from libs import go_benchmark_functions
from libs.go_benchmark_functions.go_benchmark import Benchmark
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

    def __init__(self, f: Benchmark, hardness=-1):
        self.benchmark: Benchmark = f()
        self.hardness = hardness
        self.dimensions = self.__function_dim(f)
        self.name = str(f).split('.')[-1][:-2]
        self.minValue = np.nan_to_num(self.benchmark.fglob)
        self.minVectors = [list(ele) for ele in self.benchmark.global_optimum]
        self.bounds = []
        self.evaluation = 0
        self.init()

    def init(self):
        if self.name == 'ZeroSum':
            self.minVectors = [[0, 0]]

        for i, b in enumerate(self.benchmark.bounds):
            self.bounds.append(list(b))

        center = []
        for bound in self.bounds:
            center.append(mean(bound))

        minOnCenter = False
        for minVec in self.minVectors:
            if minVec == center:
                minOnCenter = True
                break

        if minOnCenter:
            for i in range(len(self.bounds)):
                diff = self.bounds[i][1] - self.bounds[i][0]
                self.bounds[i][0] += diff / 20 * (1 + random())

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
                fun = Function(f=benchmark, hardness=info.get('hardness', -1))

                if fun.dimensions == dim:
                    funs.append(fun);

    return sorted(funs, key=lambda f: f.hardness, reverse=True)
