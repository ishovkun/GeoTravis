# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re

class LineWidget(QtGui.QWidget):
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

class InterpretationSettingsWidget(QtGui.QWidget):
	def __init__(self):
		super(InterpretationSettingsWidget,self).__init__(None,
			QtCore.Qt.WindowStaysOnTopHint)
		self.setupGUI()
	def setupGUI(self):
		self.setWindowTitle("Interpretation settings")
		self.setGeometry(500, 300, 350, 200)
		self.centralLayout = QtGui.QHBoxLayout()
		self.setLayout(self.centralLayout)
		self.leftColumnWidget = QtGui.QWidget()
		self.rightColumnWidget = QtGui.QWidget()
		self.centralLayout.addWidget(self.leftColumnWidget)
		self.centralLayout.addWidget(self.rightColumnWidget)
		self.leftLayout = QtGui.QVBoxLayout()
		self.rightLayout = QtGui.QVBoxLayout()
		self.leftColumnWidget.setLayout(self.leftLayout)
		self.rightColumnWidget.setLayout(self.rightLayout)
		### LEFT COLUMN
		self.leftLabel = QtGui.QLabel('Static')
		self.testLine = LineWidget(type='list',label='Test')
		self.npoints = LineWidget(type='value',label='Number of points')
		emptyLabel = QtGui.QLabel('')
		emptyLabel.setMinimumSize(15,37)
		self.okButton = QtGui.QPushButton("OK")
		self.leftLayout.addWidget(self.leftLabel)
		self.leftLayout.addWidget(self.testLine)
		self.leftLayout.addWidget(self.npoints)
		self.leftLayout.addWidget(emptyLabel)
		self.leftLayout.addWidget(self.okButton)
		### RIGHT COLUMN
		self.rightLabel = QtGui.QLabel('Dynamic')
		self.densityLine = LineWidget(type='value',label='Bulk density')
		self.lengthLine = LineWidget(type='value',label='Sample length')
		self.capsLine = LineWidget(type='list',label='End caps config')
		self.cancelButton = QtGui.QPushButton("Cancel")
		self.rightLayout.addWidget(self.rightLabel)
		self.rightLayout.addWidget(self.densityLine)
		self.rightLayout.addWidget(self.lengthLine)
		self.rightLayout.addWidget(self.capsLine)
		self.rightLayout.addWidget(self.cancelButton)
		### SET VALUES
		self.testLine.setValues(['Uniaxial loading','Hydrostatic loading'])
		self.npoints.setValues(10)

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = InterpretationSettingsWidget()
	# w = LineWidget()
	w.show()
	App.exec_()