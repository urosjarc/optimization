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

class Optimizer:
    def __init__(self, space: Space):
        self.space = space
        self.min = 10**10
        self.best = [ randint(b[0], b[1]) for b in self.space.f.bounds]
        self.radius = self.space.f.bounds[0][1]

    def nextPoint(self):
        self.radius*=0.99

        while True:
            vector = np.array([ best+self.radius*(random()-0.5)*2 for best in self.best ])

            inBounds = True
            for i in range(len(vector)):
                if not(self.space.f.bounds[i][0] < vector[i] < self.space.f.bounds[i][1]):
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
            if i == len(self.layers)-1:
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
