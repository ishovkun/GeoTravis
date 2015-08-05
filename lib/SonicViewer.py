# coding: UTF-8
import sys,os
import pyqtgraph as pg
import pickle
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
import numpy as np
from MultiLine import MultiLine
from functions import *
from Gradients import Gradients
from setupPlot import setup_plot
from TableWidget import TableWidget
from TriplePlotWidget import TriplePlotWidget
from GradientEditorWidget import GradientEditorWidget

xAxisName = 'Oscilloscope time (μs)'
fXAxisName = 'Frequency (MHz)'
phXAxisName = 'Phase (deg)'

Parameters = [
	{'name': 'Show', 'type': 'bool', 'value': True, 'tip': "Press to plot wave"},
	 {'name': 'Arrival times', 'type': 'group', 'children': [
            {'name': 'Mpoint', 'type': 'float', 'value': 10},
            {'name': 'BTA', 'type': 'int', 'value': 200},
            {'name': 'ATA', 'type': 'int', 'value': 5},
            {'name': 'DTA', 'type': 'int', 'value': 200},
        ]},
	]
WaveTypes = ['P','Sx','Sy']

LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}

class IdleWidget(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self,None)
	def plotSonicData(self):
		pass

class SonicViewer(QtGui.QWidget):
	'''
	Has 3 plots stored in dict plots={'P':,'Sx':,'Sy':}
	has 3 modifuing parameter trees to operate data:
	Shift - shift the data along x axis
	Amplify
	'''
	mode = 'Contours'
	autoShift = {'P':True,'Sx':True,'Sy':True} # flag to match 0 and transmission time
	arrivalsPicked = False
	updateQTable = True # don't need 
	def __init__(self,parent=None):
		self.parent = parent
		QtGui.QWidget.__init__(self,None,QtCore.Qt.WindowStaysOnTopHint)
		self.setupGUI()
		self.fWidget = TriplePlotWidget()
		self.phWidget = TriplePlotWidget()
		self.data = {'P':{},'Sx':{},'Sy':{}}
		self.currentShifts = {'P':0,'Sx':0,'Sy':0}
		self.connectPlotButtons()
		self.gEdit = GradientEditorWidget()
		self.gw = self.gEdit.sgw
		self.fgw = self.gEdit.fgw
		self.pgw = self.gEdit.pgw
		self.gw.restoreState(Gradients['hot'])
		self.fgw.restoreState(Gradients['hot'])
		self.pgw.restoreState(Gradients['hot'])
		self.allParameters = []
		self.yAxis = 'Track #'
		self.y = {}
		self.aTimes = {}
		self.showArrivalsButton.triggered.connect(self.parent.plotSonicData)
		self.pickArrivalsButton.triggered.connect(self.pickAllArrivals)
		self.invertYButton.triggered.connect(self.parent.plotSonicData)
		self.autoScaleButton.triggered.connect(self.autoScalePlots)
		self.editGradientsButton.triggered.connect(self.gEdit.show)
		self.gEdit.okButton.pressed.connect(self.parent.plotSonicData)
		self.showTableButton.triggered.connect(self.showTable)
		self.showForrierMagnitudeButton.triggered.connect(self.showFourrier)
		self.showForrierPhasesButton.triggered.connect(self.showPhases)
		# self.showArrivalsButton.triggered.connect(self.plot)
		self.waveFormButton.triggered.connect(lambda: self.setMode('WaveForms'))
		self.contourButton.triggered.connect(lambda: self.setMode('Contours'))
		for wave in WaveTypes:
			self.params[wave].param('Arrival times').param('Mpoint').sigValueChanged.connect(self.recomputeArrivals)
			self.params[wave].param('Arrival times').param('BTA').sigValueChanged.connect(self.recomputeArrivals)
			self.params[wave].param('Arrival times').param('ATA').sigValueChanged.connect(self.recomputeArrivals)
			self.params[wave].param('Arrival times').param('DTA').sigValueChanged.connect(self.recomputeArrivals)
	def setData(self,data):
		'''
		data is a dictionary with keys: P,Sx,Sy
		'''
		for wave in WaveTypes:
			self.data[wave] = data[wave]
		self.createTable()
		self.getFourrierTransforms()
		self.arrivalsPicked = False
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
		    self.y[wave] = np.arange(self.table[wave].shape[1])

	def showFourrier(self):
		self.fWidget.show()
		self.fWidget.activateWindow()
		self.parent.plotSonicData()
	def showPhases(self):
		self.phWidget.show()
		self.phWidget.activateWindow()
		self.parent.plotSonicData()
	def getFourrierTransforms(self):
		if not self.hasData(): return 0 # if no data pass
		print 'Building Fourrier matrix'
		self.fft = {} # power
		self.ph = {} # phase
		for wave in WaveTypes:
			x = self.table[wave][0,:,:]
			y = self.table[wave][1,:,:]
			N = y.shape[1]
			h = x[0,1] - x[0,0]
			# yf = np.fft.fft(y).real[:,:N/2]
			fft = np.fft.fft(y)[:,:N/2]
			yf = np.absolute(fft)
			yp = np.arctan2(fft.imag,fft.real)
			xf = np.fft.fftfreq(N,h)[:N/2]
			xf = np.tile(xf,y.shape[0])
			xf = xf.reshape(yf.shape[0],yf.shape[1])
			self.fft[wave] = np.array((xf,yf))
			self.ph[wave] = np.array((xf,yp))


	def connectPlotButtons(self):
		for wave in WaveTypes:
			self.params[wave].param('Show').sigValueChanged.connect(self.changeLayout)

	def changeLayout(self):
		print 'changing layout'
		for wave in WaveTypes:
			try:
				self.sublayout.removeItem(self.plots[wave])
				self.fWidget.sublayout.removeItem(self.fWidget.plots[wave])
			except:
				pass
		for wave in self.getActivePlots():
			if wave:
				self.sublayout.addItem(self.plots[wave])
				self.fWidget.sublayout.addItem(self.fWidget.plots[wave])
				self.sublayout.nextRow()
				self.fWidget.sublayout.nextRow()
	def autoScalePlots(self):
		for wave in self.getActivePlots():
			self.plots[wave].enableAutoRange()
	def getActivePlots(self):
		activePlots = []
		for wave in WaveTypes:
			val = self.params[wave].param('Show').value()
			if val: activePlots.append(wave)
		return activePlots
	def pickAllArrivals(self) :
		pBar = QtGui.QProgressDialog(None,QtCore.Qt.WindowStaysOnTopHint)
		pBar.setWindowTitle("Picking first arrivals")
		pBar.setAutoClose(True)
		pBar.show()
		pBar.activateWindow()
		progress = 0
		pBar.setValue(progress)
		for wave in WaveTypes:
			self.pickArrivals(wave)
			progress += 33
			pBar.setValue(progress)
		pBar.setValue(100)
		self.arrivalsPicked = True
		self.showArrivalsButton.setDisabled(False)
		self.showArrivalsButton.trigger()

	def plot(self,indices=None,yarray=None,yindices=None,
		amplify=None,yAxisName='Track #'):
		'''
		indices - number of sonic tracks to plot
		yarray - y values 
		yindices - indices of yarray to plot
		'''
		# print 1
		for wave in self.getActivePlots():
			plot = self.plots[wave]
			fplot = self.fWidget.plots[wave]
			phplot = self.phWidget.plots[wave]
			plot.clear(); fplot.clear(); phplot.clear();
			plot.getAxis('left').setLabel(yAxisName,**LabelStyle)
			plot.getAxis('bottom').setLabel(xAxisName,**LabelStyle)
			fplot.getAxis('left').setLabel(yAxisName,**LabelStyle)
			fplot.getAxis('bottom').setLabel(fXAxisName,**LabelStyle)
			phplot.getAxis('left').setLabel(yAxisName,**LabelStyle)
			phplot.getAxis('bottom').setLabel(fXAxisName,**LabelStyle)
			plot.enableAutoRange(enable=True)
			fplot.enableAutoRange(enable=True)
			phplot.enableAutoRange(enable=True)

		# print 2
		if self.mode == 'WaveForms':
			self.plotWaveForms(indices,amplify,yAxisName)
		elif self.mode == 'Contours':
			self.plotContours(indices,yarray,yindices,
			amplify,yAxisName)

		# print 3
		if self.fWidget.isVisible():
			if self.mode == 'WaveForms':
				self.plotDataWaveForms(self.fft,self.fWidget,
					indices,amplify,yAxisName)
			elif self.mode == 'Contours':
				self.plotDataContours(self.fft,
					self.fWidget, self.fgw,
					indices,yarray,yindices,
					amplify,yAxisName)
		# print 4
		if self.phWidget.isVisible():
			if self.mode == 'WaveForms':
				self.plotDataWaveForms(self.ph,self.pWidget,
					indices,amplify,yAxisName)
			elif self.mode == 'Contours':
				self.plotDataContours(self.ph,
					self.phWidget, self.pgw,
					indices,yarray,yindices,
					amplify,yAxisName)
		# print 5


		if self.showArrivalsButton.isChecked():
			self.plotArrivals(indices,yarray,yindices,
			amplify,yAxisName)

		# print 6
		
	def plotWaveForms(self,indices=None, amplify=None,yAxisName=''):
		self.graphicPaths = {}
		if (amplify is None):
			amp=np.average(np.abs(np.diff(self.y['P'])))
		for wave in self.getActivePlots():
			plot = self.plots[wave]
			if self.invertYButton.isChecked(): plot.invertY(True)
			else: plot.invertY(False)
			if indices: sind = indices[wave]
			else: sind = np.arange(self.table[wave].shape[1])
			Nlines = len(self.y[wave])
			y = amp*self.table[wave][1,sind,:] + self.y[wave].reshape(Nlines,1)
			# self.params[wave].param('Amplify').setValue(amp)
			if indices:
				self.graphicPaths[wave] = MultiLine(self.table[wave][0,sind,:],y)
			else:
				self.graphicPaths[wave] = MultiLine(self.table[wave][0,:,:],y)
			try:
				plot.addItem(self.graphicPaths[wave])
			except: pass


	def plotDataWaveForms(self,
		data,widget,indices=None, amplify=None,yAxisName=''):
		paths = {}
		amp=np.average(np.abs(np.diff(self.y['P'])))/data['P'].max()
		for wave in self.getActivePlots():
			plot = widget.plots[wave]
			if self.invertYButton.isChecked(): plot.invertY(True)
			else: plot.invertY(False)
			if indices: sind = indices[wave]
			else: sind = np.arange(data[wave].shape[1])
			Nlines = len(self.y[wave])
			y = amp*data[wave][1,sind,:] + self.y[wave].reshape(Nlines,1)
			if indices:
				paths[wave] = MultiLine(data[wave][0,sind,:],y)
			else:
				paths[wave] = MultiLine(data[wave][0,:,:],y)
			try:
				plot.addItem(paths[wave])
			except: pass
	def plotDataContours(self,data,widget,gw,
		indices=None,yarray=None,yindices=None,
		amplify=None,yAxisName=''):
		images = {}
		k = 0
		for wave in self.getActivePlots():
			plot = widget.plots[wave]
			if self.invertYButton.isChecked(): plot.invertY(True)
			else: plot.invertY(False)
			images[wave] = pg.ImageItem()
			if indices:
				z = data[wave][1,indices[wave],:].T
			else:
				z = data[wave][1,:,:].T
			if k == 0: lut = gw.getLookupTable(z.shape[0], alpha=None)
			images[wave].setImage(z)
			plot.addItem(images[wave])
			x = data[wave][0,0,:]
			shiftX0 = x[0]
			scaleX = (x[-1] - x[0])/x.shape[0]
			y = self.y[wave]
			ymax = y.max()
			ymin = y.min()
			shiftY0 = ymin
			scaleY = float(ymax - ymin)/y.shape[0]

			images[wave].translate(shiftX0,shiftY0)
			images[wave].scale(scaleX,scaleY)
			# set Colors
			images[wave].setLookupTable(lut, update=True)
			k += 1

	def plotContours(self,indices=None,yarray=None,yindices=None,
		amplify=None,yAxisName=''):
		self.images = {}
		k = 0
		for wave in self.getActivePlots():
			plot = self.plots[wave]
			if self.invertYButton.isChecked(): plot.invertY(True)
			else: plot.invertY(False)
			self.images[wave] = pg.ImageItem()
			if indices:
				z = self.table[wave][1,indices[wave],:].T
			else:
				z = self.table[wave][1,:,:].T
			if k == 0: lut = self.gw.getLookupTable(z.shape[0], alpha=None)
			self.images[wave].setImage(z)
			plot.addItem(self.images[wave])
			# scale and shift image
			x = self.table[wave][0,0,:]
			shiftX0 = x[0]
			scaleX = (x[-1] - x[0])/x.shape[0]

			y = self.y[wave]
			ymax = y.max()
			ymin = y.min()
			shiftY0 = ymin
			scaleY = float(ymax - ymin)/y.shape[0]

			self.images[wave].translate(shiftX0,shiftY0)
			self.images[wave].scale(scaleX,scaleY)
			# set Colors
			self.images[wave].setLookupTable(lut, update=True)
			k += 1

	def plotArrivals(self,indices=None,yarray=None,yindices=None,
		amplify=None,yAxisName='Track #'):
		try: 
			self.QTable.cellChanged.disconnect(self.editArrivals)
		except: pass
		tableLabels = get_list(yAxisName,WaveTypes)
		self.QTable.setHorizontalHeaderLabels(tableLabels)
		for wave in self.getActivePlots():
			k = WaveTypes.index(wave)
			if yarray is None:
				x = self.aTimes[wave]
				y = np.arange(self.aTimes[wave].shape[0])
			else: 
				ind = yindices[wave]
				sind = indices[wave]
				y = yarray[ind]
				x = self.aTimes[wave][sind]
			if self.updateQTable:
				self.QTable.setColumn(y,k)
				self.QTable.setColumn(x,k+3)
			plt = self.plots[wave]
			pen = pg.mkPen(color=(72,209,204), width=2)
			plt.plot(x,y,pen=pen)
		self.updateQTable = True
		self.QTable.cellChanged.connect(self.editArrivals)

	def setYAxisParameters(self,parameters):
		# we use setLimits because of weird implementation
		# in pyqtgraph
		self.allParameters = parameters
		self.yAxisMenu.clear()
		self.yAxisButtons = {}
		self.yAxisButtons['Track #'] = QtGui.QAction('Track #',self,checkable=True)
		self.yAxisButtons['Track #'].setActionGroup(self.yAxisGroup)
		self.yAxisMenu.addAction(self.yAxisButtons['Track #'])
		for p in parameters:
			if self.mode == 'Contours' and p!='Time': continue
			self.yAxisButtons[p] = QtGui.QAction(p,self,checkable=True)
			self.yAxisButtons[p].setActionGroup(self.yAxisGroup)
			self.yAxisMenu.addAction(self.yAxisButtons[p])
			pass
		try: 
			print 'Setting y axis to: Time'
			self.yAxisButtons['Time'].setChecked(True)
			self.yAxis = 'Time'
		except: print 'setting was not successful'

	def setMode(self,mode):
		'''
		takes string arguments: WaveForms and Contours
		'''
		self.mode = mode
		if mode == 'WaveForms':
			print 'Setting mode to Wave Forms'
			# self.modeMenu.setDefaultAction(self.waveFormButton)
		elif mode == 'Contours':
			print 'Setting mode to Contours'
			# self.modeMenu.setDefaultAction(self.contourButton)
		self.setYAxisParameters(self.allParameters)

	def setupGUI(self):
		self.setWindowTitle("Sonic Viewer")
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
		self.transformMenu = self.menuBar.addMenu('Transform')
		self.intMenu = self.menuBar.addMenu('Interpretation')
		# VIEW MENU
		self.autoScaleButton = QtGui.QAction('Auto scale',self)
		self.showArrivalsButton = QtGui.QAction('Arrivals',self,checkable=True)
		self.showArrivalsButton.setDisabled(True)
		self.showTableButton = QtGui.QAction('Table',self)
		self.yAxisMenu = self.viewMenu.addMenu('y axis')
		self.editGradientsButton = QtGui.QAction('Edit Gradients',self)
		self.invertYButton = QtGui.QAction('Invert y axis',self,checkable=True)
		
		self.viewMenu.addAction(self.autoScaleButton)
		self.viewMenu.addAction(self.showArrivalsButton)
		self.viewMenu.addAction(self.showTableButton)
		self.viewMenu.addAction(self.editGradientsButton)
		self.viewMenu.addAction(self.invertYButton)
		
		# MODE MENU
		self.modeGroup = QtGui.QActionGroup(self)
		self.waveFormButton = QtGui.QAction('Wave Forms',self,checkable=True)
		self.contourButton = QtGui.QAction('Contours',self,checkable=True)
		self.waveFormButton.setActionGroup(self.modeGroup)
		self.contourButton.setActionGroup(self.modeGroup)
		self.contourButton.setChecked(True)

		self.modeMenu.addAction(self.waveFormButton)
		self.modeMenu.addAction(self.contourButton)
		# INTERPRETATION MENU
		self.pickArrivalsButton = QtGui.QAction('Pick arrivals',self)
		self.moduliButton = QtGui.QAction('Elastic moduli',self)

		self.intMenu.addAction(self.pickArrivalsButton)
		self.intMenu.addAction(self.moduliButton)
		# TRANSFORM MENU
		self.showForrierMagnitudeButton = QtGui.QAction('Fourrier magnitude',self)
		self.showForrierPhasesButton = QtGui.QAction('Fourrier phases',self)
		self.transformMenu.addAction(self.showForrierMagnitudeButton)
		self.transformMenu.addAction(self.showForrierPhasesButton)
		# dict to store actions for y Axis
		self.yAxisButtons = {}
		self.yAxisGroup = QtGui.QActionGroup(self)
		self.yAxisButtons['Track #'] = QtGui.QAction('Track #',self,checkable=True)
		self.yAxisButtons['Track #'].setActionGroup(self.yAxisGroup)
		self.yAxisMenu.addAction(self.yAxisButtons['Track #'])
		self.yAxisButtons['Track #'].setChecked(True)

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

		self.params['Sx'].param('Arrival times').param('BTA').setValue(36)
		self.params['Sx'].param('Arrival times').param('ATA').setValue(5)
		self.params['Sx'].param('Arrival times').param('DTA').setValue(20)
		self.params['Sy'].param('Arrival times').param('BTA').setValue(100)
		self.params['Sy'].param('Arrival times').param('ATA').setValue(5)
		self.params['Sy'].param('Arrival times').param('DTA').setValue(30)
		# create table widget to show arrival times
		self.QTable = TableWidget(['Number P','Number Sx','Number Sy','P','Sx','Sy'])
		# self.splitter.addWidget(self.QTable)
		self.QTable.setColumnCount(6)
		self.QTable.hide()

		self.splitter.setSizes([int(self.width()*0.30),
                                    int(self.width()*0.35),
                                    int(self.width()*0.35)
                                ])
		self.splitter.setStretchFactor(0, 0)
		self.splitter.setStretchFactor(1, 1)
		self.splitter.setStretchFactor(2, 0)

	def pickArrivals(self,wave):
		print 'Computing arrival times for %s wave'%(wave)
		win = [0,0,0]
		mpoint = self.params[wave].param('Arrival times').param('Mpoint').value()
		win[0] = self.params[wave].param('Arrival times').param('BTA').value()
		win[1] = self.params[wave].param('Arrival times').param('ATA').value()
		win[2] = self.params[wave].param('Arrival times').param('DTA').value()
		x = self.table[wave][0,:,:]
		y = self.table[wave][1,:,:]
		h = x[0,1] - x[0,0]
		r = multi_window(y,win) 
		rx = np.arange(r.shape[1])*h + x[0,win[0]]
		mind = abs(rx-mpoint).argmin() #index of middle point
		sInd = r[:,:mind].argmax(axis=1) # sender indices
		sTimes = rx[sInd] # sender times
		rInd = r[:,mind:].argmax(axis=1) # receiver indices
		rTimes = rx[mind+rInd]
		self.aTimes[wave] = rTimes - sTimes
		# shift initial data so
		if self.autoShift[wave]:
			shift = np.mean(sTimes)
			self.table[wave][0,:,:] -= shift
			self.autoShift[wave] = False


	def editArrivals(self):
		data = self.QTable.getValues()
		indices = self.parent.trsIndices
		self.aTimes['P'][indices['P']] = data[:,3]
		self.aTimes['Sx'][indices['Sx']] = data[:,4]
		self.aTimes['Sy'][indices['Sy']] = data[:,5]
		self.updateQTable = False
		self.parent.plotSonicData()


	def recomputeArrivals(self):
		parent = self.sender().parent().parent().name()
		wave = parent.split()[0]
		self.pickArrivals(wave)
		self.parent.plotSonicData()

	def showTable(self):
		# show = self.showTableButton.isChecked()
		self.QTable.show()
		self.QTable.activateWindow()
	def closeEvent(self,event):
		QtGui.QWidget.closeEvent(self,event)
		self.fWidget.close()
		self.phWidget.close()
		

if __name__ == '__main__':
	SonicViewerApp = QtGui.QApplication(sys.argv)
	win = SonicViewer(parent=IdleWidget())
	win.setWindowTitle("Sonic Viewer")
	win.show()
	win.setGeometry(80, 30, 1000, 700)
	SonicViewerApp.exec_()