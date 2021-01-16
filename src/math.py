import numpy as np
from typing import Callable

class fun:
    rastrigin = lambda x, y: ((x**2 - 10 * np.cos(2 * np.pi * x)) + (y**2 - 10 * np.cos(2 * np.pi * y)) + 20)
    eggholder = lambda x, y: (-(y + 47) * np.sin(np.sqrt(abs(x / 2 + (y + 47)))) - x * np.sin(np.sqrt(abs(x - (y + 47)))))

def normalize_surface(matrix, mini=-1, height=2):
    matrix -= np.min(matrix)
    matrix /= np.max(matrix)
    matrix *= height
    matrix += mini
    return matrix

def surface(f: Callable, xmM=(-10, 10), ymM=(-10, 10), step=400):
    x = np.linspace(xmM[0], xmM[1], step)
    y = np.linspace(ymM[0], ymM[1], step)
    xx, yy = np.meshgrid(x, y, sparse=True)
    z = normalize_surface(f(xx, yy))
    return (x, y, z)


