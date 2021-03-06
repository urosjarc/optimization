import math
from random import randint, choices
from src.math.linalg import normalizeVector, angle, pointInTriangle
import numpy as np
from typing import *

from src.math.space import Function


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

    def pointDistance(self, point, onSurface):
        if onSurface:
            return abs(np.linalg.norm(np.array(self.vector) - np.array(point.vector)))
        else:
            return abs(np.linalg.norm(self.vector3D - point.vector3D))

    def vectorDistance(self, vector, onSurface):
        if onSurface:
            return abs(np.linalg.norm(np.array(self.vector) - np.array(vector)))
        else:
            return abs(np.linalg.norm(self.vector3D - vector))

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

        # raise Exception("Point is in border but I didn't find triangle... This is bad!")
        return self.triangles


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.points = [p1, p2]
        for p in self.points:
            p.lines.append(self)

    def size(self, onSurface):
        return self.points[0].pointDistance(self.points[1], onSurface)

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
        dist = self.points[0].pointDistance(point, onSurface)
        dist += self.points[1].pointDistance(point, onSurface)
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
        return sorted(self.lines, key=lambda l: abs(l.size(onSurface)), reverse=fromBigToLow)

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
    def __init__(self, space: Function, maxEval):
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []

        self.queue_borderPoints: List[Point] = []
        self.queue_cheepTriangles: List[Triangle] = []
        self.queue_minConnectedTriangles: List[Triangle] = []
        self.queue_minersTriangles: List[Triangle] = []

        self.searchChoice = {
            'search_global_min': 0.2,
            'search_local_min': 0.3,
            'search_best_tri': 0.5
        }

        self.evalMax = maxEval
        self.evaluation = 0

        self.init()

        self.maxLocalMinLineSize = self.triangles[0].biggestLineSize(onSurface=True) * 5 * 10 ** -4
        self.maxGlobalMinLineSize = self.triangles[0].biggestLineSize(onSurface=True) * 10 ** -6

    def init(self):
        leftdown, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][0])
        leftup, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][1])
        rightdown, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][0])
        rightup, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][1])

        self.queue_borderPoints = [leftdown, leftup, rightdown, rightup]

        lines = [
            Line(leftup, leftdown),
            Line(leftdown, rightdown),
            Line(rightdown, leftup),
            Line(leftup, rightup),
            Line(rightup, rightdown),
        ]
        self.triangles += [
            Triangle(lines[:3]),
            Triangle(lines[2:])
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
        print(f'EVAL: {self.evaluation}')

        # Return border points on start
        if len(self.queue_borderPoints) > 0:
            point = self.queue_borderPoints[0]
            self.queue_borderPoints.pop(0)
            self.evaluation += 1
            return point.vector3D

        # Return cheep triangles that doesn't need new point evaluation
        while len(self.queue_cheepTriangles) > 0:
            triangle = self.queue_cheepTriangles[0]
            self.queue_cheepTriangles.pop(0)
            point, cmd = self.partition(triangle)
            if cmd == 'make':
                raise Exception("ERR")

        # Return triangles connected to local minimums
        while len(self.queue_minConnectedTriangles) > 0:
            triangle = self.queue_minConnectedTriangles[0]
            self.queue_minConnectedTriangles.pop(0)
            if not triangle.splited:
                point, cmd = self.partition(triangle)
                if cmd == 'get':
                    raise Exception("ERR")
                self.evaluation += 1
                return point.vector3D

        searchChoice = choices(list(self.searchChoice.keys()), weights=list(self.searchChoice.values()))[0]

        # Explore space
        if searchChoice == 'search_best_tri':
            triangle = self.getBestRankedTriangle()
            point, cmd = self.partition(triangle)
            if cmd == 'get':
                raise Exception("ERR")
            self.evaluation += 1
            return point.vector3D
        elif searchChoice == 'search_local_min':
            self.addMinConnectedTrianglesToQueue(self.maxLocalMinLineSize)
            return self.nextPoint()
        elif searchChoice == 'search_global_min':
            self.addMinConnectedTrianglesToQueue(self.maxGlobalMinLineSize)
            return self.nextPoint()

    def addMinConnectedTrianglesToQueue(self, maxLineSize):
        activeMins, unactiveMins = self.getMinimums(maxLineSize)

        # Add lowest point triangles to queue list.
        if len(activeMins) > 0:
            bestMinimum = activeMins[0]
            triangles = bestMinimum.connectedTriangles(self.space.bounds, simple=False)
            for t in triangles:
                if t not in self.queue_minConnectedTriangles:
                    self.queue_minConnectedTriangles.append(t)

    def getBestRankedTriangle(self):
        maxEval = randint(8, 14)
        while True:
            triangles = [t for t in self.triangles if t.eval < maxEval]
            if len(triangles) > 0:
                break
            maxEval += 1

        info = {'evalDiff': [], 'meanValue': [], 'eval': []}
        for t in triangles:
            info['evalDiff'].append(t.evalDiff)
            info['meanValue'].append(t.meanValue())
            info['eval'].append(t.eval)

        highEvalDiff = normalizeVector(info['evalDiff'])
        lowEval = 1 - normalizeVector(info['eval'])
        lowValue = 1 - normalizeVector(info['meanValue'])

        rank = highEvalDiff + lowEval + 3 * lowValue

        bestRank = np.argsort(rank)[-1]
        return triangles[bestRank]

    def getMinimums(self, maxLineSizeOfConnectedTriangle):
        activeMinimums = []
        unactiveMinimums = []
        for t in self.triangles:
            lowPoint = t.lowestPoint()
            if t.biggestLineSize(onSurface=True) < maxLineSizeOfConnectedTriangle:
                isNewMin = True
                for umin in unactiveMinimums:
                    if umin.pointDistance(lowPoint, onSurface=True) < maxLineSizeOfConnectedTriangle * 2:
                        isNewMin = False
                        break
                if isNewMin:
                    unactiveMinimums.append(lowPoint)
                continue

            isLowest = True
            for tc in t.connectedTriangles(self.space.bounds, simple=True):
                if lowPoint.value > tc.lowestPoint().value:
                    isLowest = False
                    break

            if isLowest:
                isNewMin = True
                for amin in activeMinimums:
                    if lowPoint.pointDistance(amin, onSurface=True) < maxLineSizeOfConnectedTriangle:
                        isNewMin = False
                        break
                if isNewMin:
                    activeMinimums.append(lowPoint)

        return sorted(activeMinimums, key=lambda p: p.value, reverse=False), unactiveMinimums

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
        for t in triangle.coincidingTriangles(onSurface=True, searchSpace=self.space.bounds,
                                              simple=True) + newTriangles:
            if t not in self.queue_cheepTriangles:
                NmX, NmY = t.newPointVector(onSurface=True)
                if self.pointExists(NmX, NmY):
                    self.queue_cheepTriangles.append(t)

        return mPoint, cmd
