# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from CParameterTree import ColorButton
from functions import findInDict
from setupPlot import setup_plot

class CustomizingWindow(QtGui.QMainWindow):
	def __init__(self,xname=None,yname=None,fontSize=14):
		super(CustomizingWindow,self).__init__()
		self.xname = xname
		self.yname = yname
		self.fsize = fontSize
		self.setupGUI()
	def setupGUI(self):
		self.setWindowTitle("Customize Combo plot")
		self.setGeometry(500, 300, 400, 300)
		# add central widget to window
		# set layout to central widget
		# add treewidget and another widget to
		# place button layout
		self.centralWidget = QtGui.QWidget()
		self.setCentralWidget(self.centralWidget)
		self.centralLayout = QtGui.QVBoxLayout()
		self.centralWidget.setLayout(self.centralLayout)
		self.tree = pg.TreeWidget()
		self.centralLayout.addWidget(self.tree)
		self.buttonsWidget = QtGui.QWidget()
		self.centralLayout.addWidget(self.buttonsWidget)
		self.centralLayout.setContentsMargins(0,0,0,0)
		# set up button layout
		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonsWidget.setLayout(self.buttonLayout)
		self.OkButton = QtGui.QPushButton()
		self.CancelButton = QtGui.QPushButton()
		self.OkButton.setText("OK")
		self.CancelButton.setText("Cancel")
		self.buttonLayout.addWidget(self.OkButton)
		self.buttonLayout.addWidget(self.CancelButton)
		self.buttonLayout.setContentsMargins(0,0,0,0)
		## set up tree widget
		self.tree.setHeaderHidden(True)
		self.tree.setDragEnabled(False)
		self.tree.setColumnCount(3)
		self.tree.setColumnWidth(0, 100)
		self.tree.setColumnWidth(1, 270)
		self.tree.setColumnWidth(2, 10)
		self.xNameParameter = pg.TreeWidgetItem(['X axis'])
		self.yNameParameter = pg.TreeWidgetItem(['Y axis'])
		self.fontSizeParameter = pg.TreeWidgetItem(['Font size'])
		self.tree.addTopLevelItem(self.xNameParameter)
		self.tree.addTopLevelItem(self.yNameParameter)
		self.tree.addTopLevelItem(self.fontSizeParameter)
		self.xNameBox = QtGui.QLineEdit()
		self.yNameBox = QtGui.QLineEdit()
		self.xNameBox.setText(self.xname)
		self.yNameBox.setText(self.yname)
		self.fontSizeBox = pg.SpinBox(value=self.fsize, bounds=[10, 20],step=1)
		self.xNameParameter.setWidget(1,self.xNameBox)
		self.yNameParameter.setWidget(1,self.yNameBox)
		self.fontSizeParameter.setWidget(1,self.fontSizeBox)
		self.CancelButton.clicked.connect(self.cancel)
		# self.OkButton.clicked.connect(self.dosmth)
	def cancel(self):
		self.xNameBox.setText(self.xname)
		self.yNameBox.setText(self.yname)
		self.fontSizeBox.setValue(self.fsize)
		self.hide()


	# def dosmth(self):
	# 	print 'Font Size = %d'%( self.fontSizeBox.val)
	# 	print 'X axis name = %s'%( self.xNameBox.text())
	# 	print 'Y axis name = %s'%( self.yNameBox.text())



if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = CustomizingWindow()
	w.show()
	App.exec_()