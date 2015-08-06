# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re
from configobj import ConfigObj
from LineWidget import LineWidget


class InterpretationSettingsWidget(QtGui.QWidget):
	def __init__(self):
		super(InterpretationSettingsWidget,self).__init__(None,
			QtCore.Qt.WindowStaysOnTopHint)
		self.setupGUI()
		self.loadConfig()
		self.testconf = None
		self.capsconf = None
		self.dens = None
		self.length = None
		self.atime = None
		self.okButton.pressed.connect(self.ok)
		self.cancelButton.pressed.connect(self.cancel)
	def loadConfig(self):
		config = ConfigObj('config.ini')
		# CONFIG FOR UNIAXIAL COMPRESSION
		# config['Main parameters'] = {}
		# config['Main parameters']['time'] = 'Time'
		# config['interpretation'] = {}
		# config['interpretation']['uniaxial loading'] = {}
		# nconf = config['interpretation']['uniaxial loading']
		# nconf['moduli'] = {}
		# nconf['moduli']['Young'] = {}
		# nconf['moduli']['Young']['x'] = 'Ex'
		# nconf['moduli']['Young']['y'] = 'SigD'
		# nconf['moduli']['Poisson'] = {}
		# nconf['moduli']['Poisson']['x'] = 'Ex'
		# nconf['moduli']['Poisson']['y'] = 'Ey'
		# nconf['Oscilloscope units'] = 'mus'
		# nconf['units'] = {}
		# nconf['units']['Young'] = 'psi'
		# nconf['units']['Young_x'] = 'psi'
		# nconf['units']['Young_y'] = 'psi'
		# nconf['units']['Shear'] = 'psi'
		# nconf['units']['Shear_x'] = 'psi'
		# nconf['units']['Shear_y'] = 'psi'
		# nconf['units']['Poisson'] = ''
		# nconf['units']['Poisson_x'] = ''
		# nconf['units']['Poisson_y'] = ''
		# SIMPLE CONFIG FOR END-CAPS
		# config['end-caps'] = {}
		# config['end-caps']['no_end_caps'] = {}
		# nconf = config['end-caps']['no_end_caps']
		# nconf['length'] = 0
		# nconf['vP'] = 100
		# nconf['vS'] = 100
		# # WRITE
		# config.write()
		# READ CONFIG
		self.config = config
		tests = config['interpretation'].keys()
		ecconf = config['end-caps'].keys()
		self.testLine.setValues(tests)
		self.capsLine.setValues(ecconf)
		self.interval.setValues(100.)
		self.lengthLine.setValues(5.)
		self.densityLine.setValues(2.7)

	def ok(self):
		test = self.testLine.value()
		self.testconf = self.config['interpretation'][test]
		caps = self.capsLine.value()
		self.capsconf = self.config['end-caps'][caps]
		self.dens = self.densityLine.value()
		self.length = self.lengthLine.value()
		self.atime = self.interval.value()
		# print self.capsconf
		self.close()

	def cancel(self):
		self.close()

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
		self.interval = LineWidget(type='value',label='Averaging interval (s)')
		emptyLabel = QtGui.QLabel('')
		emptyLabel.setMinimumSize(15,37)
		self.okButton = QtGui.QPushButton("OK")
		self.leftLayout.addWidget(self.leftLabel)
		self.leftLayout.addWidget(self.testLine)
		self.leftLayout.addWidget(self.interval)
		self.leftLayout.addWidget(emptyLabel)
		self.leftLayout.addWidget(self.okButton)
		### RIGHT COLUMN
		self.rightLabel = QtGui.QLabel('Dynamic')
		self.densityLine = LineWidget(type='value',label='Bulk density (g/cm3)')
		self.lengthLine = LineWidget(type='value',label='Sample length (cm)')
		self.capsLine = LineWidget(type='list',label='End-caps config')
		self.cancelButton = QtGui.QPushButton("Cancel")
		self.rightLayout.addWidget(self.rightLabel)
		self.rightLayout.addWidget(self.densityLine)
		self.rightLayout.addWidget(self.lengthLine)
		self.rightLayout.addWidget(self.capsLine)
		self.rightLayout.addWidget(self.cancelButton)
		### SET VALUES
		# self.testLine.setValues(['Uniaxial loading','Hydrostatic loading'])
		# self.npoints.setValues(10)


if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = InterpretationSettingsWidget()
	# w = LineWidget()
	w.show()
	App.exec_()