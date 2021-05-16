from typing import Dict, List

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QOpenGLWidget
from pyrr import Matrix44

from src import utils
from src.gui.plot import Model, View


class OpenGLWidget(QOpenGLWidget):

    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent=parent)

        self.programLocations: Dict[str, GLuint]
        self.light = np.array([10, 10, 10], dtype=np.float32)

        self.view = View()
        self.models: List[Model] = []
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
            'positionView': glGetUniformLocation(program, 'positionView'),
            'normalView': glGetUniformLocation(program, 'normalView'),
            'projectionView': glGetUniformLocation(program, 'projectionView'),
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.location['in_position'])
        glEnableVertexAttribArray(self.location['in_color'])
        glEnableVertexAttribArray(self.location['in_normal'])

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

    @property
    def worldView(self):
        return self.view.translationMatrix * self.view.rotationMatrix * self.view.scaleMatrix

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set view matrixes
        glUniform3fv(self.location['in_light'], 1, self.light)

        for model in self.models:
            bd = model.bdata

            # Compute views
            positionView = self.worldView * model.modelView
            normalView = positionView.inverse.transpose()

            # Set views
            glUniformMatrix4fv(self.location['positionView'], 1, GL_FALSE, positionView)
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

        # Update size of viewport
        glViewport(0, 0, width, height)

        # Update projection matrix
        projectionView = Matrix44.perspective_projection(45, width / height, 0.1, 100.0)
        glUniformMatrix4fv(self.location['projectionView'], 1, GL_FALSE, projectionView)

    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()

        if btns != Qt.NoButton and self.mouse is not None:
            dx = self.mouse[0] - event.x()
            dy = self.mouse[1] - event.y()

            if btns == Qt.LeftButton:
                self.view.rotateX(dy / 2)
                self.view.rotateZ(dx / 2, local=True)
                self.update()
            elif btns == Qt.RightButton:
                self.view.translate(dx=-dx / 500, dy=dy / 500)
                self.update()
            elif btns == Qt.MidButton:
                self.light[0] -= dx / 20
                self.light[1] += dy / 20
                self.update()

        self.mouse = [event.x(), event.y()]

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.fitToScreen()
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        btns = event.buttons()

        if btns == Qt.MidButton:
            self.resetView()
        elif btns == Qt.NoButton:
            dz = event.angleDelta().y() / 100
            self.view.translate(dz=dz)
            self.update()

    def fitToScreen(self):
        self.view.init()
        self.view.translate(dy=-0.3, dz=-3)
        self.view.rotateX(45)
        self.view.rotateZ(60, local=True)
