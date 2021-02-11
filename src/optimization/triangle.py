import math
from src.app import PlotInterface
from src.math import Space, normalizeVector, angle
import numpy as np
from typing import *


class Point:
    def __init__(self, x, y, value):
        self.vector = [x, y]
        self.vector3D = np.array([x, y, value])
        self.x = x
        self.y = y
        self.value = value
        self.triangles = []
        self.lines = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def distance(self, point, onSurface):
        if onSurface:
            return np.linalg.norm(np.array(self.vector) - np.array(point.vector))
        else:
            return np.linalg.norm(self.vector3D - point.vector3D)


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.points = [p1, p2]
        for p in self.points:
            p.lines.append(self)

    def size(self, onSurface):
        return self.points[0].distance(self.points[1], onSurface)

    def center(self, onSurface):
        if onSurface:
            return np.mean([p.vector for p in self.points], axis=0).tolist()
        else:
            return np.mean([p.vector3D for p in self.points], axis=0).tolist()

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

    def coincidingTriangles(self, onSurface):
        tri = []
        for t in self.connectedTriangles():
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

    def connectedTriangles(self):
        tri: List[Triangle] = []
        for p in self.points:
            for t in p.triangles:
                if t != self and t not in tri:
                    tri.append(t)
        return tri

    def newPointVector(self, onSurface):
        bigestLine = self.sortedLines(onSurface, fromBigToLow=True)[0]
        return bigestLine.center(onSurface)

    def center(self):
        return np.mean([p.vector3D for p in self.points], axis=0)


class TriangleOptimizer:
    def __init__(self, space: Space, draw: PlotInterface, maxEval):
        self.draw = draw
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []
        self.queue: List[Triangle] = []

        self.eval = 0
        self.minPoint = None
        self.maxEval = maxEval
        self.init()

    def init(self):
        leftdown, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][0])
        leftup, _ = self.getOrMakePoint(self.space.bounds[0][0], self.space.bounds[1][1])
        rightdown, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][0])
        rightup, _ = self.getOrMakePoint(self.space.bounds[0][1], self.space.bounds[1][1])

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

    def drawTriangles(self, triangles: List[Triangle], permament):
        if permament:
            for t in triangles:
                self.draw.poligon([p.vector for p in t.points], permament=permament)
        else:
            vectors = []
            for t in triangles:
                vectors += [p.vector for p in t.points]
            self.draw.poligon(vectors, permament=permament)

    def nextPoint(self):

        while True:
            if len(self.queue) > 0:
                triangle = self.queue[0]
                self.queue.pop(0)
                point, cmd = self.partition(triangle)
                if cmd == 'make':
                    raise Exception("ERR")
            else:
                triangle = self.getTriangleCandidate()
                point, cmd = self.partition(triangle)
                if cmd == 'get':
                    raise Exception("ERR")
                break

        self.eval += 1
        print(self.eval)
        self.draw.localMinimum([p.vector for p in self.getLocalMinimums()])

        return point.vector

    def getTriangleCandidate(self):
        ts = self.triangles
        minEval = int(5 + (self.eval/self.maxEval)*13)

        if self.eval < 30:
            return sorted(ts, key=lambda t: t.eval)[0]


        ts_cut = [t for t in ts]
        # while True:
        #     ts_cut = [t for t in ts if t.eval < minEval]
        #     if len(ts_cut) == 0:
        #         minEval += minEval/10
        #     else:
        #         break

        lowestValue = 1 - normalizeVector([t.lowestPoint().value for t in ts_cut])

        higestRank = np.argsort(lowestValue)[-1]

        topTri = ts_cut[higestRank]
        conTri = [t for t in topTri.connectedTriangles()]

        if len(conTri)>0:
            return sorted(conTri, key=lambda t: t.volume(), reverse=True)[0]
        else:
            return topTri

    def getLocalMinimums(self):
        localMin = []
        for t in self.triangles:
            lowPoint = t.lowestPoint()
            isLowest = True
            for tc in t.connectedTriangles():
                if lowPoint.value > tc.lowestPoint().value:
                    isLowest = False
                    break

            if isLowest:
                localMin.append(lowPoint)

        return sorted(localMin, key=lambda p: p.value, reverse=False)

    def partition(self, triangle: Triangle):
        # Remove triangle from triangles, and from lines triangle list
        if not triangle.splited:
            if triangle in self.queue:
                raise Exception(f"Triangle emerge multiple times in queue list!")
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
        for t in triangle.coincidingTriangles(onSurface=True) + newTriangles:
            if t not in self.queue:
                NmX, NmY = t.newPointVector(onSurface=True)
                if self.pointExists(NmX, NmY):
                    self.queue.append(t)

        return mPoint, cmd
