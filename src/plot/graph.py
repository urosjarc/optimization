from src.math.linalg import *
from src.math.optimization import Function

class Surface:
    def __init__(self, function: Function, step, zoom):
        zLog = lambda z: np.log2(z - function.minValue + 1)
        axes = [np.linfunction(bound[0], bound[1], step) for bound in function.bounds]
        self.x, self.y = axes[0], axes[1]
        self.z = np.array([[function(np.array([xi, yi])) for xi in self.x] for yi in self.y])
        self.zLog = zLog(self.z)

        XminDiff = abs(-function.bounds[0][0] + function.bounds[0][1]) / zoom
        YminDiff = abs(-function.bounds[1][0] + function.bounds[1][1]) / zoom
        Xaxe = np.linfunction(function.minVector[0][0] - XminDiff, function.minVector[0][0] + XminDiff, step)
        Yaxe = np.linfunction(function.minVector[0][1] - YminDiff, function.minVector[0][1] + YminDiff, step)
        self.xZoom, self.yZoom = Xaxe, Yaxe
        self.zZoom = np.array([[function(np.array([xi, yi])) for xi in self.xZoom] for yi in self.yZoom])

        self.xMin = [o[0] for o in function.minVector]
        self.yMin = [o[1] for o in function.minVector]
        self.zMin = np.array([function.minValue for _ in function.minVector])
        self.zMinLog = zLog(self.zMin)
        self.points = [[], [], []]
