import copy
import math
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
    def __init__(self, vector):
        self.vector = vector
        self.intersectingCubes = []

class Cube:

    def __init__(self, bounds: List[List[float]]):
        self.bounds = bounds
        self.dim = len(bounds)
        self.start = [b[0] for b in bounds]
        self.end = [b[1] for b in bounds]

        self.value = None
        self.center = []
        self.volume = 1

        self.adjacentEndCubes: List[Cube] = []
        self.centerIntersectingParents: List[Cube] = []

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

    def connectAdjacentEndCubes(self, cube):
        if cube not in self.adjacentEndCubes:
            self.adjacentEndCubes.append(cube)
        else:
            raise Exception("Cube is allready in this cubes neighbours, this should not happend!")

        if self not in cube.adjacentEndCubes:
            cube.adjacentEndCubes.append(self)
        else:
            raise Exception("Self is allready in cubes neighbours, this should not happend!")

    @property
    def vector(self):
        if not self.value:
            raise Exception("Cant get vector because cube is not jet evaluated!")
        return self.center + [self.value]

    def divide(self, axis):
        middleAxisPoint = mean(self.bounds[axis])
        lowerAxisBound = [self.bounds[axis][0], middleAxisPoint]
        upperAxisBound = [middleAxisPoint, self.bounds[axis][1]]
        lowerBounds = copy.deepcopy(self.bounds)
        upperBounds = copy.deepcopy(self.bounds)
        lowerBounds[axis] = lowerAxisBound
        upperBounds[axis] = upperAxisBound

        return [Cube(lowerBounds), Cube(upperBounds)]

    def partition(self):
        partCubes = [self]
        splitedCubes = []

        # DIVIDE CUBE TO CHILDRENS
        for axis in range(self.dim):
            for partCube in partCubes:
                splitedCubes += partCube.divide(axis)
            partCubes = splitedCubes
            splitedCubes = []

        # SET CUBE GENERATION NUMBER
        for partCube in partCubes:
            partCube.generation = self.generation + 1

        # CONNECT PARTITIONED CUBES WITH THEM SELFS
        for i in range(len(partCubes) - 1):
            for j in range(i + 1, len(partCubes)):
                partCubes[i].connectAdjacentEndCubes(partCubes[j])

        # CONNECT PARTITIONED CUBES WITH PARENT AND PARENTS PREACESSORS
        # ONLY IF PARTITIONED CUBES CONTAINS PREAESSOR
        for partCube in partCubes:
            partCube.centerIntersectingParents.append(self)
            for preacessor in self.centerIntersectingParents:
                if partCube.contains(preacessor.center):
                    partCube.centerIntersectingParents.append(preacessor)

        # CONNECT PARTITIONED CUBES WITH PARENT NEIGHBOURS
        # ONLY IF PARTITIONED CUBE OVERLAPS WITH PARENT NEIGHBOUR
        for parentNeighbour in self.adjacentEndCubes:
            for partCube in partCubes:
                if parentNeighbour.overlapsWith(partCube):
                    partCube.connectAdjacentEndCubes(parentNeighbour)

        # DISCONNECT NEIGHBOURS WITH FROM OLD CUBE THAT HAVE BEEN PARTITIONED
        for neighbour in self.adjacentEndCubes:
            neighbour.adjacentEndCubes.remove(self)

        # REMOVE ANY CONNECTION WITH NEAR RECTANGLES
        self.adjacentEndCubes = None
        self.centerIntersectingParents = None

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
    def nearCubes(self):
        return self.adjacentEndCubes + self.centerIntersectingParents

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

        self.rootCube: Cube = None
        self.queueCubes: List[Cube] = []
        self.queue: List[List[float]] = []
        self.endCubes: List[Cube] = []
        self.init()

    def init(self):
        self.rootCube = Cube(self.fun.bounds)
        self.rootCube.value = self.fun(self.rootCube.center)

        self.queue = [self.rootCube.vector]
        self.endCubes = [self.rootCube]
        self.queueCubes = [self.rootCube]

    def nextEndCubes(self):
        minCube = self.endCubes[0]
        for cube in self.endCubes:
            if cube.value < minCube.value:
                minCube = cube
        return [minCube] + minCube.adjacentEndCubes

    def nextPoint(self):
        # RETURN POINTS FROM QUEUE IF EXISTS
        if self.queue:
            point = self.queue[0]
            self.queue.pop(0)
            return point

        if not self.queueCubes:
            self.queueCubes += self.nextEndCubes()

        # GET CUBE FROM QUEUE CUBES LIST
        nextCube = self.queueCubes[0]
        self.queueCubes.pop(0)

        # PARTITION CUBE
        paritionedCubes = nextCube.partition()

        # Remove CUBE FROM END CUBES AND ADD CUBE TO PARENT CUBES
        self.parentCubes.append(nextCube)
        self.endCubes.remove(nextCube)
        self.endCubes += paritionedCubes

        # ADD PARTITIONED CUBES CENTERS TO QUEUE
        for partitionedCube in paritionedCubes:
            partitionedCube.value = self.fun(partitionedCube.center)
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
