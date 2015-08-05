# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np
import sys
from scipy.optimize import minimize as minimize
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from setupPlot import setup_plot

EnvelopeParameters = [
    {'name':'Cohesion', 'type':'float', 'value':300.0,'step':10.0},
    {'name':'Friction Angle', 'type':'float', 'value':30.0,'step':1.0},
]
LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}
CirclePen = pg.mkPen(color=(0,0,0), width=2)
EnvelopePen = pg.mkPen(color=(255,0,0), width=2)

class MohrCircles(QtGui.QWidget):
    def __init__(self):
    	"""
        Plots Morh's Circles for given datapoints
    	"""
        QtGui.QWidget.__init__(self)
        self.s1 = None
        self.s3 = None
        self.setGeometry(80, 30, 1000, 700)
        self.setupGUI()

    def plot(self):
        self.plt.clear()
        for i in range(self.ncircles):
            self.plt.plot(self.x[:,i],self.y[:,i], pen = CirclePen)
        self.plt.showGrid(x=True, y=True)
        self.plt.plot(self.env_x,self.env_y, pen = EnvelopePen)
        self.plt.setLabel('left', 'Shear Stress (psi)',**LabelStyle)
        self.plt.setLabel('bottom', 'Normal Stress (psi)',**LabelStyle)
        self.plt.setYRange(0, self.getMax())
    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        # layout is the main layout widget
        self.layout = QtGui.QVBoxLayout()
        # sublayout is a widget we add plot window to
        self.sublayout = pg.GraphicsLayoutWidget()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        # split window into two halfs
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.partree = ParameterTree(showHeader=False)
        self.splitter.addWidget(self.partree)
        self.splitter.addWidget(self.sublayout)
        self.plt = self.sublayout.addPlot()
        setup_plot(self.plt)
        pg.setConfigOptions(antialias=True)
        self.envelopeParameters = Parameter.create(name='params', type='group',
                                                   children=EnvelopeParameters)
        self.partree.setParameters(self.envelopeParameters,showTop=False)
        self.envelopeParameters.sigTreeStateChanged.connect(self.generateEnvelopeArray)

    def setData(self,sigma1,sigma3,npoints=1000):
        '''
        Eats 2 types of data: lists and nparrays
        '''
        if len(sigma1)!=len(sigma3): raise ValueError('Length of arrays must be the same')
        else: self.ncircles = len(sigma1)
        if isinstance(sigma1,list):
        	self.s1 = np.array(sigma1)
        	self.s3 = np.array(sigma3)
        else:
        	self.s1 = sigma1
        	self.s3 = sigma3
        self.npoints = npoints
        self.generateData()
        self.getEnvelope()
    def generateEnvelopeArray(self):
        frictionAngle = self.envelopeParameters.param('Friction Angle').value()
        cohesion = self.envelopeParameters.param('Cohesion').value()
        slope = np.tan(np.radians(frictionAngle))
        # print frictionAngle
        # self.env_x = np.linspace(0,self.getMax(),self.npoints)
        self.env_y = slope*self.env_x+cohesion
        self.plot()
    def getEnvelope(self):
        def computeNorm(params):
			slope = params[0]
			intersection = params[1]
			x0 = (slope*intersection + self.C)/(slope**2+1)
			y0 = slope*x0 + intersection
			norm = (abs((x0-self.C)**2 + y0**2 - self.R**2))**0.5
			# return sum(norm/self.R)
			return sum(norm)
        solution = minimize(computeNorm,x0=[0.36,100],
        # solution = minimize(computeNorm,x0=[0.1,100],
			method='Nelder-Mead',tol=1e-6,options={'maxiter':1000,'maxfev':10000})
        print solution
        slope = solution['x'][0]
        intersection = solution['x'][1]
        frictionAngle = np.degrees(np.arctan(slope))
        self.envelopeParameters.param('Friction Angle').setValue(frictionAngle)
        self.envelopeParameters.param('Cohesion').setValue(intersection)
        
	
    def generateData(self):
    	self.x = np.zeros((self.npoints,self.ncircles))
    	self.y = np.zeros((self.npoints,self.ncircles))
    	self.R = (self.s1 - self.s3)/2 # radii of mohr's circles
    	self.C = (self.s1 + self.s3)/2 # centers of mohr's circles
    	for i in range(self.ncircles):
    		self.x[:,i] = np.linspace(self.s3[i],self.s1[i],self.npoints)
    		self.y[:,i] = (self.R[i]**2-(self.x[:,i]-self.C[i])**2)**0.5
        self.env_x = np.linspace(0,self.getMax(),self.npoints) # envelope x array

    def getMax(self):
		return max(self.s1)

if __name__ == '__main__':
    sigma1 = [1000.,1500.,4000]
    sigma3 = [500.,700.,2000]
    McApp = QtGui.QApplication(sys.argv)
    win = MohrCircles()
    # win.setGeometry(80, 30, 1000, 700)
    win.setData(sigma1,sigma3)
    win.show()
    McApp.exec_()
