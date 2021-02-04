from random import random, randint

from src.app import PlotInterface
from src.math import Space, normalizeVector
from itertools import combinations
import numpy as np
from typing import *


class Point:
    def __init__(self, x, y, value):
        self.vector = [x, y]
        self.x = x
        self.y = y
        self.value = value
        self.triangles: List[Triangle] = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def distance(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5


class Triangle:
    def __init__(self, mainPoint: Point, points: List[Point], evalDiff=10 ** 10, eval=0):
        self.points: List[Point] = points
        self.neighbour = None
        self.evalDiff: float = abs(evalDiff)
        self.mainPoint: Point = mainPoint
        self.eval = eval

        for p in self.allPoints():
            p.triangles.append(self)

    def connect(self, triangle):
        self.neighbour = triangle
        triangle.neighbour = self

    def allPoints(self):
        return [self.mainPoint] + self.points

    def meanValue(self):
        v = 0
        for p in self.allPoints():
            v += p.value
        return v/3

    def center(self):
        mX = 0
        mY = 0
        ap = self.allPoints()
        for p in ap:
            mX += p.x
            mY += p.y
        return mX / len(ap), mY / len(ap)

    def centerDiff(self, triangle):
        c1 = self.center()
        c2 = triangle.center()
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 5

    def upNormal(self):
        v1 = np.array(self.mainPoint.vector + [self.mainPoint.value])
        v2 = np.array(self.points[0].vector + [self.points[0].value])
        v3 = np.array(self.points[1].vector + [self.points[1].value])
        dv1 = v2 - v1
        dv2 = v3 - v1
        normal1 = np.cross(dv1, dv2)
        if normal1[-1] < 0:
            normal1 = np.cross(dv2, dv1)
        return normal1.tolist()

    def meanDiff(self):
        mV = self.meanValue()
        diff = 0
        for p in self.allPoints():
            diff += abs(p.value - mV)
        return diff

    def size(self):
        A = self.mainPoint
        B, C = self.points
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y)) / 2)

    def newMeanPointVector(self):
        p1, p2 = self.points
        mX = (p1.x + p2.x) / 2.0
        mY = (p1.y + p2.y) / 2.0
        mVal = (p1.value + p2.value) / 2.0
        return mX, mY, mVal

    def upNormalDiff(self):
        v1 = np.array(self.upNormal())
        vt = np.array(self.neighbour.upNormal())
        return np.linalg.norm(vt - v1)


class GridOptimizer:

    def __init__(self, space: Space, draw: PlotInterface, maxEvaluations):
        self.draw = draw
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []
        self.minimums = []
        self.evaluation = 0
        self.maxEvaluations = maxEvaluations
        self.init()

    def init(self):
        leftdown, _ = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][0])
        leftup, _ = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][1])
        rightdown, _ = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][0])
        rightup, _ = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][1])
        self.triangles += [
            Triangle(leftup, [leftdown, rightup]),
            Triangle(rightdown, [leftdown, rightup])
        ]
        self.triangles[0].connect(self.triangles[1])
        self.drawTriangles(self.triangles)

    def drawTriangles(self, triangles: List[Triangle]):
        for t in triangles:
            points = [p.vector for p in t.allPoints()]
            self.draw.poligon(points)

    def getOrMakePoint(self, x, y):
        for p in self.points:
            if p.vector == [x, y]:
                return p, "get"

        p = Point(x, y, self.space(np.array([x, y])))
        self.points.append(p)
        return p, "make"

    def nextPoint(self):
        self.evaluation += 1
        while (True):
            triangle = self.getTriangleCandidate()
            p, cmd = self.partition(triangle)
            if cmd == "make":
                return p.vector

    def getTriangleCandidate(self):
        ts = self.triangles
        print(self.evaluation, self.localMinimums())

        if self.evaluation < 30:
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)
        else:
            meanDiff = normalizeVector([t.meanDiff() for t in ts])
            evalDiff = normalizeVector([t.evalDiff for t in ts])
            upNormalDiff = normalizeVector([t.upNormalDiff() for t in ts])
            size = normalizeVector([t.size() for t in ts])
            rank = upNormalDiff*4 + evalDiff*5 + meanDiff + size*8
            higestRank = np.argsort(rank)[-1]
            return ts[higestRank]



        return ts[0]

    def localMinimums(self):
        lm = 0
        self.minimums = []
        for p in self.points:
            isMin = True
            for t in p.triangles:
                for tp in t.allPoints():
                    if tp.value < p.value:
                        isMin = False
                        break
                if not isMin:
                    break
            if isMin:
                self.minimums.append(p.vector)
                lm+=1

        self.draw.localMinimum(self.minimums)

        return lm

    def partition(self, triangle: Triangle):

        # Get new point vector of splited triangle line, and create new point from that
        mX, mY, mVal = triangle.newMeanPointVector()
        mPoint, cmd = self.getOrMakePoint(mX, mY)

        # Get eval difference of evaluation
        evalDiff = mPoint.value - mVal
        newTriangles = [
            Triangle(mPoint, [triangle.mainPoint, triangle.points[0]], evalDiff=evalDiff, eval=triangle.eval + 1),
            Triangle(mPoint, [triangle.mainPoint, triangle.points[1]], evalDiff=evalDiff, eval=triangle.eval + 1)
        ]

        # Remove triangle from triangles, and points list
        self.triangles.remove(triangle)
        for p in triangle.allPoints():
            p.triangles.remove(triangle)

        # Connect neighbours
        newTriangles[0].connect(newTriangles[1])
        self.drawTriangles(newTriangles)
        self.triangles += newTriangles
        return mPoint, cmd


class Optimizer:
    def __init__(self, space: Space):
        self.space = space
        self.min = 10 ** 10
        self.best = [randint(b[0], b[1]) for b in self.space.f.bounds]
        self.radius = self.space.f.bounds[0][1]

    def nextPoint(self):
        self.radius *= 0.99

        while True:
            vector = np.array([best + self.radius * (random() - 0.5) * 2 for best in self.best])

            inBounds = True
            for i in range(len(vector)):
                if not (self.space.f.bounds[i][0] < vector[i] < self.space.f.bounds[i][1]):
                    inBounds = False
                    break

            if inBounds:
                break

        value = self.space(vector)
        if value < self.min:
            self.min = value
            self.best = vector
        return vector
