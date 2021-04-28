#!/usr/bin/env python3

"""

Code from http://www.labri.fr/perso/nrougier/python-opengl/#the-hard-way

"""

import ctypes
import logging

import numpy as np
import OpenGL.GL as gl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QOpenGLWindow


logger = logging.getLogger(__name__)


vertex_code = '''
attribute vec2 position;
void main()
{
  gl_Position = vec4(position, 0.0, 1.0);
}
'''


fragment_code = '''
void main()
{
  gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
'''


class MinimalGLWidget(QOpenGLWindow):
    def initializeGL(self):
        program = gl.glCreateProgram()
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        # Set shaders source
        gl.glShaderSource(vertex, vertex_code)
        gl.glShaderSource(fragment, fragment_code)

        # Compile shaders
        gl.glCompileShader(vertex)
        if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(vertex).decode()
            logger.error("Vertex shader compilation error: %s", error)

        gl.glCompileShader(fragment)
        if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(fragment).decode()
            print(error)
            raise RuntimeError("Fragment shader compilation error")

        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)
        gl.glLinkProgram(program)

        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            print(gl.glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')

        gl.glDetachShader(program, vertex)
        gl.glDetachShader(program, fragment)

        gl.glUseProgram(program)

        # Build data
        data = np.zeros((4, 2), dtype=np.float32)
        # Request a buffer slot from GPU
        buffer = gl.glGenBuffers(1)

        # Make this buffer the default one
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

        stride = data.strides[0]
        offset = ctypes.c_void_p(0)
        print(stride, offset)
        loc = gl.glGetAttribLocation(program, "position")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, offset)

        # Assign CPU data
        data[...] = [(-1, +1), (+1, -1), (-1, -1), (+1, -1)]

        # Upload CPU data to GPU buffer
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


if __name__ == '__main__':
    app = QApplication([])
    widget = MinimalGLWidget()
    widget.show()
    app.exec_()