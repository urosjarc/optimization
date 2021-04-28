import ctypes
from typing import Dict, List

from PyQt5.QtOpenGL import QGLWidget
import numpy as np
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
            position=np.array([(-1, +1), (+1, -1), (-1, -1), (+1, -1)], dtype=np.float32),
            color=np.array([
                (1,0,0,1),
                (0,1,0,1),
                (0,0,1,1),
                (1,0,0,1),
            ], dtype=np.float32),

        )
        self.scenes.append(scene)

    def initializeGL(self):
        # Activate program
        with open(utils.getPath(__file__, 'ui/shader_vertex.glsl')) as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)
        with open(utils.getPath(__file__, 'ui/shader_fragments.glsl')) as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vs, fs)
        glUseProgram(program)

        # Get program locations
        self.programLocations = {
            'aVertexPosition': glGetAttribLocation(program, 'aVertexPosition'),
            'aVertexColor': glGetAttribLocation(program, 'aVertexColor'),
            # 'uProjectionMatrix': glGetUniformLocation(program, 'uProjectionMatrix'),
            # 'uModelViewMatrix': glGetUniformLocation(program, 'uModelViewMatrix')
        }

        self.__initScenes()

    def paintGL(self):
        glClearColor(1, 1, 1, 1)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for scene in self.scenes:
            self.__renderScene(scene)

    def __renderScene(self, scene: Scene):
        type = GL_FLOAT
        normalize = False
        vertexStride = scene.positionData.strides[0]
        colorStride = scene.colorData.strides[0]
        offset = ctypes.c_void_p(0)

        print(scene.positionData)

        # Vertex buffer setup
        aVertexPosition = self.programLocations['aVertexPosition']
        glEnableVertexAttribArray(aVertexPosition)
        glBindBuffer(GL_ARRAY_BUFFER, scene.positionBuffer)
        glVertexAttribPointer(aVertexPosition, 2, type, normalize, vertexStride, offset)

        # Color buffer setup
        aColorPosition = self.programLocations['aVertexColor']
        glEnableVertexAttribArray(aColorPosition)
        glBindBuffer(GL_ARRAY_BUFFER, scene.colorBuffer)
        glVertexAttribPointer(aColorPosition, 4, type, normalize, colorStride, offset)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    def resizeGL(self, width, height):
        if width + height != 0:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0.0, width, 0.0, height, -1.0, 1.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
