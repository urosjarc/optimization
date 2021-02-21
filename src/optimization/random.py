from random import random, randint

import numpy as np

from src.math.optimization import Function


class RandomOptimizer:
    def __init__(self, space: Function, maxEval):
        self.space = space
        self.maxEvaluations = maxEval
        self.evaluation = 0
        self.min = 10 ** 10
        self.best = [randint(b[0], b[1]) for b in self.space.benchmark.bounds]
        self.radius = self.space.benchmark.bounds[0][1]

    def nextPoint(self):
        self.radius *= 0.99999

        while True:
            vector = np.array([best + self.radius * (random() - 0.5) * 2 for best in self.best])

            inBounds = True
            for i in range(len(vector)):
                if not (self.space.benchmark.bounds[i][0] < vector[i] < self.space.benchmark.bounds[i][1]):
                    inBounds = False
                    break

            if inBounds:
                break

        value = self.space(vector)
        if value < self.min:
            self.min = value
            self.best = vector
        return vector.tolist() + [value]
