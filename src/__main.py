import gym
import numpy as np
from math import e
from random import random
from typing import List, Callable
env = gym.make('CartPole-v0')
a = env.action_space
o = env.observation_space

class Layer:
    def __init__(self, size, activation):
        self.weights = [1 for i in range(size)]
        self.size = size
        self.activation = activation

    def output(self, vector):
        return self.activation(np.dot(self.weights, vector))

class Act:
    sigmoid = lambda x: 1 / (1 + np.exp(-x))


class NeuralNet:
    def __init__(self, layers: List[Layer]):
        self.layers: List[Layer] = layers

    def init(self):
        for i in range(len(self.layers)-1):
            weights = []
            for y in range(self.layers[i+1].size):
                weights.append([])
                for x in range(self.layers[i].size):
                    weights[-1].append(random())
            self.layers[i].weights = np.array(weights)

        for l in self.layers:
            print(l.weights)
            print('===============')

    def calculate(self, vector):
        for i in range(len(self.layers)):
            vector = self.layers[i].output(vector)

        return vector







nn = NeuralNet([
    Layer(5 , Act.sigmoid),
    Layer(10, Act.sigmoid),
    Layer(1, Act.sigmoid)
])

nn.init()

print(nn.calculate(np.array([1,1,1,1,1])))
exit()
for i_episode in range(20):
    observation = env.reset()
    points = 0
    for t in range(100):
        env.render()
        action = env.action_space.sample()
        observation, reward, done, info = env.step(1)
        points += reward

        if done:
            print(f"Points: {points}")
            break
env.close()