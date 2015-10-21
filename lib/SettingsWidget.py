import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
# import numpy as np
# from ConfigParser import SafeConfigParser
from configobj import ConfigObj
from EffectiveStressSettingsWidget import EffectiveStressSettingsWidget
from MainSettingsWidget import MainSettingsWidget

class SettingsWidget(QtGui.QMainWindow):
	"""docstring for SettingsWidget"""
	def __init__(self):
		super(SettingsWidget, self).__init__()
		self.conf = {}
		self.setupGUI()
		self.loadConfig()
		self.okButton.clicked.connect(self.saveConfig)
		self.cancelButton.clicked.connect(self.cancel)
	def loadConfig(self):
		# config = SafeConfigParser()
		# config.read('config.ini')
		config = ConfigObj('config.ini')
		self.mcWidget.setConfig(config['effective_stress'])
		self.msWidget.setConfig(config['Main parameters'])
		self.conf = config
	def setupGUI(self):
		self.setWindowTitle('Settings')
		self.setGeometry(500, 300, 400, 300)
		centralWidget = QtGui.QWidget()
		self.centralLayout = QtGui.QVBoxLayout()
		self.setCentralWidget(centralWidget)
		centralWidget.setLayout(self.centralLayout)

		self.tabWidget = QtGui.QTabWidget()
		self.mcWidget = EffectiveStressSettingsWidget()
		self.msWidget = MainSettingsWidget()
		self.tabWidget.addTab(self.msWidget,u'Main Settings')
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
		config = ConfigObj('config.ini')
		config['effective_stress'] = self.mcWidget.config()
		config['Main parameters'] = self.msWidget.config()
		config.write()
		self.close()

	def config(self):
		config = self.conf
		config['effective_stress'] = self.mcWidget.config()
		config['Main parameters'] = self.msWidget.config()
		return config

	def cancel(self):
		print 'cancel settings change'
		self.loadConfig()
		self.close()

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = SettingsWidget()
	w.setWindowTitle('Settings')
	w.show()
	App.exec_()