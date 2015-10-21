# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from CParameterTree import ColorButton
from functions import findInDict
from setupPlot import setup_plot

CoulumbText = 'Mohr - Coulomb'
HoekText = 'Hoek - Brown'
NoteText = """
<sub></sub>
Note:
<BR>
Mohr-Coulumb criterion:
<BR>
&tau; = C + &sigma;<sub>n</sub> sin &phi;
<BR>
Hoek-Brown Criterion:
<BR>
&sigma;<sub>1</sub> = 
	&sigma;<sub>3</sub> + 
	&radic;(
		m UCS &sigma;<sub>3</sub> + 
		UCS<sup>2</sup>
		)
"""

class EditEnvelopeWidget(QtGui.QMainWindow):
	def __init__(self):
		super(EditEnvelopeWidget,self).__init__()
		self.setupGUI()
	def setupGUI(self):
		self.setWindowTitle("Edit envelope options")
		self.setGeometry(500, 300, 400, 100)
		self.centralWidget = QtGui.QWidget()
		self.setCentralWidget(self.centralWidget)
		self.centralLayout = QtGui.QVBoxLayout()
		self.centralWidget.setLayout(self.centralLayout)
		self.groupBox = QtGui.QGroupBox("Criterion type")

		self.nameWidget = QtGui.QWidget()
		self.buttonsWidget = QtGui.QWidget()
		self.centralLayout.setContentsMargins(5,10,5,0)
		# set up button layout
		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonsWidget.setLayout(self.buttonLayout)
		self.okButton = QtGui.QPushButton("OK")
		self.cancelButton = QtGui.QPushButton("Cancel")

		self.buttonLayout.addWidget(self.okButton)
		self.buttonLayout.addWidget(self.cancelButton)
		self.buttonLayout.setContentsMargins(0,0,0,5)
		# set up name layout
		self.nameLayout = QtGui.QHBoxLayout()
		self.nameWidget.setLayout(self.nameLayout)
		typeLabel = QtGui.QLabel('Title')
		self.nameBox = QtGui.QLineEdit()
		self.nameLayout.addWidget(typeLabel)
		self.nameLayout.addWidget(self.nameBox)

		self.coulumbButton = QtGui.QRadioButton(CoulumbText,self)
		# print self.coulumbButton.label
		self.brownButton = QtGui.QRadioButton(HoekText,self)
		noteLable = QtGui.QLabel(NoteText)
		self.coulumbButton.setChecked(True)

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.coulumbButton)
		vbox.addWidget(self.brownButton)
		vbox.addWidget(noteLable)
		vbox.addStretch(1)
		self.groupBox.setLayout(vbox)


		self.centralLayout.addWidget(self.groupBox)
		self.centralLayout.addWidget(self.nameWidget)
		self.centralLayout.addWidget(self.buttonsWidget)

		self.okButton.clicked.connect(self.ok)
		self.cancelButton.clicked.connect(self.hide)

	def setDefaultName(self,name='Untitled'):
		self.nameBox.setText(name)

	def value(self):
		value1 = self.coulumbButton.isChecked()
		value2 = self.brownButton.isChecked()
		if value1 == True: return 'Coulomb'
		elif value2 == True: return 'Brown'

	def ok(self):
		# print self.value()
		return self.value()

if __name__ == '__main__':
	App = QtGui.QApplication(sys.argv)
	w = EditEnvelopeWidget()
	# w.setDefaultName('Igor')
	w.show()
	App.exec_()