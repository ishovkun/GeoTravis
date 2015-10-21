import sys,os
import numpy as np
import re
import pyqtgraph as pg
from PySide import QtGui, QtCore
from setupPlot import setup_plot
from ColorButton import ColorButton
from CheckBox import CheckBox

LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}
rand = lambda: np.random.rand()
get_color = lambda: (rand()*230,rand()*230,rand()*230)

class CalculatorPlot(QtGui.QWidget):
	active = False
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setupGUI()
		self.nItems = 0
		self.nmax = 0
		self.data = []
		self.removeButtons = {}
		self.applyButtons = {}
		self.colorButtons = {}
		self.names = []
		self.xTexts = {}
		self.yTexts = {}
		self.xTextBoxes = {}
		self.yTextBoxes = {}
		self.plotItems = {}
		self.addItem()
		self.applyButton.pressed.connect(self.getData)
		self.addPlotButton.pressed.connect(self.addItem)
		self.enterAction.triggered.connect(self.applyButton.pressed)
	def setupGUI(self):
		self.setWindowTitle("Calculator plot")
		self.setGeometry(80, 50, 800, 600)
		self.setWindowIcon(QtGui.QIcon('../images/Logo.png')) 
		pg.setConfigOption('background', (255,255,255))
		pg.setConfigOption('foreground',(0,0,0))
		self.layout = QtGui.QVBoxLayout()
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setSpacing(0)
		self.setLayout(self.layout)
		# split window into two halfs
		self.splitter = QtGui.QSplitter()
		self.splitter.setOrientation(QtCore.Qt.Horizontal)
		self.layout.addWidget(self.splitter)

		self.tree = pg.TreeWidget()
		self.sublayout = pg.GraphicsLayoutWidget()
		self.splitter.addWidget(self.tree)
		self.splitter.addWidget(self.sublayout)
		self.plt = self.sublayout.addPlot()
		setup_plot(self.plt)
		pg.setConfigOptions(antialias=True)

		self.tree.setHeaderHidden(True)
		self.tree.setDragEnabled(False)
		self.tree.setIndentation(10)
		self.tree.setColumnCount(3)
		self.tree.setColumnWidth(0, 110)
		self.tree.setColumnWidth(1, 90)
		self.tree.setColumnWidth(2, 5)

		optItem = pg.TreeWidgetItem(['Options'])
		xNameItem = pg.TreeWidgetItem(['x title'])
		yNameItem = pg.TreeWidgetItem(['y title'])
		optItem.addChild(xNameItem)
		optItem.addChild(yNameItem)

		addPlotItem = pg.TreeWidgetItem()
		self.addPlotButton = QtGui.QPushButton('Add')
		self.enterAction = QtGui.QAction('',self,shortcut='Return')
		self.addAction(self.enterAction)
		self.applyButton = QtGui.QPushButton('Apply')
		self.applyButton.setDisabled(True)

		addPlotItem.setWidget(0,self.applyButton)
		addPlotItem.setWidget(1,self.addPlotButton)
		self.items = pg.TreeWidgetItem(['Items'])
		self.tree.addTopLevelItem(optItem)
		self.tree.addTopLevelItem(self.items)
		self.tree.addTopLevelItem(pg.TreeWidgetItem())
		self.tree.addTopLevelItem(addPlotItem)
		optItem.setExpanded(True)

		self.xNameEdit = QtGui.QLineEdit('X')		
		self.yNameEdit = QtGui.QLineEdit('Y')		
		xNameItem.setWidget(1,self.xNameEdit)
		yNameItem.setWidget(1,self.yNameEdit)
		self.plt.setLabel('bottom', 'X',**LabelStyle)
		self.plt.setLabel('left', 'Y',**LabelStyle)

	def addItem(self):
		name = 'Item_%d'%(self.nmax)
		self.names.append(name)
		item = pg.TreeWidgetItem([name])
		# self.tree.addTopLevelItem(item)
		# self.tree.insertTopLevelItem(2+self.nItems,item)
		self.items.addChild(item)
		self.items.setExpanded(True)
		self.nItems += 1
		self.nmax += 1
		colorButton = ColorButton()
		self.colorButtons[name] = colorButton
		item.setWidget(1,colorButton)
		color = get_color()
		colorButton.setColor(color)
		xitem = pg.TreeWidgetItem(['x'])
		yitem = pg.TreeWidgetItem(['y'])
		xline = QtGui.QLineEdit()
		yline = QtGui.QLineEdit()
		xline.setPlaceholderText('Enter expression')
		yline.setPlaceholderText('Enter expression')
		self.xTextBoxes[name] = xline
		self.yTextBoxes[name] = yline
		self.xTexts[name] = ''
		self.yTexts[name] = ''
		self.plotItems[name] = {}
		xitem.setWidget(1,xline)
		yitem.setWidget(1,yline)
		item.addChild(xitem)
		item.addChild(yitem)
		item.setExpanded(True)
		buttonItem = pg.TreeWidgetItem()
		removeButton = QtGui.QPushButton('Remove')
		self.removeButtons[name] = removeButton
		buttonItem.setWidget(1,removeButton)
		item.addChild(buttonItem)

		removeButton.pressed.connect(self.removeItem)
		colorButton.sigColorChanged.connect(self.plot)

	def removeItem(self,itemName=None):
		if itemName == None:
			sender = self.sender()
			itemName = self.getParent(sender,self.removeButtons)
		index = self.names.index(itemName)
		self.items.takeChild(index)
		# self.tree.takeTopLevelItem(index)
		self.names.pop(index)
		del self.removeButtons[itemName]
		del self.xTexts[itemName]
		del self.yTexts[itemName]
		try: del self.plotItems[itemName]
		except: pass
		self.nItems -= 1
		self.plot()
	def getParent(self,item,dic):
		'''
		looks for item parent in dictionary
		'''
		for key in dic.keys():
			if dic[key] == item:
				return key
	def setData(self,data):
		'''
		data is a dictionary with np array values
		'''
		self.data = data
		someKey = data.keys()[0]
		npoints = len(data[someKey])
		self.indices = np.arange(npoints)
		self.applyButton.setDisabled(False)

	def getData(self):
		for key in self.names:
			if self.xTexts[key] == self.xTextBoxes[key].text():
				continue
			else:
				xText = self.xTextBoxes[key].text()
				x = self.parseExpression(xText)
				if isinstance(x,np.ndarray):
					self.plotItems[key]['x'] = x
					self.xTexts[key] = xText
			if self.yTexts[key] == self.yTextBoxes[key].text():
				continue
			else:
				yText = self.yTextBoxes[key].text()
				y = self.parseExpression(yText)
				if isinstance(x,np.ndarray):
					self.plotItems[key]['y'] = y
					self.yTexts[key] = yText
		self.plot()


	def parseExpression(self,expr):
		'''
		computes array corresponding to expression
		'''
		if expr=='': 
			return 0
		if 'import' in expr: return 0
		if 'sys' in expr: return 0
		if 'os' in expr: return 0
		for key in self.data.keys():
			# print self.data[key]
			exec('%s=self.data[\'%s\']'%(key,key))
			# print key
		try: 
			return eval(expr)
		except: 
			# print self.data.keys()
			return 0 

	def validItems(self):
		'''
		returns list of item names, for which both
		x and y exist
		'''
		itms = self.plotItems
		validNames = []
		for key in itms.keys():
			if itms[key] == {}: continue
			if 'x' in itms[key] and 'y' in itms[key]:
				pass
			else: continue
			validNames.append(key)			
		return validNames

	def plot(self):
		self.plt.clear()
		self.plt.showGrid(x=True, y=True)
		xlabel = self.xNameEdit.text()
		ylabel = self.yNameEdit.text()
		
		for name in self.validItems():
			x = self.plotItems[name]['x'][self.indices]
			y = self.plotItems[name]['y'][self.indices]
			color = self.colorButtons[name].getColor()
			pen = pg.mkPen(color=color, width=2)
			self.plt.plot(x,y,pen=pen)
		self.plt.setLabel('bottom', xlabel,**LabelStyle)
		self.plt.setLabel('left', ylabel,**LabelStyle)
		self.plt.enableAutoRange(enable=True)
	def closeEvent(self,event):
		self.active = False
		super(CalculatorPlot,self).closeEvent(event)

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    win = CalculatorPlot()
    x = np.array([0,1,2,3,4,5])
    x1 = x+5
    y = x*2
    y1 = x*3
    data = {'x':x,'y':y,'x1':x1,'y1':y1}
    win.setData(data)
    win.show()
    App.exec_()