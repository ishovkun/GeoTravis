# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from LineWidget import LineWidget
from configobj import ConfigObj

class ConfigureEndCapsWidget(QtGui.QWidget):
	def __init__(self):
		super(ConfigureEndCapsWidget,self).__init__(None,
		# QtCore.Qt.WindowStaysOnTopHint)
			)
		self.setupGUI()
		self.loadConfig()
		self.configureLine.sigValueChanged.connect(self.setConfig)
		self.saveButton.pressed.connect(self.save)
		self.delButton.pressed.connect(self.delete)
		self.cancelButton.pressed.connect(self.cancel)
	def setConfig(self):
		confname = self.configureLine.value()
		if confname == 'New':
			self.delButton.setEnabled(False)
			self.nameLine.setEnabled(True)
			self.nameLine.setValue('')
			self.pTravelTime.setValue(10)
			self.sxTravelTime.setValue(10)
			self.syTravelTime.setValue(10)
		else:
			self.delButton.setEnabled(True)
			self.nameLine.setValue(confname)
			self.nameLine.setEnabled(False)
			self.pTravelTime.setValue(self.capconf[confname]['P'])
			self.sxTravelTime.setValue(self.capconf[confname]['Sx'])
			self.syTravelTime.setValue(self.capconf[confname]['Sy'])
	def cancel(self):
		self.close()
	def delete(self):
		confname = self.nameLine.value()
		del self.config['end-caps'][confname]
		self.configureLine.removeItem(confname)
		self.config.write()

	def save(self):
		confname = self.nameLine.value()
		p = self.pTravelTime.value()
		sx = self.sxTravelTime.value()
		sy = self.syTravelTime.value()
		self.config['end-caps'][confname] = {}
		self.config['end-caps'][confname]['P'] = p
		self.config['end-caps'][confname]['Sx'] = sx
		self.config['end-caps'][confname]['Sy'] = sy
		self.configureLine.addItem(confname)
		self.config.write()
		self.configureLine.setValue(confname)

	def loadConfig(self):
		self.config = ConfigObj('config.ini')
		self.capconf = self.config['end-caps']
		capkeys = self.capconf.keys()
		capkeys.append('New')
		self.configureLine.setValues(capkeys)
		self.configureLine.setValue('New')
		# self.
	def setupGUI(self):
		self.setWindowTitle("Edit end-cap configurations")
		self.setGeometry(500, 300, 350, 200)
		self.layout = QtGui.QVBoxLayout()
		self.setLayout(self.layout)
		self.configureLine = LineWidget(type='list',label='Configuration')
		self.nameLine = LineWidget(type='text',label='Name')
		self.pTravelTime = LineWidget(type='value',label=u'P travel time (μs)')
		self.sxTravelTime = LineWidget(type='value',label=u'Sx travel time (μs)')
		self.syTravelTime = LineWidget(type='value',label=u'Sy travel time (μs)')
		self.layout.addWidget(self.configureLine)
		self.layout.addWidget(self.nameLine)
		self.layout.addWidget(self.pTravelTime)
		self.layout.addWidget(self.sxTravelTime)
		self.layout.addWidget(self.syTravelTime)
		### button widget
		self.buttonWidget = QtGui.QWidget()
		self.layout.addWidget(self.buttonWidget)
		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonWidget.setLayout(self.buttonLayout)
		self.saveButton = QtGui.QPushButton('Save')
		self.delButton = QtGui.QPushButton('Delete')
		self.cancelButton = QtGui.QPushButton('Cancel')
		self.buttonLayout.addWidget(self.saveButton)
		self.buttonLayout.addWidget(self.delButton)
		self.buttonLayout.addWidget(self.cancelButton)

		self.delButton.setEnabled(False)

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = ConfigureEndCapsWidget()
	w.show()
	App.exec_()