from typing import List

import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QThreadPool, Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QHBoxLayout, QSlider, \
    QShortcut, QLabel

from src import utils
from src.gui.plot import Shape, Model
from src.gui.plot.colormap import colormaps
from src.gui.plot.model import CMAP, SCALE
from src.gui.widgets import OpenGLWidget
from src.gui.worker import Worker
from src.optimization.space import functions, Function
from src.optimization.test import TestOptimizer


class MainWindow(QtWidgets.QMainWindow):
    widgetsHL: QHBoxLayout

    startPB: QPushButton
    stopPB: QPushButton

    iterationsSB: QSpinBox
    iterationPauseSB: QSpinBox
    nameCB: QComboBox
    ortogonalViewCB: QComboBox

    showPointsCB: QCheckBox
    showLinesCB: QCheckBox
    pointsSizeS: QSlider
    linesSizeS: QSlider
    ambientRateS: QSlider
    lightRateS: QSlider

    colormapCB: QComboBox
    scaleRateS: QSlider
    birdsEyeCB: QCheckBox
    transperencyCB: QCheckBox

    infoL: QLabel

    def __init__(self):
        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(utils.getPath(__file__, 'ui/MainWindow.ui'), self)  # Load the .ui file

        self.normalW: OpenGLWidget = OpenGLWidget(self)
        self.zoomW: OpenGLWidget = OpenGLWidget(self)
        self.widgets = [self.normalW, self.zoomW]

        self.widgetsHL.addWidget(self.normalW)
        self.widgetsHL.addWidget(self.zoomW)

        self.startPB.clicked.connect(self.on_start)
        self.stopPB.clicked.connect(self.on_stop)
        self.nameCB.currentIndexChanged.connect(self.on_name_change)
        self.birdsEyeCB.stateChanged.connect(self.on_birdsEye_toggle)
        self.ortogonalViewCB.stateChanged.connect(self.on_ortogonalView_toggle)
        self.scaleRateS.valueChanged.connect(self.on_scaleRate_change)
        self.iterationPauseSB.valueChanged.connect(self.on_iterationPause_change)
        self.colormapCB.currentIndexChanged.connect(self.on_colormap_change)
        self.transperencyCB.stateChanged.connect(self.on_transperency_toggle)
        self.lightCB.stateChanged.connect(self.on_light_toggle)
        self.pointsSizeS.valueChanged.connect(self.on_pointsSize_change)
        self.linesSizeS.valueChanged.connect(self.on_linesSize_change)
        self.ambientRateS.valueChanged.connect(self.on_ambientRate_change)
        self.lightRateS.valueChanged.connect(self.on_lightRate_change)

        self.lightCB.stateChanged.connect(self.on_light_toggle)

        self.inited = False

        self.findAction = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self)
        self.findAction.activated.connect(self.on_find_shortcut)
        self.nextPointTimer = QTimer(self)
        self.nextPointTimer.timeout.connect(self.on_nextPoint)

        self.optimizer = None
        self.iterationsLeft = None

        self.__init()

    def __init(self):
        for f in functions(2):
            self.nameCB.addItem(f'{f.name:<33}{f.hardness:>.2f}', f)

        for cmap in colormaps():
            self.colormapCB.addItem(QIcon(cmap.preview),'', userData=cmap.id)

    def on_load(self):
        self.inited = True
        self.on_name_change()

    def on_transperency_toggle(self, state):
        for w in self.widgets:
            w.transperency = state == 2
            w.update()

    def on_pointsSize_change(self, value):
        for w in self.widgets:
            w.pointsSize = value
            w.update()

    def on_linesSize_change(self, value):
        for w in self.widgets:
            w.linesSize = (value/60)**2
            w.update()

    def on_ambientRate_change(self, value):
        for w in self.widgets:
            w.ambientRate = value/100
            w.update()

    def on_lightRate_change(self, value):
        for w in self.widgets:
            w.lightRate = value/100
            print(w.lightRate, w.ambientRate)
            w.update()

    def on_light_toggle(self, state):
        lightOn = state == 2
        if lightOn:
            self.ambientRateS.setValue(65)
            self.lightRateS.setValue(83)
        else:
            self.ambientRateS.setValue(56)
            self.lightRateS.setValue(50)

        for w in self.widgets:
            w.light = lightOn
            w.lightRate = self.lightRateS.value()/100.0
            w.ambientRate = self.ambientRateS.value()/100.0
            w.update()

    def on_iterationPause_change(self, value):
        self.nextPointTimer.setInterval(value)

    def on_nextPoint(self):
        point = self.optimizer.nextPoint()
        point[-1] += 0.001
        pointShape = Shape().add_point(point, [0, 0, 0, 1])
        for w in self.widgets:
            funBB = w.functionModel.boundBox
            if w == self.zoomW and not(funBB.xMin <= point[0] <= funBB.xMax and funBB.yMin <= point[1] <= funBB.yMax):
                continue

            #TODO: THIS IS A HACK (IN NORMAL IS WRITTEN WHICH POINT IS STARTING AND NEDING POINT)
            lineShape = Shape().add_line(point, point, [1,1,1,1])
            # =============================================================================
            w.evalLinesModel.addShape(lineShape)
            w.evalPointsModel.addShape(pointShape)
            w.update()
        self.iterationsLeft -= 1
        self.infoL.setText('\n'.join([
            f'Iterations left: {self.iterationsLeft}',
        ]))

    def on_start(self):
        self.optimizer = TestOptimizer(self.nameCB.currentData())
        self.iterationsLeft = self.iterationsSB.value()
        self.nextPointTimer.setInterval(self.iterationPauseSB.value())
        self.nextPointTimer.start()

    def on_stop(self):
        for w in self.widgets:
            for m in w.evalLinesModel:
                m.setShapes([])
            w.evalPointsModel.setShapes([])
            w.update()
        self.nextPointTimer.stop()

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            # shape = Shape().add_cone([1,1,1,1])
            # model = Model(GL_TRIANGLES, 3)
            # model.addShape(shape)
            # wireModel = Model(GL_LINES, 3).addShape(Shape().add_boundBox(shape.boundBox))
            # self.normalW.models = [model, wireModel]
            # self.zoomW.models = [model, wireModel]
            # self.normalW.update()
            self.loadFunction(fun)

    def on_colormap_change(self):
        colormap = self.colormapCB.currentData()
        for w in self.widgets:
            w.colormap = colormap
            w.update()

    def on_find_shortcut(self):
        self.nameCB.setEditText('')
        self.nameCB.setFocus()

    def on_scaleRate_change(self, value: float):
        for w in self.widgets:
            w.scaleRate = (value / 100)**2
            w.update()

    def on_birdsEye_toggle(self, state: int):
        for w in self.widgets:
            w.birdsEye = state == 2
            w.update(screenView=True)

    def on_ortogonalView_toggle(self, state: int):
        for w in self.widgets:
            w.ortogonalView = state == 2
            w.update(screenView=True)

    def loadFunction(self, fun: Function):

        def work(fun: Function, zoom):

            # First min vector
            firstMinVector = np.array(fun.minVectors[0] + [fun.minValue])

            # Create shape
            shape = Shape().add_function(
                function=fun, step=150,
                color=[1, 0, 0, 1], zoom=zoom,
                zoomCenter=firstMinVector
            )

            bb = shape.boundBox
            center = bb.center()  # Todo: Comment this!!!
            scale = (1 / (bb.xMax - bb.xMin), 1 / (bb.yMax - bb.yMin), 1 / (bb.zMax - bb.zMin))

            # Create models
            models = []

            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3, initBuffers=False, shading=True, colormap=CMAP.NORMAL, scale=SCALE.NORMAL)
            funModel.addShape(shape)
            funModel.view.translate(*-center)
            funModel.view.scale(*scale)
            models.append(funModel)

            # Minimum models
            for min2DVector in fun.minVectors:
                minVector = np.array(min2DVector + [fun.minValue])
                minAxis = Shape()
                for i in range(3):
                    color = [1,0,0,1,0,0][i:i+3] + [1]
                    base = np.array([int(i==j)*(1/scale[j]) for j in range(3)])
                    minAxis.add_line((minVector - base).tolist(), (minVector+base).tolist(),color)
                minAxisModel = Model(GL_LINES, 3, initBuffers=False)
                minAxisModel.addShape(minAxis)
                minAxisModel.view.translate(*-center)
                minAxisModel.view.scale(*scale)
                models.append(minAxisModel)

            # Create box grid
            # boundBoxModel = Model(GL_LINES, 3, initBuffers=False)
            # boundBoxShape = Shape().add_boundBox(bb)
            # boundBoxModel.addShape(boundBoxShape)
            # boundBoxModel.view.translate(*-center)
            # boundBoxModel.view.scale(*scale)
            # models.append(boundBoxModel)

            return models

        def on_result(widget: OpenGLWidget, models: List[Model]):
            widget.functionModel = models[0]
            widget.axesModel = models[1]
            widget.evalPointsModel.view = models[0].view
            widget.evalLinesModel.view = models[0].view
            for m in models:
                m.initBuffers()
            widget.update(cameraView=True)
            self.startPB.setEnabled(True)

        self.startPB.setEnabled(False)
        pool = QThreadPool.globalInstance()
        worker0 = Worker(work, fun, 1)
        worker1 = Worker(work, fun, 10)
        worker0.signals.result.connect(lambda models: on_result(self.normalW, models))
        worker1.signals.result.connect(lambda models: on_result(self.zoomW, models))
        pool.start(worker0)
        pool.start(worker1)


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
