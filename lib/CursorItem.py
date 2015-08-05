# -*- coding: utf-8 -*-

import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from pyqtgraph.Point import Point
import sys
from pyqtgraph.graphicsItems.ROI import EllipseROI
from pyqtgraph.graphicsItems.ROI import ROI

class CursorItem(EllipseROI):
# class CursorItem(Ellipse):
    def __init__(self, pos, size, **args):
        ROI.__init__(self, pos, size, **args)
        self.aspectLocked = True
        self.hasData = False
        self.index = None
        self.currentPen = pg.mkPen(color=(255,0,255),width=2.5)
        self.setPen(self.currentPen)

    def mouseDragEvent(self, ev):
        EllipseROI.mouseDragEvent(self,ev)
        if self.translatable and self.isMoving and ev.buttons() == QtCore.Qt.LeftButton:
            if self.hasData: self.moveToNearest()
    def setData(self,xarray,yarray):
        self.xarray = xarray
        self.yarray = yarray
        self.hasData = True
        self.moveToNearest()
    def moveToNearest(self):
        '''
        moves cursor to the nearest point in x&y array
        '''
        # index of the nearest x data point
        # print self.index
        self.index = (np.abs(self.xarray-self.position()[0])).argmin()
        newPos = Point(self.xarray[self.index],self.yarray[self.index])
        self.translate(newPos - self.pos() - self.size()/2, snap=None, finish=False)
    def position(self):
    	return [self.pos().x()+self.size().x()/2,self.pos().y()+self.size().y()/2]
    def getSize(self):
    	return np.array([self.size().x(),self.size().y()])

    def setMouseHover(self, hover):
        ## Inform the ROI that the mouse is(not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        if hover:
            self.currentPen = pg.mkPen(color=(255, 150, 255),width=3)
        else:
            self.currentPen = self.pen
        self.update()

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    win = pg.GraphicsWindow()
    pg.setConfigOptions(antialias=True)
    plt = win.addPlot()
    x = np.linspace(0,10,100)
    y = 10-x
    plt.plot(x,y)
    cursor = CursorItem([3,5],[1,1],pen=(4,9))
    plt.addItem(cursor)
    cursor.setData(x,y)
    App.exec_()
