from types import ModuleType
from typing import Dict

from OpenGL.GL import shaders
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QOpenGLWidget

from src.gui.glsl import shader
from src.gui.plot.model import *
from src.gui.ui import config


class OpenGLWidget(QOpenGLWidget):

    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent=parent)
        self.programLocations: Dict[str, GLuint]

        self.view: View = View()
        self.functionModel = FunctionModel()
        self.axesModel = AxisModel()
        self.evalPointsModel = EvalPointsModel()
        self.evalLinesModel = EvalLinesModel()
        self.locations = {}

        self.screenView = None
        self.mouse: List[int] = None
        self.setMouseTracking(True)

    def initLocation(self, program):
        # Set program atributes locations
        self.location = {
            'view_model': glGetUniformLocation(program, 'view_model'),
            'view_camera': glGetUniformLocation(program, 'view_camera'),
            'view_normal': glGetUniformLocation(program, 'view_normal'),
            'view_screen': glGetUniformLocation(program, 'view_screen'),
            'in_position': glGetAttribLocation(program, 'in_position'),
            'in_normal': glGetAttribLocation(program, 'in_normal'),
            'in_color': glGetAttribLocation(program, 'in_color'),
        }

        # Add config items to location
        for name, _ in config.getAll().items():
            self.location[f'ui_{name}'] = glGetAttribLocation(program, f'ui_{name}')

        # Activate program "in" atributes to be rendered in a process of rendering
        for name, val in self.location.items():
            if name.startswith('in_'):
                glEnableVertexAttribArray(val)

    def initializeGL(self):

        fs = shaders.compileShader(shader.fragmentSrc(), GL_FRAGMENT_SHADER)
        vs = shaders.compileShader(shader.vertexSrc(), GL_VERTEX_SHADER)
        program = shaders.compileProgram(vs, fs)
        glUseProgram(program)

        self.initLocation(program)

        # Anable depth testing in z-buffer, replace old value in z-buffer if value is less or equal to old one.
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_LINE_SMOOTH)

        glDepthFunc(GL_LEQUAL)
        glClearDepth(1.0)

        # Adding samples
        self.format().setSamples(8)

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
            transScale = 8.9 * 10e-5 * abs(dist)

            if self.birdsEye:
                if btns == Qt.LeftButton:
                    self.view.translate(dx=-dx * transScale, dy=dy * transScale)
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
            zoomScale = 5 * 10e-5 * dist
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
