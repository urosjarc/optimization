import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread
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
        if fun and self.inited:
            self.setFunction(fun)

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def setFunction(self, fun: Function):

        # Create axis shape
        axis = Shape()
        axis.add_line([-100, 0, 0], [100, 0, 0], [1, 0, 0, 1])
        axis.add_line([0, -100, 0], [0, 100, 0], [0, 1, 0, 1])
        axis.add_line([0, 0, -100], [0, 0, 100], [0, 0, 1, 1])
        axisModel = Model(GL_LINES, 3)
        axisModel.addShape(axis)

        # Function infos
        deltaX, deltaY = np.linalg.norm(fun.bounds, axis=1)
        minVector = np.array(fun.minVectors[0] + [fun.minValue])

        # Step 2: Create a QThread object
        def on_finish(shape):
            self.startPB.setEnabled(True)
            self.progressPB.setValue(0)

            # Create function shape
            for info in [(1, self.normalW), (8, self.zoomW)]:
                zoom, wid3D = info

                deltaZ = abs(np.max(shape.positions[2::3]) - fun.minValue)

                # Create model with scalled x,y,z to ~1
                funModel = Model(GL_TRIANGLES, 3)
                funModel.addShape(shape)
                funModel.view.translate(*-minVector)
                funModel.view.scale(x=1 / deltaX, y=1 / deltaY, z=1 / deltaZ)

                wid3D.models = [funModel, axisModel]
                wid3D.resetView()
                wid3D.update()

        self.thread, self.worker = ShapeLoader.Function(function=fun, step=200, color=[1, 0, 0, 1], zoom=1, zoomCenter=fun.minVectors[0])
        self.worker.finished.connect(on_finish)
        self.startPB.setEnabled(False)


# Step 1: Create a worker class
class ShapeLoader(QObject):
    finished = pyqtSignal(Shape)
    def __init__(self, **args):
        self.args = args
        super().__init__()

    def run(self):
        """Long-running task."""
        shape = Shape().add_function(**self.args)
        self.finished.emit(shape)

    @staticmethod
    def Function(**args):
        thread = QThread()
        worker = ShapeLoader(**args)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()

        return (thread, worker)


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
