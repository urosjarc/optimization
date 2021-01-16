from src.test_functions import *

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

## Create a GL View widget to display data
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
w.setCameraPosition(distance=50)

## Add a grid to the view
g = gl.GLGridItem()
g.scale(2,2,1)
g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
w.addItem(g)

#
# Saddle example with x and y specified
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
z = []
for yi in y:
    z.append([])
    for xi in x:
        print(xi, yi)
        z[-1].append(rastrigin(xi, yi))
p2 = gl.GLSurfacePlotItem(x=x, y=y, z=np.array(z), shader='normalColor')
p3 = gl.GLScatterPlotItem(pos=np.array([1,1,rastrigin(1,1)]))
w.addItem(p2)
w.addItem(p3)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

