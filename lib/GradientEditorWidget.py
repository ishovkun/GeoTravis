# -*- coding: utf-8 -*-
from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys

class GradientEditorWidget(QtGui.QWidget):
    def __init__(self):
    	"""
        Plots Morh's Circles for given datapoints
    	"""
        QtGui.QWidget.__init__(self,
        	None,QtCore.Qt.WindowStaysOnTopHint)
        self.setupGUI()
        self.scm = self.sgw.colorMap()
        self.fcm = self.fgw.colorMap()
        self.pcm = self.pgw.colorMap()
        self.okButton.pressed.connect(self.ok)
        self.cancelButton.pressed.connect(self.cancel)
    def setupGUI(self):
		self.setWindowTitle("Edit Gradients")
		self.setGeometry(500, 300, 400, 200)
		self.layout = QtGui.QVBoxLayout()
		self.setLayout(self.layout)
		self.layout.setContentsMargins(0,0,0,0)
		self.tree = pg.TreeWidget()
		self.layout.addWidget(self.tree)
		self.tree.setHeaderHidden(True)
		self.tree.setDragEnabled(False)
		self.tree.setIndentation(10)
		self.tree.setColumnCount(3)
		self.sItem = pg.TreeWidgetItem(['Original Sonic Data'])
		self.fItem = pg.TreeWidgetItem(['Fourrier Transform'])
		self.pItem = pg.TreeWidgetItem(['Fourrier Phases'])
		self.tree.addTopLevelItem(self.sItem)
		self.tree.addTopLevelItem(self.fItem)
		self.tree.addTopLevelItem(self.pItem)
		self.sgw = pg.GradientWidget(orientation='top')
		self.fgw = pg.GradientWidget(orientation='top')
		self.pgw = pg.GradientWidget(orientation='top')
		self.sItem.setWidget(2,self.sgw)
		self.fItem.setWidget(2,self.fgw)
		self.pItem.setWidget(2,self.pgw)
		self.tree.setColumnWidth(0, 150)
		#### widget of ok and Cancel buttons
		self.buttonsWidget = QtGui.QWidget()
		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonsWidget.setLayout(self.buttonLayout)
		self.okButton = QtGui.QPushButton("OK")
		self.cancelButton = QtGui.QPushButton("Cancel")
		self.buttonLayout.addWidget(self.okButton)
		self.buttonLayout.addWidget(self.cancelButton)
		self.buttonLayout.setContentsMargins(0,0,0,5)
		self.layout.addWidget(self.buttonsWidget)
    def cancel(self):
        self.sgw.setColorMap(self.scm)
        self.fgw.setColorMap(self.fcm)
        self.pgw.setColorMap(self.pcm)
        self.hide()
    def ok(self):
        self.scm = self.sgw.colorMap()		
        self.fcm = self.fgw.colorMap()		
        self.pcm = self.pgw.colorMap()		
        self.hide()

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = GradientEditorWidget()
	w.show()
	App.exec_()