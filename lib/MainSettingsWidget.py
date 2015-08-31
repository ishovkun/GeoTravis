# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re
from configobj import ConfigObj
from LineWidget import LineWidget

class MainSettingsWidget(QtGui.QWidget):
	def __init__(self):
		super(MainSettingsWidget,self).__init__(None,
		# QtCore.Qt.WindowStaysOnTopHint)
			)
		self.setupGUI()
	def setupGUI(self):
		# self.setWindowTitle("Igor")
		self.setGeometry(500, 300, 350, 200)
		self.layout = QtGui.QVBoxLayout()
		self.setLayout(self.layout)
		self.sliderLine = LineWidget(type='text',label='Slider parameter')
		self.timeLine = LineWidget(type='text',label='Time parameter (Do not touch)')
		self.fileHeaderLine = LineWidget(type='text',label='File header parameters')
		self.sampleLengthLine = LineWidget(type='text',label='Sample length parameter')
		self.layout.addWidget(self.sliderLine)
		self.layout.addWidget(self.timeLine)
		self.layout.addWidget(self.fileHeaderLine)
		self.layout.addWidget(self.sampleLengthLine)
		self.buttonsWidget = QtGui.QWidget()
		self.layout.addWidget(self.buttonsWidget)
		self.buttonsLayout = QtGui.QHBoxLayout()
		self.buttonsWidget.setLayout(self.buttonsLayout)

		# self.okButton = QtGui.QPushButton('OK')
		# self.cancelButton = QtGui.QPushButton('Cancel')
		# self.buttonsLayout.addWidget(self.okButton)
		# self.buttonsLayout.addWidget(self.cancelButton)
	def setConfig(self,config):
		self.sliderLine.setValue(config['slider'])
		self.timeLine.setValue(config['time'])
		self.fileHeaderLine.setValue(config['fileheader'])
		self.sampleLengthLine.setValue(config['SampleLengthParameter'])
		self.conf = config
	def config(self):
		time = self.timeLine.value()
		slider = self.sliderLine.value()
		fileHeaderText = self.fileHeaderLine.value()
		slengthpar = self.sampleLengthLine.value()
		self.conf['slider'] = slider
		self.conf['time'] = time
		self.conf['fileheader'] = fileHeaderText
		self.conf['SampleLengthParameter'] = slengthpar
		return self.conf
	def getHeaderExpr(self,text=None):
		'''
		get regex string to find header in clf file
		'''
		if text == None: text = self.fileHeaderLine.value()
		hlist = text.split(',')
		N = len(hlist)
		for i in xrange(N):
			hlist[i] = hlist[i].strip()
		expr = ''
		for i in xrange(N):
			expr += hlist[i]
			if i!=N-1:
				expr +='.*'
			else:
				expr += '[^\n]+'
		return expr
	def getSampleLengthExpr(self):
		text = self.sampleLengthLine.value()
		return self.getHeaderExpr(text=text)



if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = MainSettingsWidget()
	w.timeLine.setValue('Time')
	w.sliderLine.setValue('Time')
	w.show()
	App.exec_()