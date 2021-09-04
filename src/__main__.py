from PyQt5.QtCore import QThreadPool

from src.gui import app
import sys

from src.optimization.kdtree import KDTreeOptimizer
from src.optimization.space import functions


def startGUI():
    pool = QThreadPool.globalInstance()
    pool.setMaxThreadCount(pool.maxThreadCount())
    app.start(sys.argv)

def startTUI():
    funcs = functions()
    fun = funcs[10]
    opt = KDTreeOptimizer(fun, fun.bounds, maxGeneration=10, maxIterations=30000)

    print(fun)
    minVector = None
    minIter = None
    while fun.evaluation < opt.maxIterations:
        vector = opt.nextPoint()
        if minVector is None or minVector[-1] > vector[-1]:
            minVector= vector
            minIter = fun.evaluation


        dist = [round(ele-fun.minVectors[0][i],1) for i, ele in enumerate(minVector[:-1])]
        absDist = round(sum([ele**2 for ele in dist])**0.5, 1)
        print(f"\rProgress: {round(fun.evaluation/opt.maxIterations*100, 0)}%, Error: {absDist} {dist} ", end="")

    print(f"\nGLOO VECTOR: {fun.minVectors} {fun.minValue}")
    print(f"\nBEST VECTOR[{minIter}]: {minVector[:-1]} {minVector[-1]}")

if __name__ == '__main__':
    startTUI()
    # startGUI()
