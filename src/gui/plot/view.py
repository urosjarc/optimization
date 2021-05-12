from pyrr import Vector3, Matrix44, Quaternion
import numpy as np


class View:
    def __init__(self):
        self.init()

    @property
    def rotationMatrix(self):
        return self.orientation.matrix44

    def init(self):
        self.orientation = Quaternion()
        self.translationMatrix = Matrix44.identity(dtype=np.float32)
        self.scaleMatrix = Matrix44.identity(dtype=np.float32)

    def scale(self, x=1, y=1, z=1):
        self.scaleMatrix = Matrix44.from_scale([x, y, z], dtype=np.float32)

    def rotateX(self, deg, local=False):
        axis = Vector3([1, 0, 0], dtype=np.float32)
        self.__rotate(axis, deg, local)

    def rotateY(self, deg, local=False):
        axis = Vector3([0, 1, 0], dtype=np.float32)
        self.__rotate(axis, deg, local)

    def rotateZ(self, deg, local=False):
        axis = Vector3([0, 0, 1], dtype=np.float32)
        self.__rotate(axis, deg, local)

    def __rotate(self, axis, deg, local):
        if local:
            row = axis.tolist().index(1)
            localBasis = self.orientation.matrix33[row, :]
            rot = Quaternion.from_axis_rotation(localBasis, np.deg2rad(deg), dtype=np.float32)
        else:
            rot = Quaternion.from_axis_rotation(axis, np.deg2rad(deg), dtype=np.float32)
        self.orientation *= rot

    def translate(self, dx=0, dy=0, dz=0, local=False):
        dV = Vector3([dx, dy, dz], dtype=np.float32)
        if local:
            dV = self.orientation * Vector3([dx, dy, dz], dtype=np.float32)
        mat = Matrix44.from_translation(dV, dtype=np.float32)
        self.translationMatrix *= mat
