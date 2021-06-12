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
from src.gui.plot.model import CMAP, SCALE


class OpenGLWidget(QOpenGLWidget):

    def __init__(self, parent):
        format = QSurfaceFormat()
        format.setSamples(8)
        QOpenGLWidget.__init__(self, parent=parent)
        self.setFormat(format)

        self.programLocations: Dict[str, GLuint]

        self.functionModel = Model(GL_TRIANGLES, 3, initBuffers=False, colormap=CMAP.NORMAL, shading=True, scale=SCALE.NORMAL)
        self.axesModel = Model(GL_LINES, 3, initBuffers=False, colormap=CMAP.NONE, shading=False, scale=SCALE.NONE)
        self.evalPointsModel = Model(GL_POINTS, 3, initBuffers=False, colormap=CMAP.INVERSE, shading=False, scale=SCALE.NORMAL)
        self.evalLinesModel = Model(GL_LINES, 3, initBuffers=False, colormap=CMAP.INVERSE, shading=False, scale=SCALE.ELEVATE)

        self.transperency = True
        self.ortogonalView = False
        self.lightPosition = [10,10,100]
        self.birdsEye = False
        self.scaleRate = 0
        self.pointsSize = 10
        self.ambientRate = .56
        self.lightRate = .5
        self.linesSize = 2
        self.view = View()
        self.colormap: int = 0
        self.inverseColormap: bool = False
        self.light: bool = False

        self.screenView = None
        self.mouse: List[int] = None
        self.setMouseTracking(True)

    def initializeGL(self):
        maps = ""
        cases = 'switch(in_colormap){\n'
        for i,cmap in enumerate(colormaps()):
            maps += cmap.parsedSrc + "\n"
            cases += f'''        case {cmap.id}:
            colormap = {cmap.name}(modelPosition.z+0.5);
            colormap_inverse = {cmap.name}(-modelPosition.z+0.5);
            break;
'''
        cases += '        default:\n'
        cases += '            colormap = in_color;\n'
        cases += '            colormap_inverse = in_color*-1;\n'
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
        '''
        glUniformMatrix4fv(self.location['cameraView'], 1, GL_FALSE, self.cameraView)
        glUniformMatrix4fv(self.location['screenView'], 1, GL_FALSE, self.screenView)

        glUniform3fv(self.location['in_lightPosition'], 1, self.lightPosition)
        glUniform1ui(self.location['in_colormap'], np.uint(self.colormap))
        glUniform1f(self.location['in_scaleRate'], np.float32(self.scaleRate))

        for model in [self.functionModel, self.axesModel, self.evalLinesModel, self.evalPointsModel]:

            glUniform1ui(self.location['in_modelShading'], np.uint(model.shading))
            glUniform1ui(self.location['in_modelColormap'], np.uint(model.colormap))
            glUniform1ui(self.location['in_modelScale'], np.uint(model.scale))
        '''
        self.location = {
            'modelView': glGetUniformLocation(program, 'modelView'),
            'cameraView': glGetUniformLocation(program, 'cameraView'),
            'normalView': glGetUniformLocation(program, 'normalView'),
            'screenView': glGetUniformLocation(program, 'screenView'),

            'in_scaleRate': glGetUniformLocation(program, 'in_scaleRate'),
            'in_lightPosition': glGetUniformLocation(program, 'in_lightPosition'),
            'in_colormap': glGetUniformLocation(program, 'in_colormap'),
            'in_ambientRate': glGetUniformLocation(program, 'in_ambientRate'),
            'in_lightRate': glGetUniformLocation(program, 'in_lightRate'),
            'in_linesSize': glGetUniformLocation(program, 'in_linesSize'),

            'in_modelShading': glGetUniformLocation(program, 'in_modelShading'),
            'in_modelColormap': glGetUniformLocation(program, 'in_modelColormap'),
            'in_modelScale': glGetUniformLocation(program, 'in_modelScale'),

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
        glClearDepth(1.0)

        # Update widget
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_LINE_SMOOTH)

        self.evalPointsModel.initBuffers()
        self.evalLinesModel.initBuffers()
        self.functionModel.initBuffers()
        self.axesModel.initBuffers()

        self.update(context=False, cameraView=True, screenView=True)

    def paintGL(self):
        glPointSize(self.pointsSize)

        if self.light:
            paint = 0.9372549019607843
            glClearColor(paint, paint, paint, 1)
        else:
            glClearColor(0.1, 0.1, 0.1, 1)

        # Clear color buffer and depth z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set GLSL constants
        glUniformMatrix4fv(self.location['cameraView'], 1, GL_FALSE, self.cameraView)
        glUniformMatrix4fv(self.location['screenView'], 1, GL_FALSE, self.screenView)
        glUniform3fv(self.location['in_lightPosition'], 1, self.lightPosition)
        glUniform1ui(self.location['in_colormap'], np.uint(self.colormap))
        glUniform1f(self.location['in_scaleRate'], np.float32(self.scaleRate))
        glUniform1f(self.location['in_ambientRate'], np.float32(self.ambientRate))
        glUniform1f(self.location['in_lightRate'], np.float32(self.lightRate))
        glUniform1f(self.location['in_linesSize'], np.float32(self.linesSize))


        models = [self.functionModel, self.axesModel, self.evalLinesModel]
        if self.pointsSize > 0:
            models.append(self.evalPointsModel)

        for model in models:

            glEnable(GL_DEPTH_TEST)
            if self.transperency and model in [self.evalPointsModel, self.evalLinesModel]:
                glDisable(GL_DEPTH_TEST)

            glUniform1ui(self.location['in_modelShading'], np.uint(model.shading))
            glUniform1ui(self.location['in_modelColormap'], np.uint(model.colormap.value))
            glUniform1ui(self.location['in_modelScale'], np.uint(model.scale.value))

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
        self.update(screenView=True)

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
            if self.ortogonalView:
                dist = abs(self.view.translationMatrix.m43) / 5
                self.screenView = Matrix44.orthogonal_projection(-dist, dist, -dist, dist, 0.001, 100.0)
            else:
                aspect = self.width() / self.height()
                self.screenView = Matrix44.perspective_projection(45, aspect, 0.001, 100.0)

        if context:
            super(OpenGLWidget, self).update()
