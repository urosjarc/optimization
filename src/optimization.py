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
        self.neighbours: List[Point] = []
        self.squares: List[Square] = []

    def __str__(self):
        return f'({self.x},{self.y},{self.value})'

    def minSquare(self):
        mt = sorted(self.squares, key=lambda t: t.size(), reverse=True)
        return mt[0]

    def distance(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def connect(self, point):
        self.neighbours.append(point)
        point.neighbours.append(self)

class Square:
    def __init__(self, points: List[Point], evalDiff=10 ** 10, eval=0):
        self.points: List[Point] = points
        self.neighbours = []
        self.evalDiff: float = abs(evalDiff)
        self.eval = eval
        self.size = None

        # Connect points to a square
        for p in self.points:
            p.squares.append(self)

        # Connect points in a square mesh
        #TODO: Implement good neigbbour algorithm
        upDownPoints = sorted(points, key=lambda p: p.y, reverse=False)
        UP_rightLeftPoints = sorted(upDownPoints[:2], key=lambda p: p.x, reverse=False)
        DOWN_rightLeftPoints = sorted(upDownPoints[2:], key=lambda p: p.x, reverse=False)
        UP_rightLeftPoints[0].connect(UP_rightLeftPoints[1])
        DOWN_rightLeftPoints[0].connect(DOWN_rightLeftPoints[1])
        DOWN_rightLeftPoints[0].connect(UP_rightLeftPoints[0])
        DOWN_rightLeftPoints[1].connect(UP_rightLeftPoints[1])

    def connect(self, square):
        self.neighbours.append(square)
        square.neighbour.append(self)

    def meanValue(self):
        v = 0
        for p in self.points:
            v += p.value
        return v / len(self.points)

    def lowestPoint(self):
        return sorted(self.points, key=lambda p: p.value, reverse=False)[0]

    def center(self):
        mX = 0
        mY = 0
        mVal = 0
        ap = self.points
        size = len(self.points)
        for p in ap:
            mX += p.x
            mY += p.y
            mVal += p.value
        return mX / size, mY / size, mVal / size

    def upNormal(self):
        mainPoint = self.points[0]
        conPoints = [p for p in self.points if p in mainPoint.neighbours]
        v1 = np.array(mainPoint.vector + [mainPoint.value])
        v2 = np.array(conPoints[0].vector + [conPoints[0].value])
        v3 = np.array(conPoints[1].vector + [conPoints[1].value])
        dv1 = v2 - v1
        dv2 = v3 - v1
        normal1 = np.cross(dv1, dv2)
        if normal1[-1] < 0:
            normal1 = np.cross(dv2, dv1)
        return normal1.tolist()

    def size(self):
        return np.linalg.norm(self.upNormal())

    def meanDiff(self):
        mV = self.meanValue()
        diff = 0
        for p in self.points:
            diff += abs(p.value - mV)
        return diff

    def upNormalDiff(self):
        v1 = np.array(self.upNormal())

        sumDiff = 0
        for n in self.neighbours:
            vt = np.array(n.upNormal())
            sumDiff += np.linalg.norm(vt-v1)
        return sumDiff


class GridOptimizer:

    def __init__(self, space: Space, draw: PlotInterface, maxEvaluations):
        self.draw = draw
        self.space = space
        self.squares: List[Square] = []
        self.points: List[Point] = []
        self.minimums = []
        self.minDiff = 10 ** 10
        self.evalMean = []
        self.evaluation = 0
        self.maxEvaluations = maxEvaluations
        self.init()

    def init(self):
        leftdown = self.makePoint(self.space.bounds[0][0], self.space.bounds[1][0])
        leftup = self.makePoint(self.space.bounds[0][0], self.space.bounds[1][1])
        rightdown = self.makePoint(self.space.bounds[0][1], self.space.bounds[1][0])
        rightup = self.makePoint(self.space.bounds[0][1], self.space.bounds[1][1])
        self.squares = [
            Square([leftup, leftdown, rightup, rightdown]),
        ]
        self.drawSquares(self.squares)

    def drawSquares(self, squares: List[Square]):
        for t in squares:
            points = [p.vector for p in t.points]
            self.draw.poligon(points)

    def nextPoint(self):
        self.evaluation += 1
        while (True):
            square = self.getSquareCandidate()
            p = self.partition(square)
            return p.vector

    def getMinSquareCandidate(self):
        self.localMinimums()
        min: Point = sorted(self.minimums, key=lambda p: p.value, reverse=False)
        for m in min:
            square = m.minSquare()
            if square.evalDiff > 10 ** -6:
                print(self.squares[-1].evalDiff)
                self.draw.localMinimum([m.vector])
                return square

    def getSquareCandidate(self):
        ts: List[Square] = self.squares

        if self.evaluation < 30:
            ts = sorted(ts, key=lambda t: t.eval, reverse=False)
            return ts[0]
        elif self.evaluation % 10 == 0:
            t = self.getMinSquareCandidate()
            if t is not None:
                return t

        ts = sorted(ts, key=lambda t: t.meanValue())
        diff = (self.maxEvaluations - self.evaluation) / self.maxEvaluations
        ts = ts[:int(len(ts) * diff)]

        meanDiff = normalizeVector([t.meanDiff() for t in ts])
        meanValue = 1 - normalizeVector([t.meanValue() for t in ts])
        evalDiff = normalizeVector([t.evalDiff for t in ts])
        upNormalDiff = normalizeVector([t.upNormalDiff() for t in ts])
        size = normalizeVector([t.size() for t in ts])
        rank = upNormalDiff * 4 + evalDiff * 5 + meanDiff * 1 + size * 2 + meanValue * 2

        higestRank = np.argsort(rank)[-1]
        return ts[higestRank]

    def localMinimums(self):
        lm = 0
        self.minimums = []
        for p in self.points:
            isMin = True
            for t in p.squares:
                for tp in t.points:
                    if tp.value < p.value:
                        isMin = False
                        break
                if not isMin:
                    break
            if isMin:
                self.minimums.append(p)
                lm += 1

        return lm

    def partition(self, square: Square):

        # Get new point vector of splited triangle line, and create new point from that
        mX, mY, mVal = square.center()
        mPoint = self.makePoint(mX, mY)

        # Get eval difference of evaluation
        evalDiff = mPoint.value - mVal
        newTriangles = []
        for comb in combinations(square.allPoints(), 2):
            newTriangle = Square(mPoint, list(comb), evalDiff=evalDiff, eval=square.eval + 1)
            newTriangles.append(newTriangle)

        # Remove triangle from triangles, and points list
        self.squares.remove(square)
        for p in square.allPoints():
            p.squares.remove(square)

        # Connect neighbours
        for comb in list(combinations(newTriangles, 2)):
            comb[0].connect(comb[1])
        self.squares += newTriangles

        # Draw updates
        self.drawSquares(newTriangles)
        self.evalMean.append(np.mean([t.evalDiff for t in self.squares if t.evalDiff < 10 ** 10]))
        self.draw.errs(self.evalMean)

        return mPoint

    def makePoint(self, x, y):
        point = Point(x, y, self.space(np.array([x, y])))
        self.points.append(point)
        return point


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
