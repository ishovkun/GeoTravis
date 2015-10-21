# coding: UTF-8
 
import sys
import numpy as np
from PySide import QtGui, QtCore

class TableWidget(QtGui.QTableWidget):
	# sigTableChanged = QtCore.Signal(object)
	def __init__(self,labels=None):
		super(TableWidget, self).__init__()
		vheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Vertical)
		vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
		self.setVerticalHeader(vheader)
		vheader.hide()
		hheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
		# hheader.setDefaultSectionSize(50)
		hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
		self.setHorizontalHeader(hheader)
		if labels:
			self.setColumnCount(len(labels))
			self.setHorizontalHeaderLabels(labels)
		self.clipBoard = QtGui.QApplication.clipboard()
		self.copyAction = QtGui.QAction('',self,shortcut='Ctrl+C')
		self.addAction(self.copyAction)
		
		self.copyAction.triggered.connect(self.copySelection)
	def setData(self,data,labels=None):
		if labels:
			self.setColumnCount(len(labels))
			self.setHorizontalHeaderLabels(labels)
		self.setRowCount(data.shape[0])
		self.setColumnCount(data.shape[1])
		for i in range(data.shape[0]):
			for j in range(data.shape[1]):
				item = QtGui.QTableWidgetItem(str(data[i,j]))
				self.setItem(i, j, item)
	def setColumn(self,data,ncolumn):
		self.setRowCount(len(data))
		for i in range(len(data)):
			item = QtGui.QTableWidgetItem(str(data[i]))
			self.setItem(i, ncolumn, item)
		# self.cellChanged.connect(self.do)
	def copySelection(self):
		items = self.selectedItems()
		if items == []: return 0
		n = self.selectedRanges()[0].rowCount()
		m = self.selectedRanges()[0].columnCount()
		data = np.zeros((n,m))
		i=0; j=0;
		for item in items:
			data[i,j] = item.text()
			if i<n-1: i+=1
			else: i=0; j+=1;
		text ='\n'.join('\t'.join(str(cell)
				 for cell in row) for row in data)
		self.clipBoard.setText(text)
	def getValues(self):
		n = self.rowCount()
		m = self.columnCount()
		data = np.zeros((n,m))
		for i in xrange(n):
			for j in xrange(m):
				data[i,j] = self.item(i,j).text()
		return data

if __name__ == "__main__":
	Labels = ['P','Sx','Sy']
	data = np.array([[1,2,3],[4,5,6]])
	c2 = np.array([100,200])
	app = QtGui.QApplication(sys.argv)
	widget = TableWidget(Labels)
	widget.setData(data)
	widget.setColumn(c2,1)
	widget.getValues()
	widget.show()
	# print widget.getValues()
	sys.exit(app.exec_())