from typing import Dict, List

from pyrr import Matrix44, Vector3
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtOpenGL import QGLWidget

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

        projectionMatrix = Matrix44.identity()
        modelViewMatrix = Matrix44.identity() * Matrix44.from_scale(Vector3([.2, .2, .2]))
        glUniformMatrix4fv(self.locations['projectionMatrix'], 1, GL_FALSE, projectionMatrix)
        glUniformMatrix4fv(self.locations['modelViewMatrix'], 1, GL_FALSE, modelViewMatrix)

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

        glViewport(0, 0, width, height)

        # Update projections
