from typing import List

import numpy as np
from pyrr import Vector3

from src.gui.plot.view import View
from src.gui.plot.buffer_data import BufferData
from src.gui.plot.shape import Shape


class ModelInfo:
    center: List[float]
    maxWidth: float


class Model:
    def __init__(self, drawMode, dim):
        self.bdata = BufferData(drawMode, dim)
        self.view = View()
        self.shapes: List[Shape] = []

    def addShape(self, shape: Shape):
        self.shapes.append(shape)
        self.bdata.appendBuffers(
            positions=shape.positions,
            colors=shape.colors,
            normals=shape.normals,
        )

    def setShapes(self, shapes: List[Shape]):
        self.shapes = shapes

        self.bdata.resetBuffers()
        for shape in shapes:
            self.addShape(shape)


    #TODO: This method has to much dependency
    def center(self):
        vectors = []
        for shape in self.shapes:
            p = shape.positions
            vectors += np.array_split(np.array(p), len(p) / 3)

        meanV = -np.mean(vectors, axis=0)
        meanV = np.dot(meanV, self.view.scaleMatrix.matrix33.T)
        self.view.translate(*meanV.tolist())

    #TODO: This method has to much dependency
    def getInfo(self) -> ModelInfo:
        vectors = []
        centers = []
        for shape in self.shapes:
            p = shape.positions
            shapeVectors = np.array_split(np.array(p), len(p) / 3)
            shapeVectors = np.dot(shapeVectors, self.view.scaleMatrix.matrix33.T)
            shapeCenter = self.view.translationMatrix * Vector3(np.mean(shapeVectors, axis=0), dtype=np.float32)

            vectors += shapeVectors.tolist()
            centers.append(shapeCenter)

        modelInfo = ModelInfo()
        modelInfo.center = np.mean(centers, axis=0)
        modelInfo.maxWidth = max(np.linalg.norm(vectors - modelInfo.center, axis=1))

        return modelInfo
