from typing import List

import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QThreadPool, Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QHBoxLayout, QSlider, \
    QShortcut, QLabel

from src import utils
from src.gui.glsl import shader
from src.gui.plot import Shape, Model
from src.gui.plot.model import FunctionModel, AxisModel
from src.gui.ui import config
from src.gui.widgets import OpenGLWidget
from src.gui.worker import Worker
from src.optimization.kdtree import KDTreeOptimizer
from src.optimization.space import functions, Function


class MainWindow(QtWidgets.QMainWindow):
    widgetsHL: QHBoxLayout

    startPB: QPushButton
    endPB: QPushButton

    iterationsSB: QSpinBox
    iterationPauseSB: QSpinBox
    nameCB: QComboBox
    ortogonalViewCB: QComboBox

    showPointsCB: QCheckBox
    showLinesCB: QCheckBox
    stopCB: QCheckBox
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
        self.inited = False
        self.optimizer = None
        self.iterationsLeft = None

        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(utils.getPath(__file__, 'ui/MainWindow.ui'), self)  # Load the .ui file

        self.normalW: OpenGLWidget = OpenGLWidget(self)
        self.zoomW: OpenGLWidget = OpenGLWidget(self)
        self.widgetsHL.addWidget(self.normalW)
        self.widgetsHL.addWidget(self.zoomW)
        self.widgets = [self.normalW, self.zoomW]

        self.__initValues()
        self.__initController()
        self.__initShortcuts()
        self.__initTimers()

    def __initTimers(self):
        self.nextPointTimer = QTimer(self)
        self.nextPointTimer.timeout.connect(self.on_nextPoint)

    def __initController(self):
        self.startPB.clicked.connect(self.on_start)
        self.stopCB.stateChanged.connect(self.on_stop_toggle)
        self.endPB.clicked.connect(self.on_end)

        self.iterationPauseSB.valueChanged.connect(self.on_iterationPause_change)
        self.nameCB.currentIndexChanged.connect(self.on_name_change)

        self.ortogonalViewCB.stateChanged.connect(self.on_ortogonalView_toggle)
        self.birdsEyeCB.stateChanged.connect(self.on_birdsEye_toggle)
        self.scaleRateS.valueChanged.connect(self.on_scaleRate_change)
        self.colormapCB.currentIndexChanged.connect(self.on_colormap_change)

        self.pointsSizeS.valueChanged.connect(self.on_pointsSize_change)
        self.linesSizeS.valueChanged.connect(self.on_linesSize_change)
        self.transperencyCB.stateChanged.connect(self.on_transperency_toggle)

        self.ambientRateS.valueChanged.connect(self.on_ambientRate_change)
        self.lightRateS.valueChanged.connect(self.on_lightRate_change)
        self.lightCB.stateChanged.connect(self.on_light_toggle)

    def __initValues(self):
        for f in functions(2):
            self.nameCB.addItem(f'{f.name:<33}{f.hardness:>.2f}', f)

        for cmap in shader.colormaps():
            self.colormapCB.addItem(QIcon(cmap.preview), '', userData=cmap.id)

    def __initShortcuts(self):
        self.findAction = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self)
        self.findAction.activated.connect(self.on_find_shortcut)

    def on_stop_toggle(self, state):
        if state == 2:
            self.nextPointTimer.stop()
        else:
            self.nextPointTimer.start()

    def on_load(self):
        self.inited = True
        self.on_name_change()

    def updateWidgets(self, screenView=False, cameraView=False):
        for w in self.widgets:
            w.update(screenView=screenView, cameraView=cameraView)

    def on_transperency_toggle(self, state):
        config.transperency = state == 2
        self.updateWidgets()

    def on_pointsSize_change(self, value):
        config.pointsSize = value
        self.updateWidgets()

    def on_linesSize_change(self, value):
        config.linesSize = (value / 60) ** 2
        self.updateWidgets()

    def on_ambientRate_change(self, value):
        config.ambientRate = value / 100
        self.updateWidgets()

    def on_lightRate_change(self, value):
        config.lightRate = value / 100
        self.updateWidgets()

    def on_light_toggle(self, state):
        lightOn = state == 2
        if lightOn:
            self.ambientRateS.setValue(65)
            self.lightRateS.setValue(83)
        else:
            self.ambientRateS.setValue(56)
            self.lightRateS.setValue(50)

        config.light = lightOn
        config.lightRate = self.lightRateS.value() / 100.0
        config.ambientRate = self.ambientRateS.value() / 100.0
        self.updateWidgets()

    def on_iterationPause_change(self, value):
        self.nextPointTimer.setInterval(value)

    def on_nextPoint(self):
        point = self.optimizer.nextPoint()
        pointShape = Shape().add_point(point, [0, 0, 0, 1])
        models = self.optimizer.models()
        for m in models:
            m.view = self.normalW.functionModel.view

        for w in self.widgets:
            w.userModels = models

            funBB = w.functionModel.boundBox
            if w == self.zoomW:
                inZoomRange = True
                for axis in range(funBB.dim):
                    if not (funBB.start[axis] <= point[axis] <= funBB.end[axis]):
                        inZoomRange = False
                        break
                if not inZoomRange:
                    continue

            # TODO: THIS IS A HACK (IN NORMAL IS WRITTEN WHICH POINT IS STARTING AND NEDING POINT)
            lineShape = Shape().add_line(point, point, [1, 1, 1, 1])
            # =============================================================================

            w.evalLinesModel.addShape(lineShape)
            w.evalPointsModel.addShape(pointShape)
            w.update()
        self.infoL.setText('\n'.join([
            f'Iterations left: {self.iterationsLeft - self.fun.evaluation}',
        ]))

    def on_start(self):
        self.fun: Function = self.nameCB.currentData()
        self.fun.evaluation = 0
        self.optimizer = KDTreeOptimizer(self.nameCB.currentData())
        for m in self.optimizer.models():
            m.initBuffers()
        self.iterationsLeft = self.iterationsSB.value()
        self.nextPointTimer.setInterval(self.iterationPauseSB.value())
        self.nextPointTimer.start()

        self.stopCB.setDisabled(False)
        self.stopCB.setChecked(False)

    def on_end(self):
        self.stopCB.setDisabled(True)
        for w in self.widgets:
            w.evalLinesModel.setShapes([])
            w.evalPointsModel.setShapes([])
            for m in w.userModels:
                m.setShapes([])
            w.update()
        self.nextPointTimer.stop()

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            self.loadFunction(fun)

    def on_colormap_change(self):
        config.colormap = self.colormapCB.currentData()
        self.updateWidgets()

    def on_find_shortcut(self):
        self.nameCB.setEditText('')
        self.nameCB.setFocus()

    def on_scaleRate_change(self, value: float):
        config.scaleRate = (value / 100) ** 2
        self.updateWidgets()

    def on_birdsEye_toggle(self, state: int):
        config.birdsEye = state
        self.updateWidgets(cameraView=True)

    def on_ortogonalView_toggle(self, state: int):
        config.ortogonalView = state == 2
        self.updateWidgets(screenView=True)

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
            center = bb.center()
            scale = [1 / (bb.end[i] - bb.start[i]) for i in range(bb.dim)]

            # Create model with scalled x,y,z to ~1
            funModel = FunctionModel(initBuffers=False)
            funModel.addShape(shape)
            funModel.view.translate(*-center)
            funModel.view.scale(*scale)

            # Minimum models
            minAxisModel = AxisModel(initBuffers=False)
            minAxisModel.view.translate(*-center)
            minAxisModel.view.scale(*scale)
            for min2DVector in fun.minVectors:
                minVector = np.array(min2DVector + [fun.minValue])
                minAxis = Shape()
                for i in range(3):
                    color = [1, 0, 0, 1, 0, 0][i:i + 3] + [1]
                    base = np.array([int(i == j) * (1 / scale[j]) for j in range(3)])
                    minAxis.add_line((minVector - base).tolist(), (minVector + base).tolist(), color)
                minAxisModel.addShape(minAxis)

            # Create box grid
            # boundBoxModel = Model(GL_LINES, 3, initBuffers=False)
            # boundBoxShape = Shape().add_boundBox(bb)
            # boundBoxModel.addShape(boundBoxShape)
            # boundBoxModel.view.translate(*-center)
            # boundBoxModel.view.scale(*scale)
            # models.append(boundBoxModel)

            return [funModel, minAxisModel]

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
