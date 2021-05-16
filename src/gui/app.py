import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, QHBoxLayout

from src import utils
from src.gui.plot import Shape, Model
from src.gui.widgets import OpenGLWidget
from src.optimization.space import functions, Function


class MainWindow(QtWidgets.QMainWindow):
    widgetsHL: QHBoxLayout
    progressPB: QProgressBar

    startPB: QPushButton
    stopPB: QPushButton

    iterationsSB: QSpinBox
    iterationPauseDSB: QDoubleSpinBox
    nameCB: QComboBox

    logHeightCB: QCheckBox
    wireframeCB: QCheckBox

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
        self.wireframeCB.stateChanged.connect(self.on_wireframe_toggle)
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

        # Create axis
        axisModel = Model(GL_LINES, 3)
        axisShape = Shape()
        axisShape.addLine([0, 0, 0], [2, 0, 0], [0, 0, 0, 0])
        axisShape.addLine([0, 0, 0], [0, 2, 0], [0, 0, 0, 0])
        axisShape.addLine([0, 0, 0], [0, 0, 2], [0, 0, 0, 0])
        axisModel.addShape(axisShape)

        if fun and self.inited:
            self.setFunction(fun)

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def setFunction(self, fun: Function):

        # Create axis shape
        axis = Shape()
        axis.addLine([0, 0, 0], [1, 0, 0], [1, 0, 0, 1])
        axis.addLine([0, 0, 0], [0, 1, 0], [0, 1, 0, 1])
        axis.addLine([0, 0, 0], [0, 0, 1], [0, 0, 1, 1])
        axisModel = Model(GL_LINES, 3)
        axisModel.addShape(axis)

        # Function infos
        deltaX, deltaY = np.linalg.norm(fun.bounds, axis=1)
        minVector = np.array(fun.minVectors[0] + [fun.minValue])

        # Create function shape
        for info in [(1, self.normalW), (8, self.zoomW)]:
            zoom, wid3D = info

            funShape = Shape.Function(fun, step=200, color=[1, 0, 0, 1], zoom=zoom, zoomCenter=fun.minVectors[0])
            deltaZ = abs(np.max(funShape.positions[2::3]) - fun.minValue)

            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3)
            funModel.addShape(funShape)
            funModel.view.translate(*-minVector)
            funModel.view.scale(x=1 / deltaX, y=1 / deltaY, z=1 / deltaZ)

            wid3D.models = [funModel, axisModel]
            wid3D.fitToScreen(center=[0, 0.3, 3])
            wid3D.update()


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
