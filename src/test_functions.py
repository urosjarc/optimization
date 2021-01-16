import numpy as np

def rastrigin(x, y):
    return 0.1* ((x**2 - 10 * np.cos(2 * np.pi * x)) + \
    (y**2 - 10 * np.cos(2 * np.pi * y)) + 20)

def eggholder(x, y):
    return 0.1* (-(y + 47) * np.sin(np.sqrt(abs(x / 2 + (y + 47))))
            - x * np.sin(np.sqrt(abs(x - (y + 47)))))
