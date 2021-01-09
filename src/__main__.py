import pyqtgraph as pg
import pyqtgraph.opengl as gl

### something to graph ######
from numpy import *
pi=3.1415
X=linspace(-10,10,100)
Z=exp(-0.1*X*X)*cos(0.3*(X.reshape(100,1)**2+X.reshape(1,100)**2))
print(Z)
#############################
# you need this call ONCE
app=pg.QtGui.QApplication([])
#############################

##### plot 3D surface data  ####
w = gl.GLViewWidget()
## Saddle example with x and y specified
p = gl.GLSurfacePlotItem(x=X, y=X, z=Z, shader='heightColor')
w.addItem(p)
# show
w.show()
pg.QtGui.QApplication.exec_()