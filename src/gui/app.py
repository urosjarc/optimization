from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, \
    QHBoxLayout

from src import utils
from src.gui.plot import Shape, Model
from src.gui.widgets import GLWidget
from src.optimization.space import functions


class MainWindow(QtWidgets.QMainWindow):
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

        self.normal2D: GLWidget = GLWidget(self)
        self.normal3D: GLWidget = GLWidget(self)
        self.zoom2D: GLWidget = GLWidget(self)
        self.zoom3D: GLWidget = GLWidget(self)

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

    def on_start(self):
        print('start')

    def on_stop(self):
        print('stop')

    def on_name_change(self):
        fun = self.nameCB.currentData()
        if fun and self.inited:
            model = Model()
            model.addShape(Shape.Function(fun, 100, 1))
            model.center()
            self.normal2D.models = [model]
            self.normal2D.fitToScreen()
            self.normal2D.updateGL()
            # self.normal3D.models = [model]
            # self.zoom2D.models = [model]
            # self.zoom3D.models = [model]
        self.inited = True

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
