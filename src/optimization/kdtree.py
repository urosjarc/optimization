import copy
import math
from statistics import mean
from typing import List

import numpy as np
from OpenGL import GL
from sortedcontainers import SortedDict

from src.gui.plot import Model, Shape
from src.gui.plot.model import MODEL
from src.math.linalg import normalizeVector
from src.optimization.space import Function


class Cube:

    def __init__(self, bounds: List[List[float]]):
        self.bounds = bounds
        self.dim = len(bounds)
        self.start = [b[0] for b in bounds]
        self.end = [b[1] for b in bounds]

        self.value = None
        self.center = []
        self.volume = 1

        self.parent: Cube = None
        self.children: List[Cube] = []
        self.adjacentCubes: List[Cube] = []
        self.intersectingCubes: List[Cube] = []

        self.__init()

    def __init(self):
        if 2 <= self.dim <= 3:
            Models.drawGrid(self)

        # INIT CENTER
        for bound in self.bounds:
            self.center.append(mean(bound))

        # INIT VOLUME
        for axis in range(self.dim):
            self.volume *= abs(self.bounds[axis][1] - self.bounds[axis][0])

    @property
    def vector(self):
        if not self.value:
            raise Exception("Cant get vector because cube is not jet evaluated!")
        return self.center + [self.value]

    def connect(self, cube):
        if cube not in self.adjacentCubes:
            self.adjacentCubes.append(cube)
        else:
            raise Exception("Cube is allready in this cubes neighbours, this should not happend!")

        if self not in cube.adjacentCubes:
            cube.adjacentCubes.append(self)
        else:
            raise Exception("Self is allready in cubes neighbours, this should not happend!")

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
        for child in self.children:
            child.parent = self

    def partition(self):
        partCubes = [self]
        splitedCubes = []

        # DIVIDE CUBE TO CHILDRENS
        for axis in range(self.dim):
            for partCube in partCubes:
                partCube.divide(axis)
                splitedCubes += partCube.children
            partCubes = splitedCubes
            splitedCubes = []

        # CONNECT PARTITIONED CUBES WITH THEM SELFS
        for i in range(len(partCubes) - 1):
            for j in range(i + 1, len(partCubes)):
                partCubes[i].connect(partCubes[j])

        # CONNECT PARTITIONED CUBES WITH PARENT AND PARENTS PREACESSORS
        for partCube in partCubes:
            partCube.intersectingCubes.append(self)
            for preacessor in self.intersectingCubes:
                if partCube.contains(preacessor.center):
                    partCube.intersectingCubes.append(preacessor)

        # CONNECT PARTITIONED CUBES WITH PARENT NEIGHBOURS
        for parentNeighbour in self.adjacentCubes:
            for partCube in partCubes:
                if parentNeighbour.overlapsWith(partCube):
                    parentNeighbour.connect(partCube)

        # DISCONNECT NEIGHBOURS WITH FROM OLD CUBE THAT HAVE BEEN PARTITIONED
        # TODO: Removing parent from neighbours is problematic for searching connected cubes!
        for neighbour in self.adjacentCubes:
            neighbour.adjacentCubes.remove(self)
        self.adjacentCubes = None

        return partCubes

    def distance(self, cube):
        dist = 0
        for i, axis in enumerate(self.center):
            dist += (axis - cube.center[i]) ** 2
        return math.sqrt(dist)

    @property
    def isLocalMin(self):
        for cube in self.nearCubes:
            if self.value >= cube.value:
                return False
        return True

    @property
    def cubesInLocalMin(self):
        walleyCubes = SortedDict()
        queue = [self]

        i = 0
        while len(queue) < 10 and i < len(queue):
            for cube in queue[i].adjacentCubes:
                if cube not in queue:
                    queue.append(cube)
                    dist = self.distance(cube)
                    if dist not in walleyCubes:
                        walleyCubes[dist] = [cube]
                    else:
                        walleyCubes[dist].append(cube)
            i += 1
        return queue

    @property
    def nearCubes(self):
        nearCubes = []
        if self.adjacentCubes:
            nearCubes += self.adjacentCubes
        if self.intersectingCubes:
            nearCubes += self.intersectingCubes
        return nearCubes

    def overlapsWith(self, cube):
        smallCube, bigCube = (self, cube) if cube.volume > self.volume else (cube, self)

        testingPoints = [smallCube.start, smallCube.end]
        for axis, bound in enumerate(smallCube.bounds):
            testingPoint = copy.copy(smallCube.start)
            testingPoint[axis] = bound[1]
            testingPoints.append(testingPoint)

        for point in testingPoints:
            inRange = True
            for axis, bound in enumerate(bigCube.bounds):
                if not (bound[0] <= point[axis] <= bound[1]):
                    inRange = False
                    break
            if inRange:
                return True

        return False

    def contains(self, point: List[float]):
        for axis, bound in enumerate(self.bounds):
            if not (bound[0] <= point[axis] <= bound[1]):
                return False
        return True


class KDTreeOptimizer:
    def __init__(self, fun: Function):
        self.fun: Function = fun

        self.minValue = 10 ** 10
        self.minPoint = None
        self.rootCube: Cube = None
        self.queue: List[List[float]] = []
        self.endCubes: List[Cube] = []
        self.parentCubes: List[Cube] = []
        self.init()

    def init(self):
        self.rootCube = Cube(self.fun.bounds)
        self.rootCube.value = self.fun(self.rootCube.center)

        self.queue = [self.rootCube.vector]
        self.endCubes = [self.rootCube]

    def nextEndCube(self):
        info = {'value': [], 'volume': []}
        for cube in self.endCubes:
            info['value'].append(cube.value)
            info['volume'].append(cube.volume)

        lowValue = 1 - normalizeVector(info['value'])
        highVolume = normalizeVector(info['volume'])

        rank = highVolume + lowValue

        bestRank = np.argsort(rank)[-1]
        return (self.endCubes[bestRank], bestRank)

    def nextPoint(self):
        # RETURN POINTS FROM QUEUE IF EXISTS
        if self.queue:
            point = self.queue[0]
            self.queue.pop(0)
            return point

        # SEARCH NEXT CUBE FOR PARTITIONING
        nextCube, i = self.nextEndCube()

        # DRAW NEIGHBOUR CUBES, MINS, CANDIDATES
        mins = []
        for cube in self.endCubes:
            if cube.isLocalMin:
                mins.append(cube)
        Models.drawNearestPoints(nextCube)

        Models.localMins.setShapes([])
        print(f'Local mins:', len(mins))
        for min in mins:
            Models.drawLocalMins(min.cubesInLocalMin)

        # PARTITION CUBE
        paritionedCubes = nextCube.partition()

        # Remove CUBE FROM END CUBES AND ADD CUBE TO PARENT CUBES
        self.parentCubes.append(nextCube)
        self.endCubes.remove(nextCube)
        self.endCubes += paritionedCubes

        # ADD PARTITIONED CUBES CENTERS TO QUEUE
        for partitionedCube in paritionedCubes:
            partitionedCube.value = self.fun(partitionedCube.center)
            if partitionedCube.value < self.minValue:
                self.minValue = partitionedCube.value
                self.minPoint = partitionedCube.center
            self.queue.append(partitionedCube.vector)

        # RETURN NEXT POINT
        return self.nextPoint()

    def models(self):
        return [Models.grids, Models.adjecentLines, Models.localMins, Models.localMinsCandidates]


class Models:
    grids = Model(MODEL.GENERIC, GL.GL_LINES, 2, initBuffers=False)
    adjecentLines = Model(MODEL.GENERIC, GL.GL_LINES, 2, initBuffers=False)
    localMins = Model(MODEL.GENERIC, GL.GL_POINTS, 2, initBuffers=False)
    localMinsCandidates = Model(MODEL.GENERIC, GL.GL_POINTS, 2, initBuffers=False)

    @classmethod
    def initGrid(cls, cubes: List[Cube]):
        cls.grids.setShapes(cubes)

    @classmethod
    def initAdjecent(cls):
        cls.adjecentLines.setShapes([])

    @classmethod
    def drawGrid(cls, cube: Cube):
        shape = Shape()
        shape.add_line(cube.start, [cube.bounds[0][1], cube.bounds[1][0]], [1, 0, 0, 1])
        shape.add_line(cube.start, [cube.bounds[0][0], cube.bounds[1][1]], [1, 0, 0, 1])
        shape.add_line([cube.bounds[0][1], cube.bounds[1][0]], cube.end, [1, 0, 0, 1])
        shape.add_line([cube.bounds[0][0], cube.bounds[1][1]], cube.end, [1, 0, 0, 1])
        cls.grids.addShape(shape)

    @classmethod
    def drawAdjecentLine(cls, startPoint, endPoint):
        line = Shape()
        line.add_line(
            startPoint, endPoint, [0, 1, 1, 1]
        ).add_line(
            [endPoint[0] - 0.2, endPoint[1] - 0.2], [endPoint[0] + 0.2, endPoint[1] + 0.2], [0, 1, 1, 1]
        ).add_line(
            [endPoint[0] - 0.2, endPoint[1] + 0.2], [endPoint[0] + 0.2, endPoint[1] - 0.2], [0, 1, 1, 1]
        ).add_line(
            [endPoint[0], endPoint[1] + 0.2], [endPoint[0], endPoint[1] - 0.2], [0, 1, 1, 1]
        ).add_line(
            [endPoint[0] + 0.2, endPoint[1]], [endPoint[0] - 0.2, endPoint[1]], [0, 1, 1, 1]
        )
        cls.adjecentLines.addShape(line)

    @classmethod
    def drawNearestPoints(cls, cube: Cube):
        Models.initAdjecent()
        center = cube.center
        for nearCube in cube.nearCubes:
            Models.drawAdjecentLine(center, nearCube.center)

    @classmethod
    def drawLocalMins(cls, cubes: List[Cube]):
        mins = Shape()
        for cube in cubes:
            mins.add_point(cube.center, [0, 0, 0, 1])
        cls.localMins.addShape(mins)

    @classmethod
    def drawLocalMinsCandidates(cls, cubes: List[Cube]):
        mins = Shape()
        for cube in cubes:
            mins.add_point(cube.center, [0, 0, 0, 1])
        cls.localMins.setShapes([mins])
