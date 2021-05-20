from typing import List

import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QHBoxLayout

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
        self.scaleHeightCB.stateChanged.connect(self.on_scaleHeight_toggle)
        self.birdsEyeCB.stateChanged.connect(self.on_birdsEye_toggle)
        self.inited = False

        self.__init()

    def __init(self):
        for f in functions(2):
            self.nameCB.addItem(f'{f.hardness:.2f} - {f.name}', f)

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

    def on_scaleHeight_toggle(self, state: int):
        for w in [self.normalW, self.zoomW]:
            w.scaleHeight = state == 2
            w.update()

    def on_birdsEye_toggle(self, state: int):
        for w in [self.normalW, self.zoomW]:
            w.birdsEye = state == 2
            w.update(screenView=True)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def loadFunction(self, fun: Function):

        axis = Shape()
        axis.add_line([0, 0, 0], [1, 0, 0], [1, 0, 0, 1])
        axis.add_line([0, 0, 0], [0, 1, 0], [0, 1, 0, 1])
        axis.add_line([0, 0, 0], [0, 0, 1], [0, 0, 1, 1])
        axisModel = Model(GL_LINES, 3)
        axisModel.addShape(axis)

        minVector = np.array(fun.minVectors[0] + [fun.minValue])

        def work(fun, zoom):
            # Create shape
            shape = Shape().add_function(function=fun, step=150, color=[1, 0, 0, 1], zoom=zoom,
                                         zoomCenter=fun.minVectors[0])
            bb = shape.boundBox
            scale = (1/(bb.xMax - bb.xMin), 1/(bb.yMax - bb.yMin), 1/(bb.zMax - bb.zMin))

            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3, initBuffers=False)
            funModel.addShape(shape)
            funModel.view.translate(*-minVector)
            funModel.view.scale(*scale)

            # Create box grid
            boundBoxModel = Model(GL_LINES, 3, initBuffers=False)
            boundBoxShape = Shape().add_boundBox(shape.boundBox)
            boundBoxModel.addShape(boundBoxShape)
            boundBoxModel.view.translate(*-minVector)
            boundBoxModel.view.scale(*scale)

            return funModel, boundBoxModel

        def on_result(widget: OpenGLWidget, models: List[Model]):
            widget.models = [axisModel]
            for m in models:
                m.initBuffers()
                widget.models.append(m)
            widget.update(cameraView=True)
            self.startPB.setEnabled(True)

        # model0 = work(fun, 1)
        # model1 = work(fun, 8)
        # on_result(self.normalW, model0)
        # on_result(self.zoomW, model1)

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
