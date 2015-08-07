# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re
from configobj import ConfigObj

class AboutWidget(QtGui.QWidget):
	def __init__(self):
		super(AboutWidget,self).__init__(None,
		# QtCore.Qt.WindowStaysOnTopHint)
			)
		self.setupGUI()
	def setupGUI(self):
		self.setWindowTitle("About GeoTravis")
		self.setWindowIcon(QtGui.QIcon('images/Logo.png'))
		# self.setGeometry(500, 300, 350, 200)
		self.layout = QtGui.QHBoxLayout()
		self.setLayout(self.layout)
		self.image = QtGui.QPixmap()
		self.image.load('./images/Logo.png')
		self.image = self.image.scaled(200, 200, 
			QtCore.Qt.KeepAspectRatio) 
		# self.image.scaled(100, 200, QtCore.Qt.IgnoreAspectRatio) 
		self.imgLabel = QtGui.QLabel(self)
		# self.imgLabel.setScaledContents(True)
		self.imgLabel.resize(110,102)
		self.imgLabel.setPixmap(self.image)
		self.textLable = QtGui.QLabel(self)
		self.textLable.setText('GeoTravis is awesome!!!\n'*15)
		self.layout.addWidget(self.imgLabel)
		self.layout.addWidget(self.textLable)

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = AboutWidget()
	w.setWindowIcon(QtGui.QIcon('../images/Logo.png'))
	# w.image.load('../images/Logo.png')
	# w.imgLabel.setPixmap(w.image)
	w.show()
	App.exec_()