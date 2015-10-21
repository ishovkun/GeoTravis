import sys
import pyqtgraph as pg
import numpy as np
from PySide import QtCore, QtGui

class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        connect = np.ones(x.shape, dtype=bool)
        connect[:,-1] = 0 # don't draw the segment between each trace
        self.path = pg.arrayToQPath(x.flatten(), y.flatten(), connect.flatten())
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(pg.mkPen('b',width=1))
    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return pg.QtGui.QGraphicsItem.shape(self)
    def boundingRect(self):
        return self.path.boundingRect()

if __name__ == '__main__':
    
    App = QtGui.QApplication(sys.argv)
    x = np.array([[1,2,3],[4,5,6]])
    y = np.array([[1,1,1],[2,2,2]])
    a = MultiLine(x,y)
    # App._exec()
    # print a.__dict__