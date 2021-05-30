from typing import Dict, List

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QOpenGLWidget
from pyrr import Matrix44, Vector3

from src import utils
from src.gui.plot import Model, View


class OpenGLWidget(QOpenGLWidget):

    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent=parent)

        self.programLocations: Dict[str, GLuint]

        self.light = np.array([10, 10, 10], dtype=np.float32)
        self.birdsEye = False
        self.scaleRate = 0
        self.view = View()
        self.models: List[Model] = []

        self.screenView = None
        self.mouse: List[int] = None
        self.setMouseTracking(True)

    def initializeGL(self):
        # Activate program and use it
        with open(utils.getPath(__file__, 'glsl/shader_vertex.glsl')) as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)
        with open(utils.getPath(__file__, 'glsl/shader_fragments.glsl')) as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        # Use compiled shader program
        program = shaders.compileProgram(vs, fs)
        glUseProgram(program)

        # Get program atributes locations
        self.location = {
            'in_position': glGetAttribLocation(program, 'in_position'),
            'in_color': glGetAttribLocation(program, 'in_color'),
            'in_normal': glGetAttribLocation(program, 'in_normal'),

            'in_light': glGetUniformLocation(program, 'in_light'),
            'in_scaleHeight': glGetUniformLocation(program, 'in_scaleHeight'),
            'in_scaleRate': glGetUniformLocation(program, 'in_scaleRate'),
            'in_diffuse': glGetUniformLocation(program, 'in_diffuse'),
            'modelView': glGetUniformLocation(program, 'modelView'),
            'cameraView': glGetUniformLocation(program, 'cameraView'),
            'normalView': glGetUniformLocation(program, 'normalView'),
            'screenView': glGetUniformLocation(program, 'screenView'),
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.location['in_position'])
        glEnableVertexAttribArray(self.location['in_color'])
        glEnableVertexAttribArray(self.location['in_normal'])

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(0.1, 0.1, 0.1, 1)
        glClearDepth(1.0)

        # Update widget
        self.update(context=False, cameraView=True, screenView=True)

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set GLSL constants
        glUniform3fv(self.location['in_light'], 1, self.light)
        glUniformMatrix4fv(self.location['cameraView'], 1, GL_FALSE, self.cameraView)
        glUniformMatrix4fv(self.location['screenView'], 1, GL_FALSE, self.screenView)

        for model in self.models:

            if model.bdata.drawMode == GL_TRIANGLES:
                glUniform1f(self.location['in_scaleRate'], np.float32(self.scaleRate))
                glUniform1f(self.location['in_diffuse'], np.uint(0))
            else:
                glUniform1f(self.location['in_scaleRate'], np.float32(0))
                glUniform1f(self.location['in_diffuse'], np.uint(1))

            bd = model.bdata

            # Compute views
            cameraModelView = self.cameraView * model.modelView
            normalView = cameraModelView.inverse.transpose()

            # Set views
            glUniformMatrix4fv(self.location['modelView'], 1, GL_FALSE, model.modelView)
            glUniformMatrix4fv(self.location['normalView'], 1, GL_FALSE, normalView)

            # Explain data form stored in model data buffers
            glBindBuffer(GL_ARRAY_BUFFER, bd.positionBuffer)
            glVertexAttribPointer(self.location['in_position'], bd.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
            glBindBuffer(GL_ARRAY_BUFFER, bd.colorBuffer)
            glVertexAttribPointer(self.location['in_color'], bd.colorDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
            glBindBuffer(GL_ARRAY_BUFFER, bd.normalBuffer)
            glVertexAttribPointer(self.location['in_normal'], bd.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))

            # Draw number of elements binded in buffer arrays
            glDrawArrays(bd.drawMode, 0, bd.numVectors)

    def resizeGL(self, width, height):
        if width + height == 0:
            return

        glViewport(0, 0, width, height)

    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()

        if btns != Qt.NoButton and self.mouse is not None:
            dx = self.mouse[0] - event.x()
            dy = self.mouse[1] - event.y()
            dist = self.view.translationMatrix.m43
            transScale = 8.9*10e-5*abs(dist)

            if self.birdsEye:
                if btns == Qt.LeftButton:
                    self.view.translate(dx=-dx*transScale, dy=dy*transScale)
                    self.update()
            else:
                if btns == Qt.LeftButton:
                    self.view.rotateX(dy / 2)
                    self.view.rotateZ(dx / 2, local=True)
                    self.update()
                elif btns == Qt.RightButton:
                    self.view.translate(dx=-dx * transScale, dy=dy * transScale)
                    self.update()

            if btns == Qt.MidButton:
                self.birdsEye = not self.birdsEye
                self.update(screenView=True, cameraView=True)

        self.mouse = [event.x(), event.y()]

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.update(cameraView=True, screenView=True)

    def wheelEvent(self, event: QWheelEvent):
        btns = event.buttons()

        if btns == Qt.MidButton:
            self.birdsEye = not self.birdsEye
            self.update(screenView=True)
        elif btns == Qt.NoButton:

            dist = abs(self.view.translationMatrix.m43)
            zoomScale = 5*10e-5*dist
            dz = event.angleDelta().y() * zoomScale
            self.view.translate(dz=dz)

            self.update(screenView=True)

    @property
    def cameraView(self):
        if self.birdsEye:
            return self.view.translationMatrix * self.view.scaleMatrix
        return self.view.translationMatrix * self.view.rotationMatrix * self.view.scaleMatrix

    def update(self, screenView=False, cameraView=False, context=True) -> None:

        if cameraView:
            if not self.birdsEye:
                self.view.init()
                self.view.rotateX(60)
                self.view.rotateZ(20, local=True)
            self.view.place(z=-2.5)

        if screenView:
            if self.birdsEye:
                dist = abs(self.view.translationMatrix.m43) / 5
                self.screenView = Matrix44.orthogonal_projection(-dist, dist, -dist, dist, 0.001, 100.0)
            else:
                aspect = self.width() / self.height()
                self.screenView = Matrix44.perspective_projection(45, aspect, 0.001, 100.0)

        if context:
            super(OpenGLWidget, self).update()
