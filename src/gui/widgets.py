from typing import Dict, List
import numpy as np

from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtOpenGL import QGLWidget

from src import utils
from src.gui.plot import Scene, View, Shape


class GLWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        self.setMouseTracking(True)
        self.mouse: List = None

        self.view = View()
        self.view.translate(dglobal_z=-5)
        self.scene: Scene = Scene()
        self.programLocations: Dict[str, GLuint]

    def initializeGL(self):
        # Activate program and use it
        with open(utils.getPath(__file__, 'ui/shader_vertex.glsl')) as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)
        with open(utils.getPath(__file__, 'ui/shader_fragments.glsl')) as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        # Use compiled shader program
        program = shaders.compileProgram(vs, fs)
        glUseProgram(program)

        # Get program atributes locations
        self.location = {
            'in_position': glGetAttribLocation(program, 'in_position'),
            'in_color': glGetAttribLocation(program, 'in_color'),
            'in_normal': glGetAttribLocation(program, 'in_normal'),
            'projectionMatrix': glGetUniformLocation(program, 'projectionMatrix'),
            'viewMatrix': glGetUniformLocation(program, 'viewMatrix'),
            'modelMatrix': glGetUniformLocation(program, 'modelMatrix'),
            'light': glGetUniformLocation(program, 'light'),
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.location['in_position'])
        glEnableVertexAttribArray(self.location['in_color'])
        glEnableVertexAttribArray(self.location['in_normal'])

        # Setup model view matrix and light !!! projection matrix is setup in resizing event!
        self.__updateModelMatrix()
        self.__updateViewMatrix()
        self.__updateLight()

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

        # Init widget scene
        self.scene.initBuffers()
        shape = Shape()
        # shape.addTriangle()
        # shape.addSphere([1,0,0,1])
        shape.addComplex([1,0,0,1])
        # shape.addSquare()
        self.scene.appendBuffers(shape)

        self.fitToScreen()

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Explain data form stored in binded buffers
        glBindBuffer(GL_ARRAY_BUFFER, self.scene.positionBuffer)
        glVertexAttribPointer(self.location['in_position'], self.scene.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, self.scene.colorBuffer)
        glVertexAttribPointer(self.location['in_color'], self.scene.colorDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, self.scene.normalBuffer)
        glVertexAttribPointer(self.location['in_normal'], self.scene.normalDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))

        # Draw number of elements binded in buffer arrays
        glDrawArrays(GL_TRIANGLES, 0, self.scene.numVectors)

    def resizeGL(self, width, height):
        if width + height == 0:
            return

        # Update size of viewport
        glViewport(0, 0, width, height)

        # Setup projection matrix
        self.__updateProjectionMatrix(width, height)

    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()

        if btns != Qt.NoButton and self.mouse is not None:
            dx = self.mouse[0] - event.x()
            dy = self.mouse[1] - event.y()

            if btns == Qt.LeftButton:
                self.view.rotate(global_x=dy / 2, local_z=dx)
                self.__updateModelMatrix()
                self.updateGL()
            elif btns == Qt.RightButton:
                self.view.translate(dglobal_x=-dx / 200, dglobal_y=dy / 200)
                self.__updateViewMatrix()
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
            self.view.translate(dglobal_z=dz)
            self.__updateViewMatrix()
            self.updateGL()

    def __updateLight(self):
        glUniform3fv(self.location['light'], 1, self.view.light)

    def __updateViewMatrix(self):
        glUniformMatrix4fv(self.location['viewMatrix'], 1, GL_FALSE, self.view.viewMatrix())

    def __updateModelMatrix(self):
        glUniformMatrix4fv(self.location['modelMatrix'], 1, GL_FALSE, self.view.modelMatrix())

    def __updateProjectionMatrix(self, width, height):
        projectionMatrix = self.view.projectionMatrix(width, height)
        glUniformMatrix4fv(self.location['projectionMatrix'], 1, GL_FALSE, projectionMatrix)

    def fitToScreen(self):
        vectors = []
        for shape in self.scene.shapes:
            p = shape.positions
            vectors += np.array_split(np.array(p), len(p)/3)

        meanV = np.mean(vectors, axis=0)
        maxSize = max(np.linalg.norm(vectors-meanV, axis=1))

        self.view.globalLocation = [-meanV[0], -meanV[1], -3*maxSize]
        self.view.rot_global_x = 0
        self.view.rot_local_z = 0

        self.__updateModelMatrix()
        self.__updateViewMatrix()
