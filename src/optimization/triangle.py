import math
from random import randint, random

from src.app import PlotInterface
from src.math import Space, normalizeVector, angle, pointInTriangle
import numpy as np
from typing import *


class Point:
    def __init__(self, x, y, value):
        self.vector = [x, y]
        self.vector3D = np.array([x, y, value])
        self.x = x
        self.y = y
        self.value = value
        self.triangles: List[Triangle] = []
        self.lines = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def distance(self, point, onSurface):
        if onSurface:
            return np.linalg.norm(np.array(self.vector) - np.array(point.vector))
        else:
            return np.linalg.norm(self.vector3D - point.vector3D)

    def connectedTriangles(self, searchSpace, simple):
        if simple:
            return self.triangles

        forceSum = np.array([0., 0.])
        vector = np.array(self.vector)
        for t in self.triangles:
            center = t.center(onSurface=True)
            force = vector - center
            forceSum += force
        forceSum = normalizeVector(forceSum) * 10 ** -12
        nextPosition = vector + forceSum

        # Test if next position is in search space
        for i in range(len(searchSpace)):
            low, high = searchSpace[i]
            ax = nextPosition[i]
            if not (low < ax < high):
                return self.triangles

        # Test if point is in connected triangles
        for t in self.triangles:
            p1, p2, p3 = t.points
            isIn = pointInTriangle(nextPosition, p1.vector, p2.vector, p3.vector)
            if isIn:
                return self.triangles

        # In which triangle is this next position?
        queue = [self.triangles[0]]
        queueIndex = 0
        while queueIndex < len(queue):
            triInQueue = queue[queueIndex]
            queueIndex += 1

            p1, p2, p3 = triInQueue.points
            isIn = pointInTriangle(nextPosition, p1.vector, p2.vector, p3.vector)
            if isIn:
                return self.triangles + [triInQueue]

            for p in triInQueue.points:
                for t in p.triangles:
                    if t not in queue:
                        queue += p.triangles

        raise Exception("Point is in border but I didn't find triangle... This is bad!")


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.points = [p1, p2]
        for p in self.points:
            p.lines.append(self)

    def size(self, onSurface):
        return self.points[0].distance(self.points[1], onSurface)

    def center(self, onSurface):
        if onSurface:
            return np.mean([p.vector for p in self.points], axis=0)
        else:
            return np.mean([p.vector3D for p in self.points], axis=0)

    def mutualPoint(self, line):
        p1 = set(self.points)
        p2 = set(line.points)
        return list(p1.intersection(p2))[0]

    def isOnLine(self, point: Point, onSurface):
        dist = self.points[0].distance(point, onSurface)
        dist += self.points[1].distance(point, onSurface)
        return abs(dist - self.size(onSurface)) == 0

    def coinciding(self, line, onSurface):
        p1, p2 = line.points
        sp1, sp2 = self.points
        return (self.isOnLine(p1, onSurface) and self.isOnLine(p2, onSurface)) or (
                line.isOnLine(sp1, onSurface) and line.isOnLine(sp2, onSurface)
        )


class Triangle:
    def __init__(self, lines, evalDiff=10 ** 10, eval=0):
        self.splited = False
        self.lines: List[Line] = lines
        self.evalDiff: float = abs(evalDiff)
        self.eval = eval
        self.points: List[Point] = []

        # Get unique points
        pts = set()
        for l in self.lines:
            for p in l.points:
                pts.add(p)
        self.points += list(pts)

        # Add triangle to points lists
        for p in self.points:
            p.triangles.append(self)

    def __str__(self):
        return f'TRI[cen={self.center()}, eval={self.eval}, evalDiff={self.evalDiff}]'

    def meanValue(self):
        vals = [p.value for p in self.points]
        return sum(vals) / 3

    def lowestPoint(self):
        return sorted(self.points, key=lambda p: p.value, reverse=False)[0]

    def normalVector(self):
        """Returns normal vector which is turned upward"""
        v1 = self.points[0].vector3D
        v2 = self.points[1].vector3D
        v3 = self.points[2].vector3D
        dv1 = v2 - v1
        dv2 = v3 - v1
        normal1 = np.cross(dv1, dv2)
        if normal1[-1] < 0:
            normal1 = np.cross(dv2, dv1)
        return normal1 / 2

    def fractureRatio(self):
        deg = []
        for tri in self.coincidingTriangles(onSurface=False):
            deg.append(angle(self.normalVector(), tri.normalVector()))
        return np.median(deg) / (math.pi / 2)

    def volume(self):
        A, B, C = self.points
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y)) / 2)

    def sortedLines(self, onSurface, fromBigToLow=True):
        return sorted(self.lines, key=lambda l: l.size(onSurface), reverse=fromBigToLow)

    def biggestLineSize(self, onSurface):
        bigestLine = self.sortedLines(onSurface, fromBigToLow=True)[0]
        return bigestLine.size(onSurface)

    def coincidingTriangles(self, onSurface, searchSpace, simple):
        tri = []
        for t in self.connectedTriangles(searchSpace, simple):
            isConn = False
            for sline in self.lines:
                for line in t.lines:
                    if sline.coinciding(line, onSurface=onSurface):
                        isConn = True
                        break
                if isConn:
                    break
            if isConn:
                tri.append(t)

        return tri

    def connectedTriangles(self, searchSpace, simple):
        tri: List[Triangle] = []
        for p in self.points:
            for t in p.connectedTriangles(searchSpace, simple):
                if t != self and t not in tri:
                    tri.append(t)
        return tri

    def newPointVector(self, onSurface):
        bigestLine = self.sortedLines(onSurface, fromBigToLow=True)[0]
        return bigestLine.center(onSurface)

    def center(self, onSurface):
        if onSurface:
            return np.mean([np.array(p.vector) for p in self.points], axis=0)
        return np.mean([p.vector3D for p in self.points], axis=0)


class TriangleOptimizer:
    def __init__(self, space: Space, draw: PlotInterface, maxEval):
        self.draw = draw
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []

        self.queue_borderPoints: List[Point] = []
        self.queue_cheepTriangles: List[Triangle] = []
        self.queue_minConnectedTriangles: List[Triangle] = []

        self.minPoint = None
        self.maxEval = maxEval
        self.eval = 0
        self.maxLocalMinLineSize = 10 ** -3
        self.minTriangleEval = 5
        self.init()

    def init(self):
        leftdown, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][0])
        leftup, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][1])
        rightdown, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][0])
        rightup, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][1])

        self.queue_borderPoints = [leftdown, leftup, rightdown, rightup]

        l1 = [
            Line(leftup, leftdown),
            Line(leftdown, rightdown),
            Line(rightdown, leftup),
            Line(leftup, rightup),
            Line(rightup, rightdown),
        ]
        self.triangles += [
            Triangle(l1[:3]),
            Triangle(l1[2:])
        ]

    def pointExists(self, x, y):
        for p in self.points:
            if p.vector == [x, y]:
                return True
        return False

    def getOrMakePoint(self, x, y):
        for p in self.points:
            if p.vector == [x, y]:
                return p, "get"

        p = Point(x, y, self.space([x, y]))
        self.points.append(p)
        return p, "make"

    def nextPoint(self):
        self.eval += 1
        print(self.eval)

        if len(self.queue_borderPoints) > 0:
            point = self.queue_borderPoints[0]
            self.queue_borderPoints.pop(0)
            return point.vector

        while len(self.queue_cheepTriangles) > 0:
            triangle = self.queue_cheepTriangles[0]
            self.queue_cheepTriangles.pop(0)
            point, cmd = self.partition(triangle)
            if cmd == 'make':
                raise Exception("ERR")

        while len(self.queue_minConnectedTriangles) > 0:
            triangle = self.queue_minConnectedTriangles[0]
            self.queue_minConnectedTriangles.pop(0)
            if not triangle.splited:
                point, cmd = self.partition(triangle)
                if cmd == 'get':
                    raise Exception("ERR")
                return point.vector

        if self.eval % 3 != 0:
            localMinimums = self.getLowestActiveMinimums()
            if len(localMinimums) > 0:
                bestMinimum = localMinimums[0]
                triangles = bestMinimum.connectedTriangles(self.space.bounds, simple=False)
                self.draw.drawTriangles(triangles, permament=False)
                for t in triangles:
                    if t not in self.queue_minConnectedTriangles:
                        self.queue_minConnectedTriangles.append(t)
                return self.nextPoint()

        triangle = self.getBestRankedTriangle()
        point, cmd = self.partition(triangle)
        if cmd == 'get':
            raise Exception("ERR")
        return point.vector

    def getBestRankedTriangle(self):
        while True:
            triangles = [t for t in self.triangles if t.eval < (self.minTriangleEval+random()*(20-self.minTriangleEval))]
            if len(triangles) > 0:
                break
            else:
                self.minTriangleEval += 1

        evalDiff = normalizeVector([t.evalDiff for t in triangles])
        volume = normalizeVector([t.volume() for t in triangles])
        meanValue = 1 - normalizeVector([t.meanValue() for t in triangles])

        rank = volume + evalDiff + meanValue * 2

        bestRank = np.argsort(rank)[-1]
        return triangles[bestRank]

    def getLowestActiveMinimums(self):
        localMin = []
        for t in self.triangles:

            if t.biggestLineSize(onSurface=True) < self.maxLocalMinLineSize:
                continue

            lowPoint = t.lowestPoint()
            isLowest = True
            for tc in t.connectedTriangles(self.space.bounds, simple=True):
                if lowPoint.value > tc.lowestPoint().value:
                    isLowest = False
                    break

            if isLowest:
                localMin.append(lowPoint)

        activeMinimums = sorted(localMin, key=lambda p: p.value, reverse=False)
        self.draw.localMinimum([p.vector for p in activeMinimums])
        return activeMinimums

    def partition(self, triangle: Triangle):
        # Remove triangle from triangles, and from lines triangle list
        if not triangle.splited:
            if triangle in self.queue_cheepTriangles:
                raise Exception(f"Triangle emerge multiple times in queue list, but is allready splited!")
            triangle.splited = True
            self.triangles.remove(triangle)
            for p in triangle.points:
                p.triangles.remove(triangle)
        # If triangle is allready splited he was added to self.queue list multiple times!
        else:
            raise Exception("Triangle was allready splited")

        # Get new point vector of splited triangle line, and create new point from that
        line0, line1, line2 = triangle.sortedLines(onSurface=True, fromBigToLow=True)
        mX, mY, mVal = line0.center(onSurface=False)
        mPoint, cmd = self.getOrMakePoint(mX, mY)
        evalDiff = mPoint.value - mVal

        # Get other 3 points
        highPoint = line1.mutualPoint(line2)
        bottomPoint1 = line0.mutualPoint(line1)
        bottomPoint2 = line0.mutualPoint(line2)

        # Create list of new lines and triangles.
        newTrianglesLines = [
            Line(mPoint, bottomPoint1),
            line1,
            Line(highPoint, mPoint),
            Line(mPoint, bottomPoint2),
            line2,
        ]
        newTriangles = [
            Triangle(newTrianglesLines[:3], evalDiff=evalDiff, eval=triangle.eval + 1),
            Triangle(newTrianglesLines[2:], evalDiff=evalDiff, eval=triangle.eval + 1)
        ]

        # Add new triangles to the mix
        self.triangles += newTriangles

        # Partition connected triangles and new triangles if no point will be created in the process of partitioning
        for t in triangle.coincidingTriangles(onSurface=True, searchSpace=self.space.bounds, simple=True) + newTriangles:
            if t not in self.queue_cheepTriangles:
                NmX, NmY = t.newPointVector(onSurface=True)
                if self.pointExists(NmX, NmY):
                    self.queue_cheepTriangles.append(t)

        return mPoint, cmd
