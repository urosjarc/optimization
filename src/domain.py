import turtle
from typing import List, Callable
import numpy as np
from random import random, randint
from src.math import Space
from itertools import combinations


class Layer:
    def __init__(self, size, activation: Callable[[int], int]):
        self.weights: List[List[float]] = []
        self.biases: List[List[float]] = []
        self.size = size
        self.activation = activation

    def output(self, vector):
        return self.activation(
            np.dot(self.weights, vector) + self.biases
        )


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

class Draw:
    def __init__(self, draw=True):
        self.draw = draw
        if draw:
            t = turtle.Turtle()
            self.t = t
            self.drawScale = 10
            t.speed(-1)
            turtle.bgcolor("black")
            t.pencolor("white")
    def circle(self, point: Point):
        if self.draw:
            self.t.penup()
            self.t.goto(point.x*self.drawScale, point.y*self.drawScale)
            self.t.pendown()
            self.t.circle(2)
    def triangle(self, triangle):
        if self.draw:
            for i in range(-1, len(triangle.points) - 1):
                p1 = triangle.points[i]
                p2 = triangle.points[i + 1]
                self.t.penup()
                self.t.goto(p1.x*self.drawScale, p1.y*self.drawScale)
                self.t.pendown()
                self.t.goto(p2.x*self.drawScale, p2.y*self.drawScale)

    def clear(self):
        if self.draw:
            self.t.clear()


class Triangle:
    def __init__(self, points: List[Point]):
        self.points: List[Point] = points
        draw.triangle(self)

    def meanValue(self):
        v = 0
        for p in self.points:
            v += p.value
        return v

    def size(self):
        A = self.points[0]
        B = self.points[1]
        C = self.points[2]
        return abs((A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y))/2)

class GridOptimizer:

    def __init__(self, space: Space):
        self.drawScale = 10
        self.space = space
        self.triangles: List[Triangle] = []
        self.points: List[Point] = []
        self.evaluation = 0
        self.init()

    def init(self):
        p1 = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][1])
        p2 = self.getOrMakePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][0])
        p3 = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][0])
        p4 = self.getOrMakePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][1])
        self.triangles += [
            Triangle([p1, p2, p4]),
            Triangle([p2, p3, p4])
        ]

    def getOrMakePoint(self, x, y):
        for p in self.points:
            if p.vector == [x, y]:
                return p

        p = Point(x, y, self.space(np.array([x, y])))
        draw.circle(p)
        self.points.append(p)
        return p

    def nextPoint(self):
        self.evaluation+= 1
        triangle = self.getTriangleCandidate()
        p = self.partition(triangle)
        return p.vector

    def getTriangleCandidate(self):
        print(self.evaluation)
        if self.evaluation % 3 == 0 or self.evaluation > 100:
            ts = sorted(self.triangles, key=lambda t: t.meanValue(), reverse=False)
            if self.evaluation > 200:
                return ts[0]
            ts = ts[:len(ts)//2]
            return ts[randint(0, len(ts)-1)]
        else:
            ts = sorted(self.triangles, key=lambda t: t.size(), reverse=True)
            ts = ts[0]
            return ts

    def partition(self, triangle):
        self.triangles.remove(triangle)
        points = set(triangle.points)
        lines = list(combinations(triangle.points, 2))
        lines.sort(key=lambda t: t[0].distance(t[1]), reverse=True)
        p1, p2 = lines[0]
        p3 = list(points.difference([p1, p2]))[0]
        mX = (p1.x + p2.x) / 2.0
        mY = (p1.y + p2.y) / 2.0
        mPoint = self.getOrMakePoint(mX, mY)
        self.triangles += [
            Triangle([p3, mPoint, p1]),
            Triangle([p3, mPoint, p2])
        ]
        return mPoint


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


class Act:
    ReLU = lambda x: x * (x > 0)
    sigmoid = lambda x: 1 / (1 + np.exp(-x))
    output = lambda x: x
    squash = lambda x: 1 * (x > 0)


class NeuralNet:
    def __init__(self, layers: List[Layer]):
        self.layers: List[Layer] = layers

        self.init()

    def init(self):
        for i in range(len(self.layers)):
            this = self.layers[i]
            if i == len(self.layers) - 1:
                this.weights = np.random.rand(this.size, this.size)
                this.biases = np.random.rand(this.size)
                break
            next = self.layers[i + 1]
            this.weights = np.random.rand(next.size, this.size)
            this.biases = np.random.rand(next.size)

    def train(self, optimizer: Optimizer):
        pass

    def calculate(self, vector):
        for i in range(len(self.layers)):
            vector = self.layers[i].output(vector)

        return vector

draw = Draw(False)
# from gobench import go_benchmark_functions
# space = Space(go_benchmark_functions.Ackley01)
# opt = GridOptimizer(space)
# for i in range(500):
#     opt.nextPoint()

