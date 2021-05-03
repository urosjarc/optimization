from pyrr import Vector3, Matrix44, Quaternion
import numpy as np


class View:
    def __init__(self):
        self.init()

    def init(self):
        self.rotation = Quaternion()
        self.rotationMatrix = Matrix44.identity(dtype=np.float32)
        self.translationMatrix = Matrix44.identity(dtype=np.float32)

        self.axisX = Vector3([1, 0, 0], dtype=np.float32)
        self.axisY = Vector3([0, 1, 0], dtype=np.float32)
        self.axisZ = Vector3([0, 0, 1], dtype=np.float32)

    def rotateX(self, deg, local=False):
        axis = self.axisX if local else Vector3([1, 0, 0], dtype=np.float32)
        self.__rotate(axis, deg)
        self.axisY = self.rotationMatrix * self.axisY
        self.axisZ = self.rotationMatrix * self.axisZ

    def rotateY(self, deg, local=False):
        axis = self.axisY if local else Vector3([0, 1, 0], dtype=np.float32)
        self.__rotate(axis, deg)
        self.axisX = self.rotationMatrix * self.axisX
        self.axisZ = self.rotationMatrix * self.axisZ

    def rotateZ(self, deg, local=False):
        axis = self.axisZ if local else Vector3([0, 0, 1], dtype=np.float32)
        self.__rotate(axis, deg)
        self.axisY = self.rotationMatrix * self.axisY
        self.axisX = self.rotationMatrix * self.axisX

    def __rotate(self, axis, deg):
        quat = Quaternion.from_axis_rotation(axis, np.deg2rad(deg), dtype=np.float32)
        self.rotation *= quat
        self.rotationMatrix = self.rotation.matrix44

    def translate(self, dx=0, dy=0, dz=0, local=False):
        dV = Vector3([dx, dy, dz], dtype=np.float32)
        if local:
            dV = self.rotation * Vector3([dx, dy, dz], dtype=np.float32)
        mat = Matrix44.from_translation(dV, dtype=np.float32)
        self.translationMatrix *= mat
