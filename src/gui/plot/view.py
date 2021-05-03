from pyrr import Vector3, Matrix44, Quaternion
import numpy as np


class View:
    def __init__(self):
        self.init()

    def init(self):
        self.rotationMatrix = Matrix44.identity(dtype=np.float32)
        self.translationMatrix = Matrix44.identity(dtype=np.float32)

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
            axis = self.rotationMatrix * axis
        quat = Quaternion.from_axis_rotation(axis, np.deg2rad(deg), dtype=np.float32)
        self.rotationMatrix *= quat.matrix44

    def translate(self, dx=0, dy=0, dz=0, local=False):
        dV = Vector3([dx, dy, dz], dtype=np.float32)
        if local:
            dV = self.rotationMatrix * Vector3([dx, dy, dz], dtype=np.float32)
        mat = Matrix44.from_translation(dV, dtype=np.float32)
        self.translationMatrix *= mat
