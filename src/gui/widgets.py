from typing import Dict, List

from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GL import shaders
from src import utils
from src.gui.plot import Scene


class GLWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        self.scenes: List[Scene] = []
        self.programLocations: Dict[str, GLuint]

    def __initScenes(self):
        scene = Scene()
        scene.setBuffers(
            position=[
                -1, +1,
                +1, -1,
                -1, -1
            ], color=[
                1, 0, 0, 1,
                0, 1, 0, 1,
                0, 0, 1, 1
            ])
        self.scenes.append(scene)

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

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glDepthFunc( GL_LEQUAL)

        # Configure what will happend at glClear call
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)

        self.__initScenes()

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for scene in self.scenes:
            self.__renderScene(scene)

    def __renderScene(self, scene: Scene):
        type = GL_FLOAT
        normalize = False
        stride = 0 # Number of bytes between values
        offset = ctypes.c_void_p(0)

        # Explain data form stored in binded buffers
        glBindBuffer(GL_ARRAY_BUFFER, scene.positionBuffer)
        glVertexAttribPointer(
            self.locations['in_position'], scene.positionDim,
            type, normalize, stride, offset)

        glBindBuffer(GL_ARRAY_BUFFER, scene.colorBuffer)
        glVertexAttribPointer(
            self.locations['in_color'], scene.colorDim,
            type, normalize, stride, offset)

        # Draw number of elements binded in buffer arrays
        glDrawArrays(GL_TRIANGLES, 0, scene.numVectors)

    def resizeGL(self, width, height):
        if width + height != 0:
            glViewport(0, 0, width, height)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0.0, width, 0.0, height, -1.0, 1.0)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

