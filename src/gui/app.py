import numpy as np
from OpenGL.GL import GL_TRIANGLES, GL_LINES
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QSpinBox, QComboBox, QCheckBox, QDoubleSpinBox, QProgressBar, QHBoxLayout, \
    QTabWidget
from pyrr import Vector3

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

    def test_view_matrixes(self):

        #Create model
        model = Model(GL_TRIANGLES,3)
        modelShape = Shape.Cone([1,1,1,1])
        model.addShape(modelShape)
        model.view.scale(z=10)

        # Prepare normals
        starts = np.array_split(np.array(modelShape.positions), len(modelShape.positions) / 3)
        normals = np.array_split(np.array(modelShape.normal), len(modelShape.normal) / 3)
        scaledStarts = []
        scaledNormals = []
        for i, n in enumerate(normals):
            no = n
            raise Exception("You stayed here!")
            #TODO no = model.view.scaleMatrix.inverse.matrix33.transpose() * Vector3(n)
            s = model.view.scaleMatrix.matrix33 * Vector3(starts[i])
            scaledNormals.append(no)
            scaledStarts.append(s)

        scaledNormals /= np.linalg.norm(scaledNormals, axis=0)
        ends = np.array(scaledStarts) + np.array(scaledNormals)*100
        lines = np.concatenate([scaledStarts, ends], axis=1)

        #Create normals
        normalsModel = Model(GL_LINES,3)
        normalsShape = Shape()
        normalsShape.positions = lines.ravel().tolist()
        normalsShape.normals = normalsShape.positions
        normalsShape.colors = 2*modelShape.colors
        normalsModel.addShape(normalsShape)


        return [model, axisModel, normalsModel]

    def on_name_change(self):
        fun = self.nameCB.currentData()

        #Create axis
        axisModel= Model(GL_LINES,3)
        axisShape = Shape()
        axisShape.addLine([0,0,0], [2,0,0], [0,0,0,0])
        axisShape.addLine([0,0,0], [0,2,0], [0,0,0,0])
        axisShape.addLine([0,0,0], [0,0,2], [0,0,0,0])
        axisModel.addShape(axisShape)

        if fun and self.inited:
            self.setFunction(fun)
            # for w in [self.normal2D, self.normal3D, self.zoom2D, self.zoom3D]:
            #     w.models = [model]
            #     w.fitToScreen(center=[0,0,0], maxSize=1)
            #     w.update()

    def on_logaritmic_toggle(self, state: int):
        print("logaritmic toggle", state)

    def on_wireframe_toggle(self, state: int):
        print("wireframe toggle", state)

    def setFunction(self, fun: Function):
        # Create function shape
        for info in [(1, self.normalW), (8, self.zoomW)]:

            zoom, wid3D = info

            funShape = Shape.Function(fun, step=200, zoom=zoom, color=[1, 0, 0, 1])

            # Computer vector of minimal point with scaling
            maxXY = np.linalg.norm(fun.bounds, axis=1)
            maxZ_del = abs(np.max(funShape.positions[2::3]) - fun.minValue)
            max = maxXY.tolist() + [maxZ_del]
            minVector = np.array(fun.minVectors[0] + [fun.minValue])
            minVector /= max
            # Create model with scalled x,y,z to ~1
            funModel = Model(GL_TRIANGLES, 3)
            funModel.addShape(funShape)
            funModel.view.scale(x=1/maxXY[0], y=1/maxXY[1], z=1/maxZ_del)

            # Create axis shape
            axis = Shape()
            axis.addLine(minVector.tolist(), (minVector + np.array([1,0,0])).tolist(), [1,0,0,1])
            axis.addLine(minVector.tolist(), (minVector + np.array([0,1,0])).tolist(), [0,1,0,1])
            axis.addLine(minVector.tolist(), (minVector + np.array([0,0,1])).tolist(), [0,0,1,1])
            axisModel = Model(GL_LINES, 3)
            axisModel.addShape(axis)

            wid3D.models = [funModel, axisModel]
            wid3D.fitToScreen(center=[0,0,0], maxSize=2)
            wid3D.update()


def start(argv):
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    mainWindow.show()
    t = QTimer()
    t.singleShot(0, mainWindow.on_load)
    app.exec()
