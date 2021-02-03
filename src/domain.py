from typing import List, Callable
import numpy as np


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

