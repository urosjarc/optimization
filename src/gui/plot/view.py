from pyrr import Vector3, Matrix44, Quaternion
import numpy as np


class View:
    def __init__(self):
        self.projectionMatrix = Matrix44.identity()
        self.modelMatrix = Matrix44.identity()
        self.viewMatrix = Matrix44.identity()
        self.light = Vector3([10, 10, 10])

        self.axisX = Vector3([1, 0, 0])
        self.axisY = Vector3([0, 1, 0])
        self.axisZ = Vector3([0, 0, 1])

    def rotateX(self, deg, local=False):
        axis = self.axisX if local else Vector3([1, 0, 0])
        self.__rotate(axis, deg)

    def rotateY(self, deg, local=False):
        axis = self.axisY if local else Vector3([0, 1, 0])
        self.__rotate(axis, deg)

    def rotateZ(self, deg, local=False):
        axis = self.axisZ if local else Vector3([0, 0, 1])
        self.__rotate(axis, deg)

    def __rotate(self, axis, deg):
        quat = Quaternion.from_axis_rotation(axis, np.deg2rad(deg))
        self.modelMatrix *= quat.matrix44()

    def translate(self, dx=0, dy=0, dz=0, local=False):
        dV = Vector3([dx, dy, dz])
        if local:
            dV = (self.axisX * dx) + (self.axisY * dy) + (self.axisZ * dz)
        mat = Matrix44.from_translation(dV)
        self.viewMatrix *= mat

