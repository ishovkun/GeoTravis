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

class GroupedTreeItem(pg.TreeWidgetItem):
	def __init__(self,  *args, **kwargs):
		super(GroupedTreeItem,self).__init__(*args, **kwargs)
		self.group = None
	def setGroup(self,group):
		self.group = group

class CParameterTree(pg.TreeWidget):
	'''
	Tree with 3 columns:
		parameter name, checkbox, color button
		-- added option to ad a group
	'''
	sigStateChanged = QtCore.Signal(object) # emitted when color changed
	def __init__(self,name=None,items=None,colors=None):
		super(CParameterTree,self).__init__()
		self.name = name
		self.setColumnCount(4)
		self.setHeaderHidden(True)
		self.setDragEnabled(False)
		self.header = pg.TreeWidgetItem([name])
		self.setIndentation(0)
		headerBackgroundColor = pg.mkBrush(color=(100,100,100))
		fontcolor = pg.mkBrush(color=(255,255,255))
		self.setupHeader()
		# self.header.setBackground(0,headerBackgroundColor)
		# self.header.setBackground(1,headerBackgroundColor)
		# self.header.setBackground(2,headerBackgroundColor)
		# self.header.setBackground(3,headerBackgroundColor)
		# self.header.setForeground(0,fontcolor)
		# self.addTopLevelItem(self.header)
		# self.header.setSizeHint(0,QtCore.QSize(-1, 25))
		# self.setColumnWidth (0, 100)
		# self.setColumnWidth (1, 50)
		# self.setColumnWidth (2, 70)
		self.setColumnWidth (3, 5)
		if items is not None: self.names = items
		else: self.names = []
		self.items = {} # main widgets
		self.colors = {} # color widgets
		self.boxes = {} # checkbox widgets
		self.groups = {} # just empty items
		if items: self.addItems(items,colors)
		# self.sigStateChanged.connect(self.stuff)
	def setupHeader(self):
		self.header = pg.TreeWidgetItem([self.name])
		self.setIndentation(0)
		headerBackgroundColor = pg.mkBrush(color=(100,100,100))
		fontcolor = pg.mkBrush(color=(255,255,255))
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

	def addItems(self, items,colors=None,group=None,indent=5):
		'''
		items - list of names
		colors - list of colors (can be None)
		group - name of the group. if None, items ain't grouped
		'''
		print 'Setting up tree'
		if group:
			subheader = pg.TreeWidgetItem([' '+group])
			self.header.addChild(subheader)
			self.groups[group] = {'items':{},
								  'boxes':{},
								  'colors':{},
								}
		k = 0
		for item in items:
			child = GroupedTreeItem([item])
			child.setGroup(group)
			self.items[item] = child
			if group:
				self.groups[group]['items'][item] = child
			self.header.addChild(child)
			# box = QtGui.QCheckBox()
			box = CheckBox()
			box.setName(item)
			# colorButton = pg.ColorButton()
			colorButton = ColorButton()
			self.colors[item] = colorButton
			self.boxes[item] = box
			if group:
				self.groups[group]['boxes'][item] = box
				self.groups[group]['colors'][item] = colorButton
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
		super(CParameterTree,self).clear()
		self.setupHeader()
		self.items = {}
		self.colors = {}
		self.boxes = {}
		self.names = []
		self.groups = {}

	def activeItems(self):
		activeItems = {}
		if self.groups == {}:
			pass
		else:
			for group in self.groups.keys():
				activeItems[group] = []
				g = self.groups[group]
				for key in g['items'].keys():
					if g['boxes'][key].value():
						activeItems[group].append(key)
				if activeItems[group] == []:
					del activeItems[group]
		return activeItems

	def stuff(self):
		print self.activeItems()

if __name__ == '__main__':
	names = ['chlen1','chlen2','chlen3']
	col = [(255,0,0),(0,255,0),(0,0,255)]
	app = QtGui.QApplication([])
	tree = CParameterTree(name='Data')
	# tree = CParameterTree(name='Data',items=names,colors=col)
	# tree.addItems(names,col)
	tree.addItems(names,col,group='Static')
	tree.addItems(names,col,group='Dynamic')
	# print tree.items['chlen1'].group
	# tree.clear()
	tree.show()
	QtGui.QApplication.instance().exec_()