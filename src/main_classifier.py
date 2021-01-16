from random import randrange
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QTimer
from pyqtgraph.Qt import QtGui

from src.math import *

class Plot:
    def __init__(self):
        self.app = QtGui.QApplication([])

        self.grid = gl.GLGridItem()
        self.grid.scale(1, 1, 1)
        self.grid.setDepthValue(10)

        self.surface = gl.GLSurfacePlotItem(smooth=True, shader='heightColor', glOptions='opaque')
        self.points = gl.GLScatterPlotItem()
        self.points._pos = []

        self.win = gl.GLViewWidget()
        self.win.setWindowTitle('pyqtgraph example: GLSurfacePlot')
        self.win.setCameraPosition(distance=50,elevation=90, azimuth=0)

        self.win.addItem(self.grid)
        self.win.addItem(self.surface)
        self.win.addItem(self.points)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.init()

    def init(self):
        self.draw()
        self.win.show()
        self.timer.start(0.5)

    def draw(self):
        x, y, z = surface(fun.rastrigin)
        self.surface.setData(x, y, z)

    def addPoint(self, pos):
        self.points._pos.append(pos)
        self.points.setData(pos=np.array(self.points._pos))

    def run(self):
        self.app.exec_()

    def update(self):
        point = [randrange(-10, 10) for i in range(2)] + [0]
        self.addPoint(point)

plot = Plot()
plot.run()
