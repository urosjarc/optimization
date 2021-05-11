from typing import List

import numpy as np

from src.gui.plot.view import View
from src.gui.plot.buffer_data import BufferData
from src.gui.plot.shape import Shape


class Model:
    def __init__(self):
        self.bdata = BufferData()
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
            vectors += np.array_split(np.array(p), len(p)/3)

        meanV = -np.mean(vectors, axis=0)
        self.view.translate(*meanV.tolist())
