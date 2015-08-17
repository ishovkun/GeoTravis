# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np

# import re
# from configobj import ConfigObj

class LineWidget(QtGui.QWidget):
	sigValueChanged = QtCore.Signal(object)
	def __init__(self,type='text',label=''):
		super(LineWidget,self).__init__()
		self.type = type
		self.layout = QtGui.QHBoxLayout()
		self.setLayout(self.layout)
		self.label = QtGui.QLabel(label)
		if type=='text':
			self.box = QtGui.QLineEdit()
		elif type == 'list':
			self.box = QtGui.QComboBox()
			self.box.currentIndexChanged.connect(self.emitSigValueChanged)
		elif type == 'value':
			self.box = pg.SpinBox(value=10)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.box)
	def setLabel(self,text):
		self.label.setText(text)
	def setValues(self,values):
		if self.type == 'text':
			self.box.setText(values)
		elif self.type == 'list':
			self.box.addItems(values)
		elif self.type == 'value':
			self.box.setValue(values)
	def setValue(self,value):
		if self.type == 'text':
			self.box.setText(value)
		elif self.type == 'list':
			ind = self.box.findText(str(value))
			self.box.setCurrentIndex(ind)
		elif self.type == 'value':
			self.box.setValue(value)
	def value(self):
		if self.type == 'text':
			return self.box.text()
		elif self.type == 'list':
			return self.box.currentText()
		elif self.type == 'value':
			return self.box.value()
	def addItem(self,item):
		'''
		meaningful only for list items
		'''
		if self.type == 'text': return
		elif self.type == 'list':
			self.box.addItem(item)
		elif self.type == 'value': return
	def removeItem(self,item):
		'''
		meaningful only for list items
		'''
		if self.type == 'text': return
		elif self.type == 'list':
			ind = self.box.findText(str(item))
			self.box.removeItem(ind)
		elif self.type == 'value': return
	def emitSigValueChanged(self):
		self.sigValueChanged.emit(self)