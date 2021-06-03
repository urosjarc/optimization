import random

from typing import List

from src.optimization.space import Function


class TestOptimizer:
    def __init__(self, fun: Function):
        self.fun = fun
    def nextPoint(self) -> List[float]:
        xy = [random.randint(*self.fun.bounds[0]), random.randint(*self.fun.bounds[1])]
        return xy + [self.fun(xy)]
