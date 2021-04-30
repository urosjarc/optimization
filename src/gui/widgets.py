from typing import Dict, List
import numpy as np

from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtOpenGL import QGLWidget

from src import utils
from src.gui.plot import Scene, View


class GLWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        self.setMouseTracking(True)
        self.mouse = [None, None]

        self.view = View()
        self.view.translate(dglobal_z=-5)
        self.scenes: List[Scene] = []
        self.programLocations: Dict[str, GLuint]

    def initializeGL(self):
        # Activate program and use it
        with open(utils.getPath(__file__, 'ui/shader_vertex.glsl')) as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)
        with open(utils.getPath(__file__, 'ui/shader_fragments.glsl')) as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vs, fs)

        # Use compiled shader program
        glUseProgram(program)

        # Get program atributes locations
        self.locations = {
            'in_position': glGetAttribLocation(program, 'in_position'),
            'in_color': glGetAttribLocation(program, 'in_color'),
            'projectionMatrix': glGetUniformLocation(program, 'projectionMatrix'),
            'viewMatrix': glGetUniformLocation(program, 'viewMatrix'),
            'modelMatrix': glGetUniformLocation(program, 'modelMatrix')
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.locations['in_position'])
        glEnableVertexAttribArray(self.locations['in_color'])

        # Setup model view matrix !!! projection matrix is setup in resizing event!
        self.__updateModelMatrix()
        self.__updateViewMatrix()

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

        # Add scene to GLWidgets
        scene = Scene()
        scene.setBuffers(position=[-1, +1, 0, +1, -1, 0, -1, -1, 0], color=[1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1])
        self.scenes.append(scene)

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for scene in self.scenes:
            self.__renderScene(scene)

    def __renderScene(self, scene: Scene):

        # Explain data form stored in binded buffers
        glBindBuffer(GL_ARRAY_BUFFER, scene.positionBuffer)
        glVertexAttribPointer(self.locations['in_position'], scene.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, scene.colorBuffer)
        glVertexAttribPointer(self.locations['in_color'], scene.colorDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))

        # Draw number of elements binded in buffer arrays
        glDrawArrays(GL_TRIANGLES, 0, scene.numVectors)

    def resizeGL(self, width, height):
        if width + height == 0:
            return

        # Update size of viewport
        glViewport(0, 0, width, height)

        # Setup projection matrix
        self.__updateProjectionMatrix(width, height)

    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()

        if btns != Qt.NoButton:
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
        self.resetView()

    def wheelEvent(self, event: QWheelEvent):
        btns = event.buttons()

        if btns == Qt.MidButton:
            self.resetView()
            self.updateGL()
        elif btns == Qt.NoButton:
            dz = event.angleDelta().y() / 100
            self.view.translate(dglobal_z=dz)
            self.__updateViewMatrix()
            self.updateGL()

    def __updateViewMatrix(self):
        glUniformMatrix4fv(self.locations['viewMatrix'], 1, GL_FALSE, self.view.viewMatrix())

    def __updateModelMatrix(self):
        glUniformMatrix4fv(self.locations['modelMatrix'], 1, GL_FALSE, self.view.modelMatrix())

    def __updateProjectionMatrix(self, width, height):
        projectionMatrix = self.view.projectionMatrix(width, height)
        glUniformMatrix4fv(self.locations['projectionMatrix'], 1, GL_FALSE, projectionMatrix)

    def resetView(self):
        vectors = []
        for scene in self.scenes:
            p = scene.positionData
            for i in range(0, len(p), 3):
                vectors.append([p[i], p[i + 1], p[i + 2]])

        meanV = np.mean(vectors, axis=0)

        maxSize = 0
        for v in np.array(vectors):
            diff = v - meanV
            size = np.linalg.norm(diff)
            if size > maxSize:
                maxSize = size

        self.view.globalLocation = [-meanV[0], -meanV[1], -maxSize]
        self.view.rot_global_x = 0
        self.view.rot_local_z = 0
        print('reset view')
