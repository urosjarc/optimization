from typing import List

import numpy as np
from pyrr import Matrix44

from src.gui.plot.buffer_data import BufferData
from src.gui.plot.shape import Shape, BoundBox
from src.gui.plot.view import View


class Model:
    def __init__(self, drawMode, dim, initBuffers=True):
        self.bdata = BufferData(drawMode, dim)
        self.view = View()
        self.shapes: List[Shape] = []
        self.boundBox: BoundBox = BoundBox()

        self.buffersInited = initBuffers
        if initBuffers:
            self.bdata.initBuffers()

    def initBuffers(self):
        self.bdata.initBuffers()
        self.buffersInited = True

        for shape in self.shapes:
            self.bdata.appendBuffers(
                positions=shape.positions,
                colors=shape.colors,
                normals=shape.normals,
            )

    def addShape(self, shape: Shape):
        self.shapes.append(shape)
        self.boundBox.resize(boundBox=shape.boundBox)

        if self.buffersInited:
            self.bdata.appendBuffers(
                positions=shape.positions,
                colors=shape.colors,
                normals=shape.normals,
            )
        return self

    def setShapes(self, shapes: List[Shape]):

        if self.buffersInited:
            self.bdata.resetBuffers()

        self.shapes = []
        self.boundBox = BoundBox()
        for shape in shapes:
            self.addShape(shape)
        return self

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
