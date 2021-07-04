from __future__ import annotations

import copy
from statistics import mean
from typing import List

from OpenGL import GL

from src.gui.plot import Model, Shape
from src.gui.plot.model import MODEL
from src.optimization.space import Function


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
    def connectedCubes(self):
        if len(self.intersectingCubes) == 1:  # Ce je pika v centru kvadrata, vrni povezane kvadrate z kvadratom.
            return [
                       self.parentCube] + self.parentCube.adjacentCubes  # V nasprotnem primeru ce je pika povezana z vec kvadrati vrni kvadrate povezane z piko.
        else:
            return self.intersectingCubes

    @property
    def isLocalMinimum(self):
        for cube in self.connectedCubes:
            for point in [cube.centralPoint] + cube.parentsPoints:
                if self.value > point.value:
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

    def __init(self):
        # INIT CENTER POINT
        for bound in self.bounds:
            self.centralPoint.center.append(mean(bound))

        # INIT VOLUME
        self.volume = 1
        for axis in range(self.dim):
            self.volume *= abs(self.bounds[axis][1] - self.bounds[axis][0])

        if 2 <= self.dim <= 3:
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
        for point in [self.centralPoint] + self.parentsPoints:
            point.intersectingCubes.remove(self)


class KDTreeOptimizer:
    def __init__(self, fun: Function, maxGeneration=8, finishedLocalMinGeneration=20):
        self.fun: Function = fun

        self.globalMin = None

        self.cubes: List[Cube] = []
        self.points: List[Point] = []

        self.finishedMinimums: List[Point] = []
        self.unfinishedMinimums: List[Point] = []

        self.firstPassSearchFinished = False
        self.maxGeneration = maxGeneration
        self.currentSearchGeneration = 0
        self.finishedLocalMinGeneration = finishedLocalMinGeneration

        self.partitioningQueue: List[Cube] = []
        self.returningQueue: List[Point] = []

        self.init()

    def init(self):
        cube = Cube(self.fun.bounds)
        cube.generation = 0

        self.cubes = [cube]
        self.points = [cube.centralPoint]

        self.partitioningQueue = [cube]
        self.returningQueue = [cube.centralPoint]

    def minCubeFromCurrentSearchGeneration(self):
        minCube = None
        while minCube is None:
            for cube in self.cubes:
                if cube.generation == self.currentSearchGeneration:
                    if minCube is None or cube.centralPoint.value < minCube.centralPoint.value:
                        minCube = cube

            if minCube is None:
                self.currentSearchGeneration += 1

        self.currentSearchGeneration += 1
        if self.currentSearchGeneration >= self.maxGeneration:
            self.currentSearchGeneration = 0
        return minCube

    def minConnectedCubes(self):
        minPoint = None
        for point in self.points:
            if point.parentCube.generation < self.maxGeneration:
                if minPoint is None:
                    minPoint = point
                elif point.value < minPoint.value:
                    minPoint = point

        if minPoint is None:
            return []
        else:
            return minPoint.connectedCubes

    def isLocalMinFinished(self, point: Point):
        for cub in point.connectedCubes:
            if cub.generation < self.finishedLocalMinGeneration:
                return False
        return True

    def unfinishedLocalMinimums(self):
        unFinishedMins = []
        finishedMins = []
        for point in self.points:
            if point.isLocalMinimum:
                if self.isLocalMinFinished(point):
                    finishedMins.append(point)
                else:
                    unFinishedMins.append(point)

        self.finishedMinimums = sorted(finishedMins, key=lambda point: point.value)
        self.unfinishedMinimums = sorted(unFinishedMins, key=lambda point: point.value)

        cubes = []
        if len(unFinishedMins) > 0:
            unFinMin = self.unfinishedMinimums[0]
            for cub in unFinMin.connectedCubes:
                if cub.generation < self.finishedLocalMinGeneration:
                    cubes.append(cub)
        return cubes

    def nextPoint(self):
        # EVALUATE POINT AND THEN RETURN POINTS FROM QUEUE IF EXISTS
        if self.returningQueue:
            point = self.returningQueue[0]
            self.returningQueue.pop(0)
            point.value = self.fun(point.center)
            if self.globalMin is None or point.value < self.globalMin.value:
                self.globalMin = point
            print('   - POINT:', point.parentCube.generation)
            return point.vector

        if not self.partitioningQueue:
            if self.firstPassSearchFinished:
                cubes = self.unfinishedLocalMinimums()
                if len(cubes) > 0:
                    print("LOCAL MIN MODE")
                    self.partitioningQueue += cubes
                    return self.partitionNextQueueCube(self.finishedLocalMinGeneration)
                else:
                    print("SEARCH MODE")
                    self.partitioningQueue.append(self.minCubeFromCurrentSearchGeneration())
            else:
                print("NORMAL MODE")
                self.partitioningQueue += self.minConnectedCubes()

        return self.partitionNextQueueCube(self.maxGeneration)

    def partitionNextQueueCube(self, maxGeneration):

        # GET CUBE FROM QUEUE CUBES LIST
        while True:
            if not self.partitioningQueue:
                self.firstPassSearchFinished = True
                self.currentSearchGeneration = 0
                print('No cube in partitioning queue list satisfy requirements: Entering search mode...')
                return self.nextPoint()

            cube = self.partitioningQueue[0]
            self.partitioningQueue.pop(0)
            if cube.generation < maxGeneration:
                break

        # CHECK IF MAX GEN IS REACHED
        if not self.firstPassSearchFinished and cube.generation - 1 == maxGeneration:
            input('Max gen reached in normal mode: Entering search mode...')
            self.firstPassSearchFinished = True

        return self.partition(cube)

    def partition(self, cube: Cube):
        print(" - CUBE: ", cube.generation)
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
