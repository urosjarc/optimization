from typing import List

from src.math.linalg import *
from src.math.space import Function
from OpenGL.GL import *


class Surface:
    def __init__(self, step, zoom):
        self.function = None
        self.name = None
        self.step = step
        self.zoom = zoom

        self.x = None
        self.y = None
        self.z = None
        self.zLog = None

        self.xZoom = None
        self.yZoom = None
        self.zZoom = None
        self.zZoomLog = None

        self.xMin = None
        self.yMin = None
        self.zMin = None
        self.zMinLog = None

        self.bounds = None
        self.zoomBounds = None

    def logZ(self, array):
        return np.log2(array - self.function.minValue + 1)

    def init(self, function: Function):
        self.function = function
        self.bounds = function.bounds
        self.name = function.name

        axes = [np.linspace(bound[0], bound[1], self.step).tolist() for bound in function.bounds]
        self.x, self.y = axes[0], axes[1]
        self.z = [[function(np.array([xi, yi])) for xi in self.x] for yi in self.y]
        self.zLog = self.logZ(self.z)

        XminDiff = abs(-function.bounds[0][0] + function.bounds[0][1]) / self.zoom
        YminDiff = abs(-function.bounds[1][0] + function.bounds[1][1]) / self.zoom
        self.zoomBounds = [
            [function.minVector[0][0] - XminDiff, function.minVector[0][0] + XminDiff],
            [function.minVector[0][1] - YminDiff, function.minVector[0][1] + YminDiff]
        ]
        Xaxe = np.linspace(*self.zoomBounds[0], self.step).tolist()
        Yaxe = np.linspace(*self.zoomBounds[1], self.step).tolist()
        self.xZoom, self.yZoom = Xaxe, Yaxe
        self.zZoom = [[function(np.array([xi, yi])) for xi in self.xZoom] for yi in self.yZoom]
        self.zZoomLog = self.logZ(self.zZoom)

        self.xMin = [o[0] for o in function.minVector]
        self.yMin = [o[1] for o in function.minVector]
        self.zMin = [function.minValue for _ in function.minVector]
        self.zMinLog = self.logZ(self.zMin)


class Scene:

    colorDim = 4
    positionDim = 2

    def __init__(self, maxNumVertexes=10**5):

        self.positionData = None
        self.colorData = None

        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0

        self.positionBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.positionDim * maxNumVertexes, dtype=np.float32), GL_STATIC_DRAW)

        self.colorBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.colorDim * maxNumVertexes, dtype=np.float32), GL_STATIC_DRAW)

    def setBuffers(self, position: List[float], color: List[float]):

        position = np.array(position, dtype=np.float32)
        color = np.array(color, dtype=np.float32)

        posNum = position.size//self.positionDim
        colNum = color.size//self.colorDim

        if posNum != colNum:
            raise Exception(f"Length of position and color array doesn't match: {posNum} != {colNum}")

        self.numVectors = posNum
        self.posOffset = position.nbytes
        self.colOffset = color.nbytes

        self.positionData = position
        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferData(GL_ARRAY_BUFFER, self.positionData.nbytes, self.positionData, GL_STATIC_DRAW)

        self.colorData = color
        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferData(GL_ARRAY_BUFFER, self.colorData.nbytes, self.colorData, GL_STATIC_DRAW)
