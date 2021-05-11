from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, QHBoxLayout, \
    QTabWidget

from src import utils
from src.gui.plot import Shape, Model
from src.gui.widgets import OpenGLWidget
from src.optimization.space import functions


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
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(utils.getPath(__file__, 'ui/MainWindow.ui'), self) # Load the .ui file

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

        model = Model()
        shape = Shape()
        shape.addSphere([1, 1, 1, 1])
        model.addShape(shape)
        model.center()

        import time
        for w in [self.normal2D, self.normal3D, self.zoom2D, self.zoom3D]:
            w.models = [model]
            start = time.time()
            w.fitToScreen()
            end = time.time()
            print(end - start) # Time in seconds, e.g. 5.38091952400282
            w.update()

    def on_start(self):
        print('start')

    def on_stop(self):
        print('stop')

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            model = Model()
            model.addShape(Shape.Function(fun, 200, 1))
            model.center()

            self.normal3D.models = [model]
            self.normal3D.fitToScreen()
            self.normal3D.update()
        self.inited = True

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0,mainWindow.on_load)
    app.exec()
