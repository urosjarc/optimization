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
        self.init_window()

    def init_window(self):
        self.win = pg.GraphicsWindow(title="Basic plotting examples")
        self.win.resize(1000, 600)
        self.win.setWindowTitle('pyqtgraph example: Plotting')

        # self.win3D = gl.GLViewWidget()
        # g = gl.GLGridItem()
        # g.scale(2, 2, 1)
        # g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # self.win3D.addItem(g)
        # self.win3D.show()
        # self.win3D.setWindowTitle('pyqtgraph example: GLSurfacePlot')
        # self.win3D.setCameraPosition(distance=50)
        #
        # 2D
        pg.setConfigOptions(antialias=True)
        p1 = self.win.addPlot(title="Training error", row=1, col=1)
        p2 = self.win.addPlot(title="Training sample", col=2, row=1, rowspan=2)

        self.errorCurve = p1.plot(np.random.normal(size=100), pen=(255, 0, 0))
        self.data = p2.plot(x=self.x, y=self.y, pen=None, symbol='o')
        self.model = p2.plot(x=[0, 1], y=[0, 1])

        # 3D
        ## Animated example
        ## compute surface vertex data
        # cols = 90
        # rows = 100
        # x = np.linspace(-8, 8, cols + 1).reshape(cols + 1, 1)
        # y = np.linspace(-8, 8, rows + 1).reshape(1, rows + 1)
        # d = (x ** 2 + y ** 2) * 0.1
        # d2 = d ** 0.5 + 0.1

        ## precompute height values for all frames
        # phi = np.arange(0, np.pi * 2, np.pi / 20.)
        # z = np.sin(d[np.newaxis, ...] + phi.reshape(phi.shape[0], 1, 1)) / d2[np.newaxis, ...]

        ## create a surface plot, tell it to use the 'heightColor' shader
        ## since this does not require normal vectors to render (thus we
        ## can set computeNormals=False to save time when the mesh updates)
        # p4 = gl.GLSurfacePlotItem(x=x[:, 0], y=y[0, :], shader='heightColor', computeNormals=False, smooth=False)
        # p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
        # p4.translate(10, 10, 0)
        # self.win3D.addItem(p4)

        # index = 0
        # def update():
        #     global p4, z, index
        #     index -= 1
        #     p4.setData(z=z[index%z.shape[0]])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.train)
        self.timer.start(1)

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

    def predict(self, x):
        return self.k * x + self.y0

    def error(self):
        error = 0
        for i in range(len(self.x)):
            x = self.x[i]
            y = self.y[i]
            yfun = self.predict(x)
            error += abs(y - yfun)
        return error

    def new_error(self):
        self.train_i += 1
        err = self.error()
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
        y1 = self.predict(0)
        y2 = self.predict(1)
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
