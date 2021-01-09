from random import random

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg
import csv


class WeightHeight:
    def __init__(self):
        self.win = None
        self.win3D = None
        self.errorCurve = None
        self.errors = []
        self.min_error = 10 ** 10
        self.model = None
        self.x = []
        self.y = []
        self.timer = None

        self.train_i = 0
        self.k = 0.5
        self.y0 = 0.5
        self.best_k = 0.5
        self.best_y0 = 0.5
        self.speed = 5

        self.init_data()
        self.normalize()
        self.init_window3D()
        self.error_space()
        self.init_window2D()


    def init_window3D(self):
        self.win3D = gl.GLViewWidget()
        g = gl.GLGridItem()
        g.scale(1, 1, 1)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.win3D.addItem(g)
        self.win3D.show()
        self.win3D.setWindowTitle('pyqtgraph example: GLSurfacePlot')
        self.win3D.setCameraPosition(distance=2)

    def init_window2D(self):
        self.win = pg.GraphicsWindow(title="Basic plotting examples")
        self.win.resize(1000, 600)
        self.win.setWindowTitle('pyqtgraph example: Plotting')

        #
        # 2D
        pg.setConfigOptions(antialias=True)
        p1 = self.win.addPlot(title="Training error", row=1, col=1)
        p2 = self.win.addPlot(title="Training sample", col=2, row=1, rowspan=2)

        self.errorCurve = p1.plot(np.random.normal(size=100), pen=(255, 0, 0))
        self.data = p2.plot(x=self.x, y=self.y, pen=None, symbol='o')
        self.model = p2.plot(x=[0, 1], y=[0, 1])

        # 3D
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.train)
        self.timer.start(1)

    def error_space(self):
        k = [i/100.0 for i in range(100)]
        y0 = [i/100.0 for i in range(100)]
        errors = []
        for ki in k:
            errors.append([])
            for y0i in y0:
                err = self.error(ki, y0i)
                errors[-1].append(err)

        x=np.array(k)
        y=np.array(y0)
        z=np.array(errors)
        z = z/z.max()
        p = gl.GLSurfacePlotItem(x, y, z, shader='heightColor')
        self.win3D.addItem(p)


    def normalize(self):
        max_x = max(self.x)
        max_y = max(self.y)
        self.x = [e / max_x for e in self.x]
        self.y = [e / max_y for e in self.y]

    def init_data(self):
        file = open('../data/weight-height.txt')
        for row in csv.DictReader(file):
            if row['Gender'] == 'Male':
                self.x.append(float(row['Height']))
                self.y.append(float(row['Weight']))

    def predict(self, k, y0, x):
        return k * x + y0

    def error(self, k, y0):
        error = 0
        for i in range(len(self.x)):
            x = self.x[i]
            y = self.y[i]
            yfun = self.predict(k, y0, x)
            error += abs(y - yfun)
        return error

    def new_error(self):
        self.train_i += 1
        err = self.error(self.k, self.y0)
        self.errors.append(err)
        self.errorCurve.setData(self.errors)
        if err < self.min_error:
            self.min_error = err
            self.best_k = self.k
            self.best_y0 = self.y0
        return err

    def train_info(self):
        info = [self.train_i, self.best_k, self.best_y0, self.min_error, self.speed]
        print([round(e, 2) for e in info])

    def draw_model(self):
        y1 = self.predict(self.k, self.y0, 0)
        y2 = self.predict(self.k, self.y0, 1)
        self.model.setData([y1, y2])

    def train(self):
        self.new_error()
        self.k = self.best_k + self.speed * (random() - 0.5)
        self.y0 = self.best_y0 + self.speed * (random() - 0.5)
        self.speed *= 0.998
        self.train_info()
        self.draw_model()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])
    model = WeightHeight()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
