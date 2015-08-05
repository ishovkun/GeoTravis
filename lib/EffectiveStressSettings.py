# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re

class EffectiveStressSettings(QtGui.QWidget):
	def __init__(self):
		super(EffectiveStressSettings,self).__init__()
		self.setupGUI()
		self.formula = None
		# self.okButton.clicked.connect(self.saveParameters)
		# self.cancelButton.clicked.connect(self.cancel)
	def setupGUI(self):
		self.setWindowTitle("Edit effectibve stress formula")
		self.setGeometry(500, 300, 350, 200)
		# self.centralWidget = QtGui.QWidget()
		# self.setCentralWidget(self.centralWidget)
		self.centralLayout = QtGui.QVBoxLayout()
		# self.centralWidget.setLayout(self.centralLayout)
		self.setLayout(self.centralLayout)
		self.variablesText = QtGui.QLabel('')

		tree = pg.TreeWidget()
		tree.setHeaderHidden(True)
		tree.setIndentation(0)
		tree.setColumnCount(3)
		
		# stuff to make gray background for tree widget
		g = pg.mkBrush(240,240,240)
		b = pg.mkBrush(0,0,0)
		w = pg.mkBrush(255,255,255)
		bgBrush = pg.mkBrush(255,0,0)
		tree.setFrameShape(QtGui.QFrame.NoFrame)
		palette = QtGui.QPalette(g, g, g, g, g, b, b, g, g)
		tree.setPalette(palette)

		axStressItem = pg.TreeWidgetItem(['Axial stress'])
		# axStressItem.setTextAlignment(0,0)
		# axStressItem.setBackground(1,w)
		confStressItem = pg.TreeWidgetItem(['Confining pressure'])
		# confStressItem.setTextAlignment(0,0)
		porePressItem = pg.TreeWidgetItem(['Pore pressure'])
		biotItem = pg.TreeWidgetItem(['Biot coefficient'])
		porePressItem.setTextAlignment(0,0)

		self.axStressBox = QtGui.QLineEdit()
		self.confStressBox = QtGui.QLineEdit()
		self.porePressBox = QtGui.QLineEdit()
		self.biotBox = pg.SpinBox(value=1, bounds=[0.5, 1],step=0.1)
		
		axStressItem.setWidget(1,self.axStressBox)
		confStressItem.setWidget(1,self.confStressBox)
		biotItem.setWidget(1,self.biotBox)

		porePressItem.setWidget(1,self.porePressBox)
		tree.addTopLevelItem(axStressItem)
		tree.addTopLevelItem(confStressItem)
		tree.addTopLevelItem(porePressItem)
		tree.addTopLevelItem(biotItem)

		self.centralLayout.addWidget(self.variablesText)
		self.centralLayout.addWidget(tree)
		# self.centralLayout.addWidget(self.buttonsWidget)

		tree.setColumnWidth(0,120)
		tree.setColumnWidth(1,170)
		tree.setColumnWidth(2,10)

		# # set default parameters
		# p1 = Parameters['Axial stress']
		# p2 = Parameters['Confining pressure']
		# p3 = Parameters['Pore pressure']
		# p4 = Parameters['Biot coefficient']
		# self.setParameters([p1,p2,p3,p4])
	def setAvailableVariables(self,varlist):
		text = 'Avaliable variables: '
		i = 0
		for var in varlist:
			if (len(text)>50) and (i==0): 
				text += '\n'
				i += 1
			if (len(text)>100) and (i==1): 
				text += '\n'
				i += 1
			if (len(text)>150) and (i==2):
				text += '\n'
				i += 1
			if var!=varlist[-1]:
				text += '%s, '%(var)
			else:
				text += '%s.'%(var)
		self.variablesText.setText(text)
	def parameters(self):
		p1 = self.axStressBox.text()
		p2 = self.confStressBox.text()
		p3 = self.porePressBox.text()
		p4 = self.biotBox.value()
		return [p1,p2,p3,p4]
	def setParameters(self,parlist):
		self.axStressBox.setText(parlist[0])
		self.confStressBox.setText(parlist[1])
		self.porePressBox.setText(parlist[2])
		self.biotBox.setValue(parlist[3])

	def saveParameters(self):
		par = self.parameters()
		text = 'Parameters = {\n' +\
		'\'Axial stress\':\'%s\',\n'%(par[0]) +\
		'\'Confining pressure\':\'%s\',\n'%(par[1]) +\
		'\'Pore pressure\':\'%s\',\n'%(par[2]) +\
		'\'Biot coefficient\':%f,\n}'%(par[3])
		with open('EffectiveStressParameters.py','w') as f:
			f.write(text)
		self.hide()
	def cancel(self):
		p1 = Parameters['Axial stress']
		p2 = Parameters['Confining pressure']
		p3 = Parameters['Pore pressure']
		p4 = Parameters['Biot coefficient']
		self.setParameters([p1,p2,p3,p4])
		self.hide()



if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = EffectiveStressSettings()
	varlist = ['sig1','sigD','Pc','Pu','1'*20,'2'*20]
	w.setAvailableVariables(varlist)
	w.setParameters(['sig1','Pc','Pu',0.1])
	w.show()
	App.exec_()