from EffectiveStressSettings import EffectiveStressSettings
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
# import numpy as np
from ConfigParser import SafeConfigParser
from configobj import ConfigObj

class SettingsWidget(QtGui.QMainWindow):
	"""docstring for SettingsWidget"""
	def __init__(self):
		super(SettingsWidget, self).__init__()
		self.setupGUI()
		self.loadConfig()
		self.okButton.clicked.connect(self.saveConfig)
		self.cancelButton.clicked.connect(self.cancel)
	def loadConfig(self):
		# config = SafeConfigParser()
		# config.read('config.ini')
		config = ConfigObj('config.ini')
		p1 = config['effective_stress']['Axial_stress']
		p2 = config['effective_stress']['Confining_stress']
		p3 = config['effective_stress']['Pore_pressure']
		p4 = config['effective_stress']['Biot']
		self.mcWidget.setParameters([p1,p2,p3,p4])
	def setupGUI(self):
		self.setWindowTitle('Settings')
		self.setGeometry(500, 300, 400, 300)
		centralWidget = QtGui.QWidget()
		self.centralLayout = QtGui.QVBoxLayout()
		self.setCentralWidget(centralWidget)
		centralWidget.setLayout(self.centralLayout)

		self.tabWidget = QtGui.QTabWidget()
		self.mcWidget = EffectiveStressSettings()
		self.tabWidget.addTab(self.mcWidget,u'Effective stress')
		# set up button layout
		self.buttonsWidget = QtGui.QWidget()
		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonsWidget.setLayout(self.buttonLayout)
		self.okButton = QtGui.QPushButton("OK")
		self.cancelButton = QtGui.QPushButton("Cancel")

		self.buttonLayout.addWidget(self.okButton)
		self.buttonLayout.addWidget(self.cancelButton)
		self.buttonLayout.setContentsMargins(0,0,0,5)
		self.centralLayout.addWidget(self.tabWidget)

		self.centralLayout.addWidget(self.buttonsWidget)
	def saveConfig(self):
		print 'Saving Settings'
		p = self.mcWidget.parameters()
		config = ConfigObj('config.ini')
		config['effective_stress'] = {}
		config['effective_stress']['Axial_stress'] = p[0]
		config['effective_stress']['Confining_stress'] = p[1]
		config['effective_stress']['Pore_pressure'] = p[2]
		config['effective_stress']['Biot'] = p[3]
		config.write()

		    
	def cancel(self):
		print 'cancel settings change'
		self.loadConfig()
		self.hide()

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = SettingsWidget()
	w.setWindowTitle('Settings')
	w.show()
	App.exec_()