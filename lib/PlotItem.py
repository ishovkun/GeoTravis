# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re
from configobj import ConfigObj

class PlotItem(pg.PlotItem):
    def __init__(self,*args,**kwargs):
        super(PlotItem,self).__init__(None,*args,**kwargs)
        # self.ctrlMenu.clear()
        m = self.getViewBox().menu
        # print type(m)
        m.clear()
    def getContextMenus(self,event):
        return None


if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    # w = Widget()
    w = QtGui.QWidget()
    w.layout = QtGui.QVBoxLayout()
    w.setLayout(w.layout)
    plt = PlotItem()
    slo  = pg.GraphicsLayoutWidget()
    w.layout.addWidget(slo)
    slo.addItem(plt)
    w.show()
    App.exec_()