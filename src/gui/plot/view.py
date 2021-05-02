from pyrr import Vector3, Matrix44, Quaternion
import numpy as np


class View:
    def __init__(self):
        self.init()

    def rotateX(self, deg, local=False):
        axis = self.axisX if local else Vector3([1, 0, 0], dtype=np.float32)
        self.__rotate(axis, deg)

    def rotateY(self, deg, local=False):
        axis = self.axisY if local else Vector3([0, 1, 0], dtype=np.float32)
        self.__rotate(axis, deg)

    def rotateZ(self, deg, local=False):
        axis = self.axisZ if local else Vector3([0, 0, 1], dtype=np.float32)
        self.__rotate(axis, deg)

    def __rotate(self, axis, deg):
        quat = Quaternion.from_axis_rotation(axis, np.deg2rad(deg), dtype=np.float32)
        self.modelMatrix *= quat.matrix44

    def translate(self, dx=0, dy=0, dz=0, local=False):
        dV = Vector3([dx, dy, dz], dtype=np.float32)
        if local:
            dV = (self.axisX * dx) + (self.axisY * dy) + (self.axisZ * dz)
        mat = Matrix44.from_translation(dV, dtype=np.float32)
        self.viewMatrix *= mat

    def init(self):
        self.projectionMatrix = Matrix44.identity(dtype=np.float32)
        self.modelMatrix = Matrix44.identity(dtype=np.float32)
        self.viewMatrix = Matrix44.identity(dtype=np.float32)
        self.axisX = Vector3([1, 0, 0], dtype=np.float32)
        self.axisY = Vector3([0, 1, 0], dtype=np.float32)
        self.axisZ = Vector3([0, 0, 1], dtype=np.float32)
