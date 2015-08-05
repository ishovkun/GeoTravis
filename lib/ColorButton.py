# -*- coding: utf-8 -*-
import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
from PySide import QtCore, QtGui
import numpy as np

class ColorButton(pg.ColorButton):
	def __init__(self):
		super(ColorButton,self).__init__()
	def getColor(self):
		col = self.color(mode='float')
		color = [0,0,0]
		color[0] = col[0]*255
		color[1] = col[1]*255
		color[2] = col[2]*255
		return color