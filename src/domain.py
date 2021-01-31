import turtle
from typing import List, Callable
import numpy as np
from random import random, randint
from src.math import Space


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


    def closestNeighbours(self, num=2):
        nearest = sorted(self.neighbours, key=lambda p: self.distance(p), reverse=False)
        return nearest[:num]

    def distance(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def minNeighbourDistance(self):
        minD = np.inf
        for n in self.neighbours:
            D = self.distance(n)
            if D < minD:
                minD = D
        return minD

    def connect(self, point, draw=True):
        print('Connect', self, point)
        if draw:
            t.penup()
            t.goto(self.x*10, self.y*10)
            t.pendown()
            t.goto(point.x*10, point.y*10)
        self.neighbours.append(point)
        point.neighbours.append(self)


class GridOptimizer:

    def __init__(self, space: Space):
        self.space = space
        self.points: List[Point] = []
        self.pointNum = 0
        self.init()

    def makePoint(self, x, y, add=True):
        t.penup()
        t.goto(x*10, y*10)
        t.pendown()
        t.circle(2)
        p = Point(x, y, self.space(np.array([x, y])))
        print('MAKE', p)
        if add:
            self.points.append(p)
        return p

    def makeMeanPoint(self, points: List[Point], add):
        x = 0.0
        y = 0.0
        for p in points:
            x += p.x
            y += p.y
        c = len(points)
        point = self.makePoint(x / c, y / c, add)
        return point

    def init(self):
        self.makePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][0]),
        self.makePoint(self.space.f.bounds[0][0], self.space.f.bounds[1][1]),
        self.makePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][0]),
        self.makePoint(self.space.f.bounds[0][1], self.space.f.bounds[1][1]),
        t.speed(-1)
        for i in range(len(self.points)):
            for j in range(i + 1, len(self.points)):
                self.points[i].connect(self.points[j],draw=False)
        t.speed(2)

    def minPoint(self):
        minPointsCandidates = [p for p in self.points]
        mp = minPointsCandidates[0]

        for p in minPointsCandidates:
            if p.value < mp.value:
                mp = p

        return mp

    def addMeanPoints(self, point: Point):
        print("MIN", point, len(point.neighbours))
        n1, n2 = point.closestNeighbours()
        mean = self.makeMeanPoint([point, n1, n2], False)
        p1, p2, p3 = self.closestPoints(mean)
        mean.connect(p1)
        mean.connect(p2)
        mean.connect(p3)
        self.points.append(mean)

    def closestPoints(self, point):
        nearest = sorted(self.points, key=lambda p: ((point.x-p.x)**2 + (point.y-p.y)**2)**0.5, reverse=False)
        return nearest[:3]

    def nextPoint(self):
        print(self.pointNum, len(self.points))
        if self.pointNum == len(self.points):
            minPoint = self.minPoint()
            self.addMeanPoints(minPoint)

        nextPoint = self.points[self.pointNum]
        self.pointNum += 1

        return nextPoint.vector


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


t = turtle.Turtle()
t.speed(-1)
turtle.bgcolor("black")
t.pencolor("white")
from gobench import go_benchmark_functions
space = Space(go_benchmark_functions.Ackley01)
opt = GridOptimizer(space)
for i in range(500):
    opt.nextPoint()
#