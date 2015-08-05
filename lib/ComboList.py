# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from CParameterTree import ColorButton
from functions import findInDict
from setupPlot import setup_plot
from CustomizingWindow import CustomizingWindow

rand = lambda: np.random.rand()
class ComboList(QtGui.QMainWindow):
	'''
	Tree with 3 columns:
		parameter name, checkbox, color button
	'''
	sigStateChanged = QtCore.Signal(object) # emitted when color changed
	labelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}
	def __init__(self,name=None,items=None,colors=None):
		super(ComboList,self).__init__()
		self.setupGUI()
		self.setupPlotWindow()
		self.props = CustomizingWindow()
		self.names = []
		self.items = {}
		self.xData = {}
		self.yData = {}
		self.colorButtons = {}
		self.removeButtons = {}
		self.plotButton.clicked.connect(self.plot)
		self.customizeButton.clicked.connect(self.props.show)
		self.props.OkButton.clicked.connect(self.saveProps)
	def saveProps(self):
		self.props.xname = self.props.xNameBox.text()
		self.props.yname = self.props.yNameBox.text()
		self.props.fsize = self.props.fontSizeBox.val
		self.labelStyle['font-size'] = '%dpt'%(self.props.fsize)
		self.props.hide()
	def setupGUI(self):
		self.setWindowTitle("Combo Plot List")
		self.setGeometry(420, 350, 570, 200)
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
		self.plotButton = QtGui.QPushButton()
		self.customizeButton = QtGui.QPushButton()
		self.plotButton.setText("Plot")
		self.customizeButton.setText("Customize")
		self.buttonLayout.addWidget(self.plotButton)
		self.buttonLayout.addWidget(self.customizeButton)
		self.buttonLayout.setContentsMargins(0,0,0,0)
		## set up tree widget
		self.tree.setHeaderHidden(True)
		self.tree.setDragEnabled(False)
		self.tree.setColumnCount(4)
		self.tree.setColumnWidth(0, 400)
		self.tree.setColumnWidth(1, 70)
		self.tree.setColumnWidth(2, 60)
		self.tree.setColumnWidth(3, 35)

	def addItem(self,name,xdata,ydata):
		item = pg.TreeWidgetItem([name])
		self.names.append(name)
		self.items[name] = item
		self.tree.addTopLevelItem(item)
		# self.insertTopLevelItem(self.nitems,item)
		color = (rand()*230,rand()*230,rand()*230)
		colorButton = ColorButton()
		self.colorButtons[name] = colorButton
		colorButton.setColor(color)
		removeButton = QtGui.QPushButton("Remove", self)
		self.removeButtons[name] = removeButton
		item.setWidget(1,colorButton)
		item.setWidget(2,removeButton)
		removeButton.clicked.connect(self.removeItem)
		self.xData[name] = xdata
		self.yData[name] = ydata
	def removeItem(self):
		s = self.sender()
		name = findInDict(s,self.removeButtons)
		ind = self.names.index(name)
		del self.removeButtons[name]
		del self.colorButtons[name]
		del self.xData[name]
		del self.yData[name]
		self.names.pop(ind)
		self.tree.takeTopLevelItem(ind)
	def plot(self):
		self.clearPlotWindow()
		for name in self.names:
			color = self.colorButtons[name].getColor()
			linestyle = pg.mkPen(color=color, width=3)
			x = self.xData[name]
			y = self.yData[name]
			self.plt.plot(x,y,pen=linestyle,
				name=name)
			self.plt.enableAutoRange(enable=True)
			self.plt.setLabel('left',self.props.yname,**self.labelStyle)
			self.plt.setLabel('bottom',self.props.xname,**self.labelStyle)
		self.plotWindow.show()
		self.plotWindow.activateWindow()

	def setupPlotWindow(self):
		pg.setConfigOption('background', (255,255,255))
		pg.setConfigOption('foreground',(0,0,0))
		pg.setConfigOptions(antialias=True)
		self.plotWindow = QtGui.QWidget()
		self.plotWindow.setWindowTitle("Combo Plot")
		layout = QtGui.QVBoxLayout()
		layout.setContentsMargins(0,0,0,0)
		sublayout = pg.GraphicsLayoutWidget()
		self.plotWindow.setLayout(layout)
		layout.addWidget(sublayout)
		self.plt = sublayout.addPlot()
		setup_plot(self.plt)
		self.plt.showGrid(x=True, y=True)
		# self.plotWindow.show()
		self.legend = None



	def clearPlotWindow(self):
		'''
		clears plot from data. clears legend.
		if there is no legend creates it
		'''
		# default legend position
		position = [30,30]
		# clear plot area
		self.plt.clear()
		# remove old legend
		if self.legend: 
		    position = self.legend.pos()
		    self.legend.scene().removeItem(self.legend)
		# create new legend
		self.plt.addLegend([90,20],offset=position)
		self.legend = self.plt.legend
		# print self.legend.pos()

if __name__ == '__main__':
	DataListApp = QtGui.QApplication(sys.argv)
	l = ComboList()
	l.addItem('4len',[0,1],[0,1])
	l.addItem('4len1',[0,2],[0,1])
	l.show()
	DataListApp.exec_()