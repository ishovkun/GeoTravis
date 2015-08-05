# -*- coding: utf-8 -*-
import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
from PySide import QtCore, QtGui
import numpy as np

class CheckBox(QtGui.QCheckBox):
	def __init__(self):
		super(CheckBox,self).__init__()
		self.name = None
	def value(self):
		if self.checkState() == QtCore.Qt.CheckState.Unchecked:
			return False
		elif self.checkState() == QtCore.Qt.CheckState.Checked:
			return True
	def setName(self,name):
		self.name = name

class ColorButton(pg.ColorButton):
	def __init__(self):
		super(ColorButton,self).__init__()
	def getColor(self):
		col = self.color(mode='float')
		color = [0,0,0]
		color[0] = col[0]*255
		color[1] = col[1]*255
		color[2] = col[2]*255
		return color

class CParameterTree(pg.TreeWidget):
	'''
	Tree with 3 columns:
		parameter name, checkbox, color button
	'''
	sigStateChanged = QtCore.Signal(object) # emitted when color changed
	def __init__(self,name=None,items=None,colors=None):
		super(CParameterTree,self).__init__()
		self.setColumnCount(4)
		self.setHeaderHidden(True)
		self.setDragEnabled(False)
		self.header = pg.TreeWidgetItem([name])
		self.setIndentation(0)
		headerBackgroundColor = pg.mkBrush(color=(100,100,100))
		fontcolor =pg.mkBrush(color=(255,255,255))
		self.header.setBackground(0,headerBackgroundColor)
		self.header.setBackground(1,headerBackgroundColor)
		self.header.setBackground(2,headerBackgroundColor)
		self.header.setBackground(3,headerBackgroundColor)
		self.header.setForeground(0,fontcolor)
		self.addTopLevelItem(self.header)
		self.header.setSizeHint(0,QtCore.QSize(-1, 25))
		self.setColumnWidth (0, 100)
		self.setColumnWidth (1, 50)
		self.setColumnWidth (2, 70)
		if items is not None: self.names = items
		else: self.names = []
		self.items = {} # main widgets
		self.colors = {} # color widgets
		self.boxes = {} # checkbox widgets
		if items: self.addItems(items,colors)
		
			
	def addItems(self, items,colors=None,indent=5):
		print 'Setting up tree'
		k = 0
		for item in items:
			child = pg.TreeWidgetItem([item])
			self.items[item] = child
			self.header.addChild(child)
			# box = QtGui.QCheckBox()
			box = CheckBox()
			box.setName(item)
			# colorButton = pg.ColorButton()
			colorButton = ColorButton()
			self.colors[item] = colorButton
			self.boxes[item] = box
			self.names.append(item)
			child.setWidget(1,box)
			child.setWidget(2,colorButton)
			child.setText(0,' '*indent+item)
			# print colorButton.color()
			if colors:
				if k<len(colors):
					colorButton.setColor(colors[k])
			k += 1
			colorButton.sigColorChanged.connect(self.emitStateChangedSignal)
			box.stateChanged.connect(self.emitStateChangedSignal)
		self.header.setExpanded(True)
	def emitStateChangedSignal(self):
		self.sigStateChanged.emit(self)
		# key = self.names[0]
		# print self.colors[key].getColor()
	def clear(self):
		print 'Clearing Tree'
		for key in self.items.keys():
			self.header.removeChild(self.items[key])
		self.items = {}
		self.colors = {}
		self.boxes = {}
		self.names = []

if __name__ == '__main__':
	names = ['chlen1','chlen2','chlen3']
	col = [(255,0,0),(0,255,0),(0,0,255)]
	app = QtGui.QApplication([])
	tree = CParameterTree(name='Data')
	# tree = CParameterTree(name='Data',items=names,colors=col)
	tree.clear()
	tree.addItems(names,col)
	tree.show()
	# print 'here'
	QtGui.QApplication.instance().exec_()