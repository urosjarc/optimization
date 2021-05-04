from typing import Dict, List
import numpy as np

from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtOpenGL import QGLWidget
from pyrr import Matrix44, Vector3

from src import utils
from src.gui.plot import Model, View, Shape


class GLWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

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
            'projectionMatrix': glGetUniformLocation(program, 'projectionMatrix'),
            'worldTranslationMatrix': glGetUniformLocation(program, 'worldTranslationMatrix'),
            'worldRotationMatrix': glGetUniformLocation(program, 'worldRotationMatrix'),
            'modelTranslationMatrix': glGetUniformLocation(program, 'modelTranslationMatrix'),
            'modelRotationMatrix': glGetUniformLocation(program, 'modelRotationMatrix'),
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.location['in_position'])
        glEnableVertexAttribArray(self.location['in_color'])
        glEnableVertexAttribArray(self.location['in_normal'])

        # Setup world matrixes and light.
        # Projection matrix is updated on resize event only.
        # Model matrixes is updated before rendering object.
        self.__updateWorldTranslationMatrix()
        self.__updateWorldRotationMatrix()
        self.__updateLight()

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

        # Add shapes to scene
        model = Model()
        model.addShape(Shape.Dragon([1,1,1,1]))
        model.center()
        model.view.rotateX(-90)
        #Todo fix centering and rotation
        self.models.append(model)

        # Fit to screen
        self.fitToScreen()

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for model in self.models:
            bd = model.bdata

            # Set model matrixes
            glUniformMatrix4fv(self.location['modelTranslationMatrix'], 1, GL_FALSE, model.view.translationMatrix)
            glUniformMatrix4fv(self.location['modelRotationMatrix'], 1, GL_FALSE, model.view.rotationMatrix)

            # Explain data form stored in model data buffers
            glBindBuffer(GL_ARRAY_BUFFER, bd.positionBuffer)
            glVertexAttribPointer(self.location['in_position'], bd.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
            glBindBuffer(GL_ARRAY_BUFFER, bd.colorBuffer)
            glVertexAttribPointer(self.location['in_color'], bd.colorDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
            glBindBuffer(GL_ARRAY_BUFFER, bd.normalBuffer)
            glVertexAttribPointer(self.location['in_normal'], bd.normalDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))

            # Draw number of elements binded in buffer arrays
            glDrawArrays(GL_TRIANGLES, 0, bd.numVectors)

    def resizeGL(self, width, height):
        if width + height == 0:
            return

        # Update size of viewport
        glViewport(0, 0, width, height)

        # Update projection matrix
        projectionMatrix = Matrix44.perspective_projection(45, width / height, 0.1, 100.0)
        glUniformMatrix4fv(self.location['projectionMatrix'], 1, GL_FALSE, projectionMatrix)

    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()

        if btns != Qt.NoButton and self.mouse is not None:
            dx = self.mouse[0] - event.x()
            dy = self.mouse[1] - event.y()

            if btns == Qt.LeftButton:
                self.view.rotateX(dy / 2)
                self.view.rotateZ(dx / 2, local=True)
                self.__updateWorldRotationMatrix()
                self.updateGL()
            elif btns == Qt.RightButton:
                self.view.translate(dx=-dx / 1000, dy=dy / 1000)
                self.__updateWorldTranslationMatrix()
                self.updateGL()
            elif btns == Qt.MidButton:
                self.light[0] -= dx/20
                self.light[1] += dy/20
                self.__updateLight()
                self.updateGL()

        self.mouse = [event.x(), event.y()]

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.fitToScreen()
        self.updateGL()

    def wheelEvent(self, event: QWheelEvent):
        btns = event.buttons()

        if btns == Qt.MidButton:
            self.resetView()
        elif btns == Qt.NoButton:
            dz = event.angleDelta().y() / 100
            self.view.translate(dz=dz)
            self.__updateWorldTranslationMatrix()
            self.updateGL()

    def __updateLight(self):
        glUniform3fv(self.location['in_light'], 1, self.light)

    def __updateWorldRotationMatrix(self):
        glUniformMatrix4fv(self.location['worldRotationMatrix'], 1, GL_FALSE, self.view.rotationMatrix)

    def __updateWorldTranslationMatrix(self):
        glUniformMatrix4fv(self.location['worldTranslationMatrix'], 1, GL_FALSE, self.view.translationMatrix)

    def fitToScreen(self):
        vectors = []
        centers = []
        for model in self.models:
            for shape in model.shapes:
                p = shape.positions
                shapeVectors = np.array_split(np.array(p), len(p)/3)
                shapeCenter = model.view.translationMatrix * Vector3(np.mean(shapeVectors, axis=0), dtype=np.float32)
                vectors += shapeVectors
                centers.append(shapeCenter)

        center = np.mean(centers, axis=0)
        maxSize = max(np.linalg.norm(vectors-center, axis=1))

        self.view.init()
        self.view.translate(-center[0], -center[1], -3*maxSize)
        self.light = np.array([10, 10, 10], dtype=np.float32)
        self.view.rotateX(45)

        self.__updateWorldTranslationMatrix()
        self.__updateWorldRotationMatrix()
        self.__updateLight()
