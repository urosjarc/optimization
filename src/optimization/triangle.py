import math
from itertools import combinations

import matplotlib.pyplot as plt

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

    def distance(self, point):
        return np.linalg.norm(self.vector3D - point.vector3D)


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.points = [p1, p2]
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

    def isOnLine(self, point: Point):
        dist = self.points[0].distance(point)
        dist += self.points[1].distance(point)
        return abs(dist - self.size()) < 10 ** -5

    def coinciding(self, line):
        p1, p2 = line.points
        sp1, sp2 = self.points
        return (self.isOnLine(p1) and self.isOnLine(p2)) or (line.isOnLine(sp1) and line.isOnLine(sp2))


class Triangle:
    def __init__(self, lines, evalDiff=10 ** 10, eval=0):
        self.lines: List[Line] = lines
        self.evalDiff: float = abs(evalDiff)
        self.splited = False
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

    def meanValue(self):
        vals = [p.value for p in self.points]
        return sum(vals) / 3

    def meanValueDiff(self):
        mV = self.meanValue()
        return sum([abs(mV - p.value) for p in self.points])

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
        return normal1/2

    def fractureRatio(self):
        pass
        """
        For every line in triangle check every connected triangle.
        For every
        """

    def volume(self):
        A, B, C = self.points
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y)) / 2)

    def sortedLines(self, fromBigToLow=True):
        return sorted(self.lines, key=lambda l: l.size(), reverse=fromBigToLow)

    def connectedTriangles(self):
        tri = []
        for p in self.points:
            for t in p.triangles:
                if not t.splited and t != self and t not in tri:
                    isConn = False
                    for sline in self.lines:
                        for line in t.lines:
                            if sline.coinciding(line):
                                isConn = True
                                break
                        if isConn:
                            break
                    if isConn:
                        tri.append(t)

        return tri


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
            self.draw.poligon([p.vector for p in t.points])

    def drawConnectedTriangles(self, triangle: Triangle):
        print("DRAW: ", self.eval)
        self.draw.poligon([p.vector for p in triangle.points], permament=False)
        plt.waitforbuttonpress()
        cTri = triangle.connectedTriangles()
        for t in cTri:
            self.draw.poligon([p.vector for p in t.points], permament=False)
            plt.waitforbuttonpress()
        self.draw.poligon([[0, 0]], permament=False)
        plt.waitforbuttonpress()

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
        while True:
            triangle = self.getTriangleCandidate()
            p, cmd = self.partition(triangle)
            if cmd == "make":
                return p.vector

    def getMinTriangleCandidate(self):
        minTri = sorted(self.triangles, key=lambda t: t.volume(), reverse=True)[0]
        self.drawConnectedTriangles(minTri)
        return minTri

    def getTriangleCandidate(self):
        ts = self.triangles

        if self.eval < 10:
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)
            return ts[0]
        # elif self.eval % 10 == 0:
        t = self.getMinTriangleCandidate()
        if t is not None:
            return t

        # ts = sorted(ts, key=lambda t: t.meanValue())
        # diff = (self.maxEval - self.eval) / self.maxEval
        # ts = ts[:int(len(ts)*diff)]

        meanDiff = normalizeVector([t.meanValueDiff() for t in ts])
        meanValue = 1 - normalizeVector([t.meanValue() for t in ts])
        evalDiff = normalizeVector([t.evalDiff for t in ts])
        # upNormalDiff = normalizeVector([t.fractureRatio() for t in ts])
        volume = normalizeVector([t.volume() for t in ts])
        rank = evalDiff * 5 + volume + meanValue + meanDiff

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

        # Remove triangle from triangles, and from lines triangle list
        self.triangles.remove(triangle)
        triangle.splited = True

        # Get other 3 points
        highPoint = line1.mutualPoint(line2)
        bottomPoint1 = line0.mutualPoint(line1)
        bottomPoint2 = line0.mutualPoint(line2)

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

        self.triangles += newTriangles

        # Draw updates
        self.drawTriangles(self.triangles)

        return mPoint, cmd
