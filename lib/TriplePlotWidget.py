# coding: UTF-8
import sys,os
import pyqtgraph as pg
# import pickle
from PySide import QtGui, QtCore
# from pyqtgraph.parametertree import Parameter, ParameterTree
# from pyqtgraph.parametertree import types as pTypes
# from pyqtgraph.Point import Point
# import numpy as np
# from MultiLine import MultiLine
# from functions import *
from Gradients import Gradients
from setupPlot import setup_plot
# from TableWidget import TableWidget

WaveTypes = ['P','Sx','Sy']

class TriplePlotWidget(QtGui.QWidget):
	def __init__(self):
		super(TriplePlotWidget, self).__init__(None,QtCore.Qt.WindowStaysOnTopHint)
		self.setupGUI()
	def setupGUI(self):
		# self.setWindowTitle("Fourrier Transforms")
		pg.setConfigOption('background', (255,255,255))
		pg.setConfigOption('foreground',(0,0,0))
		self.layout = QtGui.QVBoxLayout()
		self.sublayout = pg.GraphicsLayoutWidget()
		self.setLayout(self.layout)
		self.layout.addWidget(self.sublayout)
		self.layout.setContentsMargins(0,0,0,0)
		self.plots = {}
		for wave in WaveTypes:
			self.plots[wave] = self.sublayout.addPlot()
			self.sublayout.nextRow()
			setup_plot(self.plots[wave])



if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	win = TriplePlotWidget()
	win.show()
	win.setGeometry(80, 30, 1000, 700)
	App.exec_()