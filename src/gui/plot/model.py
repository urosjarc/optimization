from typing import List

import numpy as np
from pyrr import Matrix44

from src.gui.plot.buffer_data import BufferData
from src.gui.plot.shape import Shape
from src.gui.plot.view import View


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

    def center(self):
        vectors = []
        for shape in self.shapes:
            p = shape.positions
            vectors += np.array_split(np.array(p), len(p) / 3)
        meanV = -np.mean(vectors, axis=0)
        self.view.translate(*meanV.tolist())

    @property
    def modelView(self) -> Matrix44:
        return self.view.scaleMatrix * self.view.rotationMatrix * self.view.translationMatrix

    @property
    def vectors(self):
        vectors = []
        for shape in self.shapes:
            p = shape.positions
            shapeVectors = np.array_split(np.array(p), len(p) / 3)
            vectors += shapeVectors

        return np.dot(self.modelView.matrix33, np.array(vectors).T).T
