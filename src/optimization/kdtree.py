import copy
from statistics import mean
from typing import List

import numpy as np
from OpenGL import GL

from src.gui.plot import Model, Shape
from src.gui.plot.model import MODEL
from src.math.linalg import normalizeVector
from src.optimization.space import Function


class Cube:
    model = Model(MODEL.GENERIC, GL.GL_LINES, 3, initBuffers=False)

    def __init__(self, bounds: List[List[float]]):
        self.bounds = bounds
        self.dim = len(bounds)
        self.start = [b[0] for b in bounds]
        self.end = [b[1] for b in bounds]
        self.value = None
        Cube.model.addShape(self.shape3D())

        self.children: List[Cube] = []

    def longestAxis(self):
        maxAxis = 0
        maxDist = 0

        for i in range(self.dim):
            dist = abs(self.end[i] - self.start[i])
            if dist > maxDist:
                maxAxis = i
                maxDist = dist

        return maxAxis

    def divide(self, axis):
        middleAxisPoint = mean(self.bounds[axis])
        lowerAxisBound = [self.bounds[axis][0], middleAxisPoint]
        upperAxisBound = [middleAxisPoint, self.bounds[axis][1]]
        lowerBounds = copy.deepcopy(self.bounds)
        upperBounds = copy.deepcopy(self.bounds)
        lowerBounds[axis] = lowerAxisBound
        upperBounds[axis] = upperAxisBound

        self.children += [
            Cube(lowerBounds),
            Cube(upperBounds)
        ]

    def partition(self):
        cubes = [self]
        splitedCubes = []
        for axis in range(self.dim):
            for cube in cubes:
                cube.divide(axis)
                splitedCubes += cube.children
            cubes = splitedCubes
            splitedCubes = []

        return cubes

    def center(self):
        middle = []
        for bound in self.bounds:
            middle.append(mean(bound))
        return middle

    def volume(self):
        v = 1
        for axis in range(self.dim):
            v *= abs(self.bounds[axis][1] - self.bounds[axis][0])
        print(v)
        return v

    def setValue(self, value):
        self.value = value

    def shape3D(self):
        shape = Shape()
        shape.add_line(self.start + [0], [self.bounds[0][1], self.bounds[1][0], 0], [1, 0, 0, 1])
        shape.add_line(self.start + [0], [self.bounds[0][0], self.bounds[1][1], 0], [1, 0, 0, 1])
        shape.add_line([self.bounds[0][1], self.bounds[1][0], 0], self.end + [0], [1, 0, 0, 1])
        shape.add_line([self.bounds[0][0], self.bounds[1][1], 0], self.end + [0], [1, 0, 0, 1])
        return shape

class KDTreeOptimizer:
    def __init__(self, fun: Function):
        self.fun: Function = fun

        self.rootCube: Cube = None
        self.queue: List[List[float]] = []
        self.endCubes: List[Cube] = []
        self.init()

    def init(self):
        self.rootCube = Cube(self.fun.bounds)
        self.rootCube.setValue(self.fun(self.rootCube.center()))

        self.queue = [self.rootCube.center() + [self.rootCube.value]]
        self.endCubes = [self.rootCube]
        Cube.model.setShapes([self.endCubes[0].shape3D()])

    def nextCube(self):
        info = {'value': [], 'volume': []}
        for cube in self.endCubes:
            info['value'].append(cube.value)
            info['volume'].append(cube.volume())

        lowValue = 1 - normalizeVector(info['value'])
        highVolume = normalizeVector(info['volume'])

        rank = 5*highVolume + lowValue*3

        bestRank = np.argsort(rank)[-1]
        return (self.endCubes[bestRank], bestRank)

    def nextPoint(self):
        if self.queue:
            point = self.queue[0]
            self.queue.pop(0)
            return point

        #Search next cube for partitioning
        cube, i = self.nextCube()
        self.endCubes.pop(i)

        #Partition cube and add partitioned cubes to endcubes
        cubes = cube.partition()
        self.endCubes += cubes

        #Add paritioned cubes to queue
        for cube in cubes:
            center = cube.center()
            cube.setValue(self.fun(center))
            vector = center + [cube.value]
            self.queue.append(vector)

        return self.nextPoint()

    def models(self):
        return [Cube.model]
