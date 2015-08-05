# -*- coding: utf-8 -*-
import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
from PySide import QtCore, QtGui
import numpy as np

class CheckBox(QtGui.QCheckBox):
	def __init__(self):
		super(CheckBox,self).__init__()
		self.name = None
	def value(self):
		if self.checkState() == QtCore.Qt.CheckState.Unchecked:
			return False
		elif self.checkState() == QtCore.Qt.CheckState.Checked:
			return True
	def setName(self,name):
		self.name = name