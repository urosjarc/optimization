from random import randrange
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QTimer
from pyqtgraph.Qt import QtGui

from src.math import *
from pyqtgraph.examples import run
run()

class Plot:

    def __init__(self, surface: Surface):
        self.fun: Surface = surface
        self.app = QtGui.QApplication([])

        self.grid = gl.GLGridItem()
        self.grid.scale(1, 1, 1)
        self.grid.setDepthValue(10)

        self.surface = gl.GLSurfacePlotItem(x=self.fun.x, y=self.fun.y, z=self.fun.z, smooth=True, shader='viewNormalColor', glOptions='opaque')
        self.points = gl.GLScatterPlotItem()
        self.points._pos = []

        self.win = gl.GLViewWidget()
        self.win.setWindowTitle('pyqtgraph example: GLSurfacePlot')
        self.win.setCameraPosition(distance=200,elevation=90, azimuth=0)

        self.win.addItem(self.grid)
        self.win.addItem(self.surface)
        self.win.addItem(self.points)

        self.timer = QTimer()
        self.timer.timeout.connect(self.addPoint)

    def init(self):
        self.win.show()
        self.timer.start(0.5)
        self.app.exec_()

    def addPoint(self):
        pos = [randrange(*self.fun.range) for i in range(2)]
        pos.append(self.fun(pos[0], pos[1]))
        self.points._pos.append(pos)
        self.points.setData(pos=np.array(self.points._pos))

surface = Surface(fun.rastrigin, range=(-5, 5))
# surface = Surface(fun.eggholder, range=(-1000, 1000))
plot = Plot(surface)
plot.init()
