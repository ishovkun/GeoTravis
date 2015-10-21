import sys,os
import pyqtgraph as pg
# from pyqtgraph.Qt import QtGui, QtCore
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
import numpy as np
from MultiLine import MultiLine
from functions import *
from Gradients import Gradients
from setupPlot import setup_plot

xAxisName = 'Oscilloscope time (mus)'
Parameters = [
	{'name': 'Show', 'type': 'bool', 'value': True, 'tip': "Press to plot wave"},
	{'name':'Shift','type':'float','value':0.0,'dec':True,'minStep':'0.1'},
	{'name':'Amplify','type':'float','value':1.0,'step':0.1,'dec':True},
]
WaveTypes = ['P','Sx','Sy']

LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}


class SonicViewer(QtGui.QWidget):
	'''
	Has 3 plots stored in dict plots={'P':,'Sx':,'Sy':}
	has 3 modifuing parameter trees to operate data:
	Shift - shift the data along x axis
	Amplify
	'''
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setupGUI()
		self.data = {'P':{},'Sx':{},'Sy':{}}
		self.currentShifts = {'P':0,'Sx':0,'Sy':0}
		self.connectPlotButtons()
		self.mode = 'WaveForms'
		self.gw = pg.GradientEditorItem(orientation='right')
		self.gw.restoreState(Gradients['hot'])
		self.allParameters = []
		self.yAxis = 'Number of sonic track'
	def setData(self,data):
		for wave in WaveTypes:
			self.data[wave] = data[wave]
		self.createTable()
		self.connectShiftParameters()
	def hasData(self):
		'''
		check if the viewer has data to work with
		'''
		for wave in WaveTypes:
			if len(self.data[wave])>0: return True
		return False
	def createTable(self):
		'''
		store all data in one 3D np-array
		1st dimension - time or amplitude
	    2nd dimension - number of file
	    3rd dimension - datapoints
		'''
		if not self.hasData(): return 0 # if no data pass
		print 'Building sonic matrix'
		self.table = {}
		for wave in WaveTypes:
		    self.table[wave] = get_table(self.data[wave])

	def connectPlotButtons(self):
		for wave in WaveTypes:
			self.params[wave].param('Show').sigValueChanged.connect(self.changeLayout)

	def changeLayout(self):
		print 'changing layout'
		for wave in WaveTypes:
			try:
				self.sublayout.removeItem(self.plots[wave])
			except:
				pass
		for wave in self.getActivePlots():
			if wave:
				self.sublayout.addItem(self.plots[wave])
				self.sublayout.nextRow()
	def autoScalePlots(self):
		for wave in self.getActivePlots():
			self.plots[wave].enableAutoRange()
	def shiftPlot(self,wave):
		newshift = self.params[wave].param('Shift').value()
		oldshift = self.currentShifts[wave]
		if self.mode == 'WaveForms':
			self.graphicPaths[wave].translate(newshift-oldshift,0)
		elif self.mode == 'Contours':
			self.images[wave].translate(newshift-oldshift,0)
		self.currentShifts[wave] = newshift
	def getActivePlots(self):
		activePlots = []
		for wave in WaveTypes:
			val = self.params[wave].param('Show').value()
			if val: activePlots.append(wave)
		return activePlots
	 
	def plot(self,indices=None,yarray=None,yindices=None,
			amplify=None,yAxisName=''):
		if self.mode == 'WaveForms':
			self.plotWaveForms(indices,yarray,yindices,
			amplify,yAxisName)
		elif self.mode == 'Contours':
			self.plotContours(indices,yarray,yindices,
			amplify,yAxisName)
		
	def plotWaveForms(self,indices=None,yarray=None,yindices=None,
			amplify=None,yAxisName=''):
		self.graphicPaths = {}
		if (amplify is None) & (yarray is not None):
			amp=np.average(np.abs(np.diff(yarray[yindices['P']])))
		for wave in self.getActivePlots():
			shift = self.params[wave]['Shift']
			plot = self.plots[wave]
			plot.clear()
			plot.getAxis('left').setLabel(yAxisName,**LabelStyle)
			plot.getAxis('bottom').setLabel(xAxisName,**LabelStyle)
			plot.enableAutoRange(enable=True)
			plot.showButtons()
			if yarray is None:
				Nlines = self.table[wave].shape[1]
				y = np.arange(Nlines).reshape(Nlines,1)
				y = self.table[wave][1,:,:] + y
			else: 
				ind = yindices[wave]
				sind = indices[wave]
				Nlines = len(ind)
				# print self.table[wave].shape
				# print sind.shape
				# print yarray[ind].shape
				y = amp*self.table[wave][1,sind,:] + yarray[ind].reshape(Nlines,1)
				self.params[wave].param('Amplify').setValue(amp)
			if indices:
				self.graphicPaths[wave] = MultiLine(self.table[wave][0,sind,:],y)
			else:
				self.graphicPaths[wave] = MultiLine(self.table[wave][0,:,:],y)
			try:
				self.graphicPaths[wave].translate(shift,0)
				plot.addItem(self.graphicPaths[wave])
			except: pass
	def plotContours(self,indices=None,yarray=None,yindices=None,
			amplify=None,yAxisName=''):
		self.images = {}
		k = 0
		for wave in self.getActivePlots():
			shift = self.params[wave]['Shift']
			plot = self.plots[wave]
			plot.clear()
			plot.getAxis('left').setLabel(yAxisName,**LabelStyle)
			plot.getAxis('bottom').setLabel(xAxisName,**LabelStyle)
			plot.enableAutoRange(enable=True)
			self.images[wave] = pg.ImageItem()
			if indices:
				z =self.table[wave][1,indices[wave],:].T
			else:
				z =self.table[wave][1,:,:].T
			if k == 0: lut = self.gw.getLookupTable(z.shape[0], alpha=None)
			self.images[wave].setImage(z)
			plot.addItem(self.images[wave])
			# scale and shift image
			x = self.table[wave][0,0,:]
			shiftX0 = x[0]
			scaleX = (x[-1] - x[0])/x.shape[0]
			if yarray is not None:
				if yindices:
					y = yarray[yindices[wave]]
				else:
					y = yarray
				ymax = y.max()
				ymin = y.min()
				shiftY0 = ymin
				nbpts = len(y)
				scaleY = (ymax - ymin)/nbpts
			else: 
				scaleY = 1
				shiftY0 = 0
			self.images[wave].translate(shiftX0,shiftY0)
			shift = self.params[wave]['Shift']
			self.images[wave].translate(shift,0)
			self.images[wave].scale(scaleX,scaleY)
			# set Colors
			self.images[wave].setLookupTable(lut, update=True)
			k += 1
			

	def setYAxisParameters(self,parameters):
		# we use setLimits because of weird implementation
		# in pyqtgraph
		self.allParameters = parameters
		self.yAxisMenu.clear()
		self.yAxisButtons = {}
		self.yAxisButtons['Number of sonic track'] = QtGui.QAction('Number of sonic track',self)
		self.yAxisMenu.addAction(self.yAxisButtons['Number of sonic track'])
		for p in parameters:
			if self.mode == 'Contours' and p!='Time': continue
			self.yAxisButtons[p] = QtGui.QAction(p,self)
			self.yAxisMenu.addAction(self.yAxisButtons[p])
			pass
		try: 
			print 'Setting y axis to: Time'
			self.yAxisMenu.setDefaultAction(self.yAxisButtons['Time'])
			self.yAxis = 'Time'
		except: print 'setting was not successful'
	def connectShiftParameters(self):
		try:
			self.params['P'].param('Shift').sigValueChanged.disconnect(lambda: self.shiftPlot('P'))
			self.params['Sx'].param('Shift').sigValueChanged.disconnect(lambda: self.shiftPlot('Sx'))
			self.params['Sy'].param('Shift').sigValueChanged.disconnect(lambda: self.shiftPlot('Sy'))
		except: pass
		self.params['P'].param('Shift').sigValueChanged.connect(lambda: self.shiftPlot('P'))
		self.params['Sx'].param('Shift').sigValueChanged.connect(lambda: self.shiftPlot('Sx'))
		self.params['Sy'].param('Shift').sigValueChanged.connect(lambda: self.shiftPlot('Sy'))
	def setMode(self,mode):
		'''
		takes string arguments: WaveForms and Contours
		'''
		self.mode = mode
		if mode == 'WaveForms':
			print 'Setting mode to Wave Forms'
			self.modeMenu.setDefaultAction(self.waveFormButton)
		elif mode == 'Contours':
			print 'Setting mode to Contours'
			self.modeMenu.setDefaultAction(self.contourButton)
		self.setYAxisParameters(self.allParameters)

	def setupGUI(self):
		self.setWindowTitle("Sonic Viewer")
		self.setWindowIcon(QtGui.QIcon('../images/Logo.png'))    
		pg.setConfigOption('background', (255,255,255))
		pg.setConfigOption('foreground',(0,0,0))
		self.layout = QtGui.QVBoxLayout()
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setSpacing(0)
		self.setLayout(self.layout)
		## setting up the menu bar
		self.menuBar = QtGui.QMenuBar()
		self.layout.setMenuBar(self.menuBar)
		self.viewMenu = self.menuBar.addMenu('View')
		self.modeMenu = self.menuBar.addMenu('Mode')
		self.autoScaleButton = QtGui.QAction('Auto scale',self)
		self.viewMenu.addAction(self.autoScaleButton)
		self.autoScaleButton.triggered.connect(self.autoScalePlots)
		self.yAxisMenu = self.viewMenu.addMenu('y axis')
		# 'Number of sonic track'
		self.waveFormButton = QtGui.QAction('Wave Forms',self)
		self.contourButton = QtGui.QAction('Contours',self)

		self.modeMenu.addAction(self.waveFormButton)
		self.modeMenu.addAction(self.contourButton)
		self.modeMenu.setDefaultAction(self.waveFormButton)
		# dict to store actions for y Axis
		self.yAxisButtons = {}
		self.yAxisButtons['Number of sonic track'] = QtGui.QAction('Number of sonic track',self)
		self.yAxisMenu.addAction(self.yAxisButtons['Number of sonic track'])
		self.yAxisMenu.setDefaultAction(self.yAxisButtons['Number of sonic track'])
		# for wave in WaveTypes:
		# split main widget into plotting area and parameters area
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		self.splitter.setOrientation(QtCore.Qt.Horizontal)
		self.layout.addWidget(self.splitter)
		# split parameter area into 3 for each wave
		self.treeSplitter = QtGui.QSplitter()
		self.treeSplitter.setOrientation(QtCore.Qt.Vertical)
		self.splitter.addWidget(self.treeSplitter)
		# create parameter trees
		self.trees={}
		for wave in WaveTypes:
			self.trees[wave] = ParameterTree(showHeader=False)
			self.treeSplitter.addWidget(self.trees[wave])
		# create layout for the plotting area
		self.sublayout = pg.GraphicsLayoutWidget()
		self.splitter.addWidget(self.sublayout)
		self.params = {}
		self.plots = {}
		for wave in WaveTypes:
			# create parameter instances
			self.params[wave] = Parameter.create(name=wave + ' wave',
				type='group',children=Parameters)
			self.trees[wave].setParameters(self.params[wave],showTop=True)
			# fill plotting area with 3 plots
			self.plots[wave] = self.sublayout.addPlot()
			setup_plot(self.plots[wave])
			self.sublayout.nextRow()
		self.splitter.setSizes([int(self.width()*0.20),
                                    int(self.width()*0.80),
                                    20])
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)



if __name__ == '__main__':
    SonicViewerApp = QtGui.QApplication(sys.argv)
    win = SonicViewer()
    win.setWindowTitle("Sonic Viewer")
    win.show()
    win.setGeometry(80, 30, 1000, 700)
    SonicViewerApp.exec_()