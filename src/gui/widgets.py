from typing import Dict, List

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt
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


    def mouseMoveEvent(self, event: QMouseEvent):
        btns = event.buttons()
        if btns == Qt.LeftButton:
            dx = self.mouse[0] - event.x()
            dy = self.mouse[1] - event.y()
            self.view.rotate(global_x=dy, local_z=dx)
            glUniformMatrix4fv(self.locations['modelViewMatrix'], 1, GL_FALSE, self.view.modelViewMatrix())
            self.updateGL()
        elif btns == Qt.RightButton:
            dx = (self.mouse[0] - event.x())/100
            dy = (self.mouse[1] - event.y())/100
            print(dx, dy, self.view.globalLocation)
            self.view.translate(dglobal_x=dx, dglobal_y=dy)
            glUniformMatrix4fv(self.locations['modelViewMatrix'], 1, GL_FALSE, self.view.modelViewMatrix())
            self.updateGL()

        self.mouse = [event.x(), event.y()]

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
            'modelViewMatrix': glGetUniformLocation(program, 'modelViewMatrix')
        }

        # Activate program "in" atributes to be rendered in a process of rendering
        glEnableVertexAttribArray(self.locations['in_position'])
        glEnableVertexAttribArray(self.locations['in_color'])

        # Setup model view matrix !!! projection matrix is setup in resizing event!
        glUniformMatrix4fv(self.locations['modelViewMatrix'], 1, GL_FALSE, self.view.modelViewMatrix())

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

        self.__initScenes()

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for scene in self.scenes:
            self.__renderScene(scene)

    def resizeGL(self, width, height):
        if width + height == 0:
            return

        # Update size of viewport
        glViewport(0, 0, width, height)

        # Setup projection matrix
        projectionMatrix = self.view.projectionMatrix(width, height)
        glUniformMatrix4fv(self.locations['projectionMatrix'], 1, GL_FALSE, projectionMatrix)

    def __initScenes(self):
        scene = Scene()
        scene.setBuffers(
            position=[
                -1, +1, 0,
                +1, -1, 0,
                -1, -1, 0,
            ], color=[
                1, 0, 0, 1,
                0, 1, 0, 1,
                0, 0, 1, 1
            ])
        scene1 = Scene()
        scene1.setBuffers(
            position=[
                -.1, .1, +1,
                +.1, -.1, -1,
                -.1, .1, 0,
            ], color=[
                1, 0, 0, 1,
                0, 1, 0, 1,
                0, 0, 1, 1
            ])
        self.scenes += [scene, scene1]

    def __renderScene(self, scene: Scene):

        # Explain data form stored in binded buffers
        glBindBuffer(GL_ARRAY_BUFFER, scene.positionBuffer)
        glVertexAttribPointer(self.locations['in_position'], scene.positionDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, scene.colorBuffer)
        glVertexAttribPointer(self.locations['in_color'], scene.colorDim, GL_FLOAT, False, 0, ctypes.c_void_p(0))

        # Draw number of elements binded in buffer arrays
        glDrawArrays(GL_TRIANGLES, 0, scene.numVectors)
