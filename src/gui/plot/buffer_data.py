import numpy as np
from OpenGL.GL import *


class BufferData:
    maxNumVectors = 10 ** 6

    def __init__(self, drawModel, dim):
        self.drawMode = drawModel

        self.positionDim = dim
        self.colorDim = 4

        self.normalBuffer = None
        self.positionBuffer = None
        self.colorBuffer = None

        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0
        self.norOffset = 0

    def initBuffers(self):
        self.positionBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.positionDim * self.maxNumVectors, dtype=np.float32),
                     GL_DYNAMIC_DRAW)

        self.colorBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.colorDim * self.maxNumVectors, dtype=np.float32), GL_DYNAMIC_DRAW)

        self.normalBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.normalBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.positionDim * self.maxNumVectors, dtype=np.float32),
                     GL_DYNAMIC_DRAW)

    def __del__(self):
        try:
            glDeleteBuffers(3, [
                self.normalBuffer,
                self.positionBuffer,
                self.colorBuffer,
            ])
        except Exception:
            pass

    def appendBuffers(self, positions, colors, normals):
        positions = np.array(positions, dtype=np.float32)
        colors = np.array(colors, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)

        posNum = positions.size // self.positionDim
        colNum = colors.size // self.colorDim
        norNum = normals.size // self.positionDim

        if posNum != colNum != norNum:
            raise Exception(f"Length of positions | colors | normals array doesn't match: {posNum} != {colNum}")

        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.posOffset, positions)

        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.colOffset, colors)

        glBindBuffer(GL_ARRAY_BUFFER, self.normalBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.norOffset, normals)

        self.numVectors += posNum
        self.posOffset += positions.nbytes
        self.colOffset += colors.nbytes
        self.norOffset += normals.nbytes

        if self.numVectors > self.maxNumVectors:
            raise Exception("Buffers memory overflown!")

    def resetBuffers(self):
        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0
        self.norOffset = 0
