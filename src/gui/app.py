import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, QHBoxLayout

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

    logHeightCB: QCheckBox
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
        self.logHeightCB.stateChanged.connect(self.on_logaritmic_toggle)
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


    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_birdsEye_toggle(self, state: int):
        for w in [self.normalW, self.zoomW]:
            w.birdsEye = state == 2
            w.update(view=True, projection=True)


    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def loadFunction(self, fun: Function):

        axis = Shape()
        axis.add_line([-100, 0, 0], [100, 0, 0], [1, 0, 0, 1])
        axis.add_line([0, -100, 0], [0, 100, 0], [0, 1, 0, 1])
        axis.add_line([0, 0, -100], [0, 0, 100], [0, 0, 1, 1])
        axisModel = Model(GL_LINES, 3)
        axisModel.addShape(axis)

        deltaX, deltaY = np.linalg.norm(fun.bounds, axis=1)
        minVector = np.array(fun.minVectors[0] + [fun.minValue])

        def work(fun, zoom):
            # Create shape
            shape = Shape().add_function(function=fun, step=150, color=[1, 0, 0, 1], zoom=zoom, zoomCenter=fun.minVectors[0])

            # Function infos
            deltaZ = abs(np.max(shape.positions[2::3]) - fun.minValue)

            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3, initBuffers=False)
            funModel.addShape(shape)
            funModel.view.translate(*-minVector)
            funModel.view.scale(x=1 / deltaX, y=1 / deltaY, z=1 / deltaZ)

            return funModel

        def on_result(widget: OpenGLWidget, model: Model):
            model.initBuffers()
            widget.models = [axisModel, model]
            widget.update(view=True)
            self.startPB.setEnabled(True)

        # model0 = work(fun, 1)
        # model1 = work(fun, 8)
        # on_result(self.normalW, model0)
        # on_result(self.zoomW, model1)

        self.startPB.setEnabled(False)
        pool = QThreadPool.globalInstance()
        worker0 = Worker(work, fun, 1)
        worker1 = Worker(work, fun, 10)
        worker0.signals.result.connect(lambda model: on_result(self.normalW, model))
        worker1.signals.result.connect(lambda model: on_result(self.zoomW, model))
        pool.start(worker0)
        pool.start(worker1)


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
