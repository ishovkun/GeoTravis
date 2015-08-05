import sys
import numpy as np
import pyqtgraph as pg
from PySide import QtGui, QtCore
import setupPlot

WaveTypes = ['P','Sx','Sy']

class BindingWidget(QtGui.QWidget):
    def __init__(self,parents=None):
        super(BindingWidget, self).__init__(None,
        	QtCore.Qt.WindowStaysOnTopHint)
        self.setupGUI()
        self.gw = parents[0]
        self.sw = parents[1]
    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.sublayout = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.sublayout)
        self.plt = self.sublayout.addPlot()
        setupPlot.setup_plot(self.plt)
    def run(self):
    	self.show()
    	self.getSonicTimes()
    def getSonicTimes(self):
    	'''
    	every wave has its own recording time
    	geomecanic time range includes all sonic times
    	no need to plot all geomechanics
    	take average recording times for sonic data
    	plot geomechanics at them
    	also, there can be different amount of sonic data
    	for each wave. so must make arrays same length.
    	'''
    	l = []
    	for wave in WaveTypes:
	    	l.append(len(self.gw.sTimes[wave]))
    	l = 

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    # pg.mkQApp()
    win = BindingWidget()
    # win.showMaximized()
    # win.showFullScreen()
    win.show()
    App.exec_()
