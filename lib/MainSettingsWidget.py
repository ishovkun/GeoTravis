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
		self.layout.addWidget(self.sliderLine)
		self.layout.addWidget(self.timeLine)
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
		self.conf = config
	def config(self):
		time = self.timeLine.value()
		slider = self.sliderLine.value()
		self.conf['slider'] = slider
		self.conf['time'] = time
		return self.conf


if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = MainSettingsWidget()
	w.timeLine.setValue('Time')
	w.sliderLine.setValue('Time')
	w.show()
	App.exec_()