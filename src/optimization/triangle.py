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
        self.lines = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def distance(self, point):
        return np.linalg.norm(self.vector3D-point.vector3D)

class Line:
    def __init__(self, p1: Point, p2: Point):
        self.points = [p1, p2]
        self.triangles: List[Triangle] = []
        self.childrens = []

        for p in self.points:
            p.lines.append(self)

    def size(self):
        return self.points[0].distance(self.points[1])

    def center(self):
        return np.mean([p.vector3D for p in self.points], axis=0).tolist()

    def mutualPoint(self, line):
        p1 = set(self.points)
        p2 = set(line.points)
        return list(p1.intersection(p2))[0]

class Triangle:
    def __init__(self, lines, evalDiff=10 ** 10, eval=0):
        self.splited = True
        self.lines: List[Line] = lines
        self.evalDiff: float = abs(evalDiff)
        self.eval = eval
        self.points: List[Point] = []

        for l in self.lines:
            l.triangles.append(self)

        pts = set()
        for l in self.lines:
            for p in l.points:
                pts.add(p)
        self.points += list(pts)

    def meanValue(self):
        vals = [p.value for p in self.points]
        return sum(vals)/3

    def meanValueDiff(self):
        mV = self.meanValue()
        diff = 0
        for p in self.points:
            diff += abs(p.value - mV)
        return diff

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
        return normal1

    def fractureRatio(self):
        pass
        # TODO: Get all connected triangles and calculate fracture on lines

        # v1 = self.normalVector()
        # degs = []
        # for p in self.points:
        #     for t in p.triangles:
        #         vt = t.normalVector()
        #         degs.append(angle(v1, vt))
        # return np.median(degs) / math.pi

    def volume(self):
        A, B, C = self.points
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y)) / 2)

    def sortedLines(self, fromBigToLow=True):
        return sorted(self.lines, key=lambda l: l.size(), reverse=fromBigToLow)


class TriangleOptimizer:

    def getOrMakePoint(self, x, y):
        for p in self.points:
            if p.vector == [x, y]:
                return p, "get"

        p = Point(x, y, self.space([x, y]))
        self.points.append(p)
        return p, "make"

    def drawTriangles(self, triangles: List[Triangle]):
        for t in triangles:
            points = [p.vector for p in t.points]
            self.draw.poligon(points)


    def __init__(self, space: Space, draw: PlotInterface, maxEval):
        self.draw = draw
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []

        self.eval = 0
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
        self.drawTriangles(self.triangles)

    def nextPoint(self):
        self.eval += 1
        while (True):
            triangle = self.getTriangleCandidate()
            p, cmd = self.partition(triangle)
            if cmd == "make":
                return p.vector

    def getMinTriangleCandidate(self):
        minPoints = self.getLocalMinimums()
        min: Point = sorted(minPoints, key=lambda p: p.value, reverse=False)
        for m in min:
            triangle = m.minTriangle()
            if triangle.evalDiff > 10**-4:
                print(self.triangles[-1].evalDiff)
                self.draw.localMinimum([m.vector])
                return triangle

    def getTriangleCandidate(self):
        ts = self.triangles

        if self.eval < 30:
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)
            return ts[0]
        # elif self.eval % 10 == 0:
        #     t = self.getMinTriangleCandidate()
        #     if t is not None:
        #         return t

        # ts = sorted(ts, key=lambda t: t.meanValue())
        # diff = (self.maxEval - self.eval) / self.maxEval
        # ts = ts[:int(len(ts)*diff)]

        meanDiff = normalizeVector([t.meanValueDiff() for t in ts])
        meanValue = 1-normalizeVector([t.meanValue() for t in ts])
        evalDiff = normalizeVector([t.evalDiff for t in ts])
        # upNormalDiff = normalizeVector([t.fractureRatio() for t in ts])
        size = normalizeVector([t.volume() for t in ts])
        rank = evalDiff*5 + size + meanValue + meanDiff

        higestRank = np.argsort(rank)[-1]
        return ts[higestRank]

    def getLocalMinimums(self):
        pass
        """
        Za tocko poglej vse trikotnike s katerimi je povezana.
        Za ta trikotnik poglej vse njegove tocke.
        Za tocko poglej ce je vrednost tocke poglej ce je vrednost vecja.
        Ce je tocka ni minimum
        """

    def partition(self, triangle: Triangle):

        # Get new point vector of splited triangle line, and create new point from that
        line0, line1, line2 = triangle.sortedLines(fromBigToLow=True)
        mX, mY, mVal = line0.center()
        mPoint, cmd = self.getOrMakePoint(mX, mY)
        evalDiff = mPoint.value - mVal

        # Remove triangle from triangles, and points list
        self.triangles.remove(triangle)
        triangle.splited = True

        # Get other 3 points
        highPoint = line1.mutualPoint(line2)
        bottomPoint1 = line0.mutualPoint(line2)
        bottomPoint2 = line0.mutualPoint(line1)

        newLines = [
            Line(mPoint, bottomPoint1),
            Line(bottomPoint1, highPoint),
            Line(highPoint, mPoint),
            Line(mPoint, bottomPoint2),
            Line(bottomPoint2, highPoint),
        ]
        line0.childrens += [newLines[0],newLines[-1]]

        newTriangles = [
            Triangle(newLines[:3], evalDiff=evalDiff, eval=triangle.eval + 1),
            Triangle(newLines[2:], evalDiff=evalDiff, eval=triangle.eval + 1)
        ]

        self.triangles += newTriangles

        # Draw updates
        self.drawTriangles(newTriangles)

        return mPoint, cmd

