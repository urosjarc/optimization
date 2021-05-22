from typing import List

import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QHBoxLayout, QSlider

from src import utils
from src.gui.plot import Shape, Model
from src.gui.widgets import OpenGLWidget
from src.gui.worker import Worker
from src.optimization.space import functions, Function


class MainWindow(QtWidgets.QMainWindow):
    widgetsHL: QHBoxLayout

    startPB: QPushButton
    stopPB: QPushButton

    iterationsSB: QSpinBox
    iterationPauseDSB: QDoubleSpinBox
    nameCB: QComboBox

    scaleHeightCB: QCheckBox
    scaleRateS: QSlider
    birdsEyeCB: QCheckBox

    def __init__(self):
        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(utils.getPath(__file__, 'ui/MainWindow.ui'), self)  # Load the .ui file

        self.normalW: OpenGLWidget = OpenGLWidget(self)
        self.zoomW: OpenGLWidget = OpenGLWidget(self)

        self.widgetsHL.addWidget(self.normalW)
        self.widgetsHL.addWidget(self.zoomW)

        self.startPB.clicked.connect(self.on_start)
        self.stopPB.clicked.connect(self.on_stop)
        self.nameCB.currentIndexChanged.connect(self.on_name_change)
        self.birdsEyeCB.stateChanged.connect(self.on_birdsEye_toggle)
        self.scaleRateS.valueChanged.connect(self.on_scaleRate_change)
        self.inited = False

        self.__init()

    def __init(self):
        for f in functions(2):
            self.nameCB.addItem(f'{f.name:<30}{f.hardness:>.2f}', f)

    def on_load(self):
        self.inited = True
        self.on_name_change()

    def on_start(self):
        print('start')

    def on_stop(self):
        print('stop')

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            self.loadFunction(fun)

    def on_scaleRate_change(self, value: float):
        for w in [self.normalW, self.zoomW]:
            w.scaleRate = 1.1 ** value + 2 if value != 0 else value
            w.update()

    def on_birdsEye_toggle(self, state: int):
        for w in [self.normalW, self.zoomW]:
            w.birdsEye = state == 2
            w.update(screenView=True)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

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
            scale = (1/(bb.xMax - bb.xMin), 1/(bb.yMax - bb.yMin), 1/(bb.zMax - bb.zMin))

            # Create models
            models = []

            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3, initBuffers=False)
            funModel.addShape(shape)
            funModel.view.translate(*-firstMinVector)
            funModel.view.scale(*scale)
            models.append(funModel)

            # Minimum models
            for min2DVector in fun.minVectors:
                minVector = np.array(min2DVector + [fun.minValue])
                minAxis = Shape()
                for i in range(3):
                    base = np.array([0,0,0])
                    base[i] = 1
                    minAxis.add_line((minVector-base*100).tolist(), (minVector+base*100).tolist(), base.tolist() + [1])
                minAxisModel = Model(GL_LINES, 3, initBuffers=False)
                minAxisModel.addShape(minAxis)
                minAxisModel.view.translate(*-firstMinVector)
                minAxisModel.view.scale(*scale)
                models.append(minAxisModel)

            return models

        def on_result(widget: OpenGLWidget, models: List[Model]):
            widget.models = models
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
