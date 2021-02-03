from random import random, randint

from src.app import PlotInterface
from src.math import Space
from itertools import combinations
import numpy as np
from typing import *



class Point:
    def __init__(self, x, y, value):
        self.vector = [x, y]
        self.x = x
        self.y = y
        self.value = value
        self.neighbours: List[Point] = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def distance(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

class Triangle:
    def __init__(self, mainPoint: Point, points: List[Point], evalDiff=10**10, eval=0):
        self.points: List[Point] = points
        self.evalDiff: float = abs(evalDiff)
        self.mainPoint: Point = mainPoint
        self.eval = eval

    def allPoints(self):
        return [self.mainPoint] + self.points

    def meanValue(self):
        v = 0
        for p in self.allPoints():
            v += p.value
        return v

    def size(self):
        A = self.mainPoint
        B,C = self.points
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y))/2)

    def newMeanPointVector(self):
        p1, p2 = self.points
        mX = (p1.x + p2.x) / 2.0
        mY = (p1.y + p2.y) / 2.0
        mVal = (p1.value + p2.value) / 2.0
        return mX, mY, mVal

class GridOptimizer:

    def __init__(self, space: Space, draw: PlotInterface, maxEvaluations):
        self.draw = draw
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []
        self.evaluation = 0
        self.maxEvaluations = maxEvaluations
        self.init()

    def init(self):
        leftdown,_ = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][0])
        leftup,_ = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][1])
        rightdown,_ = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][0])
        rightup,_ = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][1])
        self.triangles += [
            Triangle(leftup, [leftdown, rightup]),
            Triangle(rightdown, [leftdown, rightup])
        ]
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
        self.evaluation+= 1
        while(True):
            triangle = self.getTriangleCandidate()
            p, cmd = self.partition(triangle)
            if cmd == "make":
                return p.vector

    def getTriangleCandidate(self):
        ts = self.triangles
        if self.evaluation < self.maxEvaluations/2:
            ts = sorted(ts, key=lambda t: t.evalDiff, reverse=True)
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)
        elif self.evaluation < 3*self.maxEvaluations/4:
            ts = sorted(ts, key=lambda t: t.meanValue(), reverse=False)
            ts = ts[:len(ts)//10]
            ts = sorted(ts, key=lambda t: t.evalDiff, reverse=True)
        else:
            ts = sorted(ts, key=lambda t: t.meanValue(), reverse=False)
            ts = ts[:len(ts)//10]
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)

        return ts[0]

    def partition(self, triangle: Triangle):
        self.triangles.remove(triangle)
        mX, mY, mVal = triangle.newMeanPointVector()
        mPoint, cmd = self.getOrMakePoint(mX, mY)
        evalDiff = mPoint.value - mVal
        newTriangles = [
            Triangle(mPoint, [triangle.mainPoint, triangle.points[0]], evalDiff=evalDiff, eval=triangle.eval+1),
            Triangle(mPoint, [triangle.mainPoint, triangle.points[1]], evalDiff=evalDiff, eval=triangle.eval+1)
        ]
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
