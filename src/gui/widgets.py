from typing import Dict, List

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent, QSurfaceFormat
from PyQt5.QtOpenGL import QGLFormat
from PyQt5.QtWidgets import QOpenGLWidget
from pyrr import Matrix44, Vector3

from src import utils
from src.gui.plot import Model, View
from src.gui.plot.colormap import colormaps


class OpenGLWidget(QOpenGLWidget):

    def __init__(self, parent):
        format = QSurfaceFormat()
        format.setSamples(8)
        QOpenGLWidget.__init__(self, parent=parent)
        self.setFormat(format)

        self.programLocations: Dict[str, GLuint]

        self.functionModel: Model = None
        self.axesModel: Model = None
        self.evalPointsModel: Model = None
        self.evalLinesModel: Model = None

        self.lightPosition = [1,1,5]
        self.birdsEye = False
        self.scaleRate = 0
        self.view = View()
        self.colormap: int = 0

        self.screenView = None
        self.mouse: List[int] = None
        self.setMouseTracking(True)

    def initializeGL(self):
        maps = ""
        cases = 'switch(in_colormap){\n'
        for i,cmap in enumerate(colormaps()):
            maps += cmap.parsedSrc + "\n"
            cases += f'''        case {cmap.id}:
            surfaceColor = {cmap.name}(modelPosition.z+0.5);
            surfaceColor_inverse = {cmap.name}(-modelPosition.z+0.5);
            break;
'''
        cases += '        default:\n'
        cases += '            surfaceColor = in_color;\n'
        cases += '            surfaceColor_inverse = in_color*-1;\n'
        cases += '            break;\n'
        cases += '    }'

        # Activate program and use it
        with open(utils.getPath(__file__, 'glsl/shader_vertex.glsl')) as f:
            src = f.read()
            src = src.replace("#include <colormap_shaders>", maps)
            src = src.replace("#include <colormap_shaders_switch>", cases)
            vs = shaders.compileShader(src, GL_VERTEX_SHADER)
        with open(utils.getPath(__file__, 'glsl/shader_fragments.glsl')) as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        program = shaders.compileProgram(vs, fs)
        glUseProgram(program)

        # Get program atributes locations
        self.location = {
            'modelView': glGetUniformLocation(program, 'modelView'),
            'cameraView': glGetUniformLocation(program, 'cameraView'),
            'normalView': glGetUniformLocation(program, 'normalView'),
            'screenView': glGetUniformLocation(program, 'screenView'),

            'in_scaleRate': glGetUniformLocation(program, 'in_scaleRate'),

            'in_lightPosition': glGetUniformLocation(program, 'in_lightPosition'),
            'in_shading': glGetUniformLocation(program, 'in_shading'),
            'in_colormapInverse': glGetUniformLocation(program, 'in_colormapInverse'),
            'in_colormap': glGetUniformLocation(program, 'in_colormap'),

            'in_position': glGetAttribLocation(program, 'in_position'),
            'in_normal': glGetAttribLocation(program, 'in_normal'),
            'in_color': glGetAttribLocation(program, 'in_color'),
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
        glPointSize(4.0)
        glLineWidth(1.0)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_LINE_SMOOTH)

        self.evalPointsModel = Model(GL_POINTS, 3, colormap=True, shading=False)
        self.evalLinesModel = Model(GL_LINES, 3, colormap=True, shading=False)
        self.functionModel = Model(GL_TRIANGLES, 3, colormap=True, shading=True)
        self.axesModel = Model(GL_LINES, 3, colormap=False, shading=False)

        self.update(context=False, cameraView=True, screenView=True)

    def paintGL(self):
        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set GLSL constants
        glUniformMatrix4fv(self.location['cameraView'], 1, GL_FALSE, self.cameraView)
        glUniformMatrix4fv(self.location['screenView'], 1, GL_FALSE, self.screenView)

        glUniform3fv(self.location['in_lightPosition'], 1, self.lightPosition)

        for model in [self.functionModel, self.axesModel, self.evalLinesModel, self.evalPointsModel]:

            glUniform1ui(self.location['in_shading'], np.uint(model.shading))
            glUniform1ui(self.location['in_colormap'], np.uint(self.colormap if model.colormap else -1))

            if model.bdata.drawMode != GL_LINES:
                glUniform1f(self.location['in_scaleRate'], np.float32(self.scaleRate))
            else:
                glUniform1f(self.location['in_scaleRate'], np.float32(0))

            if model.bdata.drawMode == GL_POINTS:
                glUniform1ui(self.location['in_colormapInverse'], np.uint(True))
            else:
                glUniform1ui(self.location['in_colormapInverse'], np.uint(False))


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
