from __future__ import annotations

import copy
from statistics import mean
from typing import List, Callable

import numpy as np
from OpenGL import GL

from src.gui.plot import Model, Shape
from src.gui.plot.model import MODEL

# TODO: DO NOT MAKE A TREE THERE SHALL BE ONLY END CUBES WITH DOUBLE CONNECTED POINTS CONNECTIONS
# TODO: SEARCH MIN CUBE FROM LIST OF CONNECTED CUBES TO A POINT!
# TODO: THEN AFTER FIRST PASS DIVIDE CUBES

class Point:
    def __init__(self, center, parentCube: Cube):
        self.value = None
        self.center = center
        self.parentCube: Cube = parentCube
        self.intersectingCubes = [parentCube]

    @property
    def vector(self):
        if self.value is None:
            raise Exception("Cant get vector because point is not jet evaluated!")
        return self.center + [self.value]

    @property
    def generation(self):
        return mean([cube.generation for cube in self.intersectingCubes])

    @property
    def closeCubes(self):
        if len(self.intersectingCubes) == 1:  # Ce je pika v centru kvadrata, vrni povezane kvadrate z kvadratom.
            return [self.parentCube] + self.parentCube.adjacentCubes  # V nasprotnem primeru ce je pika povezana z vec kvadrati vrni kvadrate povezane z piko.
        else:
            return self.intersectingCubes

    @property
    def closePoints(self):
        points = []
        for closeCube in self.closeCubes:
            for closePoint in closeCube.intersectingPoints:
                if closePoint is not self and closePoint not in points:
                    points.append(closePoint)
        return points

    @property
    def isLocalMin(self):
        for closeCube in self.closeCubes:
            if closeCube.centralPoint.value < self.value:
                return False
        return True

class Cube:

    def __init__(self, bounds: List[List[float]]):
        self.bounds = bounds
        self.dim = len(bounds)
        self.start = [b[0] for b in bounds]
        self.end = [b[1] for b in bounds]

        self.volume = None
        self.generation = None
        self.disconnected = False

        self.centralPoint: Point = Point([], self)
        self.parentsPoints: List[Point] = []
        self.adjacentCubes: List[Cube] = []

        self.__init()

    @property
    def meanValue(self):
        values = []
        for point in self.intersectingPoints:
            values.append(point.value)
        return mean(values)

    @property
    def intersectingPoints(self):
        return [self.centralPoint] + self.parentsPoints

    def __init(self):
        # INIT CENTER POINT
        for bound in self.bounds:
            self.centralPoint.center.append(mean(bound))

        # INIT VOLUME
        self.volume = 1
        for axis in range(self.dim):
            self.volume *= abs(self.bounds[axis][1] - self.bounds[axis][0])

        if 2 == self.dim:
            Models.drawGrid(self)

    def divide(self, axis):
        middleaxispoint = mean(self.bounds[axis])
        loweraxisbound = [self.bounds[axis][0], middleaxispoint]
        upperaxisbound = [middleaxispoint, self.bounds[axis][1]]
        lowerbounds = copy.deepcopy(self.bounds)
        upperbounds = copy.deepcopy(self.bounds)
        lowerbounds[axis] = loweraxisbound
        upperbounds[axis] = upperaxisbound

        return [Cube(lowerbounds), Cube(upperbounds)]

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

    def contains(self, vector: List[float]):
        for axis, bound in enumerate(self.bounds):
            if not (bound[0] <= vector[axis] <= bound[1]):
                return False
        return True

    def connectWithAdjacentCube(self, cube):
        if cube not in self.adjacentCubes:
            self.adjacentCubes.append(cube)
        else:
            raise Exception("Cube is already in this cubes neighbours list, this should not happened!")

        if self not in cube.adjacentCubes:
            cube.adjacentCubes.append(self)
        else:
            raise Exception("Self is already in cubes neighbours list, this should not happened!")

    def connectWithParentPoint(self, point: Point):
        if point not in self.parentsPoints:
            self.parentsPoints.append(point)
        else:
            raise Exception("Point is already in this parents points list, this should not happened!")

        if self not in point.intersectingCubes:
            point.intersectingCubes.append(self)
        else:
            raise Exception("Self is already in point's intersecting cubes list, this should not happened!")

    def partition(self):
        partCubes = [self]
        splitedCubes = []

        # DIVIDE CUBE TO CHILDRENS
        for axis in range(self.dim):
            for partCube in partCubes:
                splitedCubes += partCube.divide(axis)
            partCubes = splitedCubes
            splitedCubes = []

        # CONNECT PARTITIONED CUBES WITH CURENT CUBES PARENTS POINT
        # CREATE POINT FOR CURRENT PARITIONED CUBE
        for partCube in partCubes:
            partCube.generation = self.generation + 1
            partCube.connectWithParentPoint(self.centralPoint)
            for parentPoint in self.parentsPoints:
                if partCube.contains(parentPoint.center):
                    partCube.connectWithParentPoint(parentPoint)

        # CONNECT PARTITIONED CUBES WITH THEM SELFS
        for i in range(len(partCubes) - 1):
            for j in range(i + 1, len(partCubes)):
                partCubes[i].connectWithAdjacentCube(partCubes[j])

        # CONNECT PARTITIONED CUBES WITH PARENT NEIGHBOURS
        for partCube in partCubes:
            for adjacentCube in self.adjacentCubes:
                if adjacentCube.overlapsWith(partCube):
                    partCube.connectWithAdjacentCube(adjacentCube)

        # DISCONNECT FROM ALL ASSOCIATED POINTS AND CUBES
        self.disconnect()

        return partCubes

    def disconnect(self):
        self.disconnected = True

        # DISCONNECT NEIGHBOURS WITH FROM OLD CUBE THAT HAVE BEEN PARTITIONED
        for adjacentCube in self.adjacentCubes:
            adjacentCube.adjacentCubes.remove(self)

        # DISCONNECT FROM ALL POINTS THAT ARE IN CUBE
        for point in self.intersectingPoints:
            point.intersectingCubes.remove(self)

class KDTreeOptimizer:
    def __init__(self, fun: Callable, bounds: List[List[float]],  maxGeneration=15, maxIterations=2000):
        self.fun: Callable = fun
        self.bounds = bounds

        self.cubes: List[Cube] = []
        self.points: List[Point] = []

        self.partitioningQueue: List[Cube] = []
        self.returningQueue: List[Point] = []

        self.globalMin = None
        self.maxIterations = maxIterations

        self.currentMinGeneration = 0
        self.currentSearchGeneration = self.currentMinGeneration
        self.maxGeneration = maxGeneration

        self.init()

    def init(self):
        cube = Cube(self.bounds)
        cube.generation = 0

        self.cubes = [cube]
        self.points = [cube.centralPoint]

        self.partitioningQueue = [cube]
        self.returningQueue = [cube.centralPoint]

    def lowestLocalMinCubeFromCurrentSearchGeneration(self):
        # Search most connected cube
        conCubes = sorted(self.cubes, key=lambda c: (len(c.adjacentCubes), -c.generation, -sum([(ele-self.globalMin.vector[i])**2 for i, ele in enumerate(c.centralPoint.vector)])), reverse=True)[:2**len(self.bounds)]

        # Search lowest local minimum from current generation
        localMin = None
        minPoint = None
        while [localMin, minPoint].count(None) == 2:
            for point in self.points:
                for closeCube in point.intersectingCubes:
                    if closeCube.generation <= self.currentSearchGeneration:
                        if point.isLocalMin:
                            if localMin is None or point.value < localMin.value:
                                localMin = point
                        else:
                            if minPoint is None or point.value < minPoint.value:
                                minPoint = point
                        break
            self.currentSearchGeneration += 1

        # Reset current search generation
        if self.currentSearchGeneration >= self.maxGeneration:
            self.currentSearchGeneration = 0

        cubes = []
        if localMin is not None:
            cubes += localMin.intersectingCubes
        otherCubes = conCubes + [sorted(minPoint.intersectingCubes, key=lambda cube: cube.generation)[0]]
        for oc in otherCubes:
            if oc not in cubes:
                cubes.append(oc)
        return cubes

    def nextPoint(self):
        # EVALUATE POINT AND THEN RETURN POINTS FROM QUEUE IF EXISTS
        if self.returningQueue:
            point = self.returningQueue[0]
            self.returningQueue.pop(0)
            point.value = self.fun(point.center)
            if self.globalMin is None or point.value < self.globalMin.value:
                self.globalMin = point
            return point.vector

        if not self.partitioningQueue:
            self.partitioningQueue += self.lowestLocalMinCubeFromCurrentSearchGeneration()

        return self.partitionNextQueueCube()

    def partitionNextQueueCube(self):

        # GET CUBE FROM QUEUE CUBES LIST
        while True:
            if not self.partitioningQueue:
                self.currentSearchGeneration = 0
                return self.nextPoint()

            cube = self.partitioningQueue[0]
            self.partitioningQueue.pop(0)
            if cube.generation < self.maxGeneration:
                break

        return self.partition(cube)

    def partition(self, cube: Cube):
        children = cube.partition()

        # Remove CUBE FROM END CUBES AND ADD CUBE TO PARENT CUBES
        self.cubes.remove(cube)
        self.cubes += children

        # ADD PARTITIONED CUBES CENTERS TO QUEUE
        for child in children:
            if child.centralPoint not in self.points:
                self.points.append(child.centralPoint)
            else:
                raise Exception("Point is allready in list of all points!")

            if child.centralPoint not in self.returningQueue:
                self.returningQueue.append(child.centralPoint)
            else:
                raise Exception("Point is allready in queue list!")

        # RETURN NEXT POINT
        return self.nextPoint()

    def models(self):
        return [Models.grids, Models.localMins]

class Models:
    grids = Model(MODEL.GENERIC, GL.GL_LINES, 2, initBuffers=False)
    localMins = Model(MODEL.GENERIC, GL.GL_LINES, 3, initBuffers=False)

    @classmethod
    def initGrid(cls, cubes: List[Cube]):
        cls.grids.setShapes(cubes)

    @classmethod
    def initLocalMins(cls, points: List[Point]):
        cls.localMins.setShapes(points)

    @classmethod
    def drawGrid(cls, cube: Cube):
        shape = Shape()
        shape.add_line(cube.start, [cube.bounds[0][1], cube.bounds[1][0]], [1, 0, 0, 1])
        shape.add_line(cube.start, [cube.bounds[0][0], cube.bounds[1][1]], [1, 0, 0, 1])
        shape.add_line([cube.bounds[0][1], cube.bounds[1][0]], cube.end, [1, 0, 0, 1])
        shape.add_line([cube.bounds[0][0], cube.bounds[1][1]], cube.end, [1, 0, 0, 1])
        cls.grids.addShape(shape)

    @classmethod
    def drawLocalMin(cls, point: Point):
        shape = Shape()
        shape.add_line(point.center + [-100], [point.center[0]+0.01, point.center[1]+0.01] + [100],[1, 0, 0, 1])
        cls.localMins.addShape(shape)
