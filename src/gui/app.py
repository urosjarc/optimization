import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, QHBoxLayout, \
    QTabWidget

from src import utils
from src.gui.plot import Shape, Model
from src.gui.widgets import OpenGLWidget
from src.optimization.space import functions, Function


class MainWindow(QtWidgets.QMainWindow):
    tabWidget: QTabWidget
    normalBL: QHBoxLayout
    zoomBL: QHBoxLayout

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

        self.normal2D: OpenGLWidget = OpenGLWidget(self)
        self.normal3D: OpenGLWidget = OpenGLWidget(self)
        self.zoom2D: OpenGLWidget = OpenGLWidget(self)
        self.zoom3D: OpenGLWidget = OpenGLWidget(self)

        self.zoomBL.addWidget(self.zoom3D)
        self.zoomBL.addWidget(self.zoom2D)
        self.normalBL.addWidget(self.normal3D)
        self.normalBL.addWidget(self.normal2D)

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
        self.tabWidget.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        self.inited = True
        self.on_name_change()

    def on_start(self):
        print('start')

    def on_stop(self):
        print('stop')

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            self.setFunction(fun)

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def setFunction(self, fun: Function):
        funShape = Shape.Function(fun, 200, color=[1, 0, 0, 1])

        # Computer vector of minimal point with scaling
        maxXY = np.linalg.norm(fun.bounds, axis=1)
        maxZ_del = abs(np.max(funShape.positions[2::3]) - fun.minValue)
        max = maxXY.tolist() + [maxZ_del]
        minVector = np.array(fun.minVectors[0] + [fun.minValue])
        minVector /= max

        # Create model with scalled x,y,z to ~1
        model = Model()
        model.addShape(funShape)
        model.view.scale(x=1/maxXY[0], y=1/maxXY[1], z=1/maxZ_del)

        for w in [self.normal2D, self.normal3D, self.zoom2D, self.zoom3D]:
            w.models = [model]
            w.fitToScreen(center=minVector.tolist(), maxSize=1)
            w.update()


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
