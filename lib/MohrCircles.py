# -*- coding: utf-8 -*-
'''
WARNING:
PRESSING 'CANCEL' BUTTON DOESN'T CLOSE THE APPLICATION
USE X BUTTON INSTEAD
(THIS IS ONLY IMPORTANT FOR RUNNING THIS WIDGET 
    AS A STANDALONE)
'''

import pyqtgraph as pg
import numpy as np
import sys
from scipy.optimize import curve_fit
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from setupPlot import setup_plot
from CParameterTree import ColorButton,CheckBox
from EditEnvelopeWidget import EditEnvelopeWidget

EnvelopeParameters = [
    {'name':'Cohesion', 'type':'float', 'value':300.0,'step':10.0},
    {'name':'Friction Angle', 'type':'float', 'value':30.0,'step':1.0},
]
LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}
CirclePen = pg.mkPen(color=(0,0,0), width=2)
EnvelopePen = pg.mkPen(color=(255,0,0), width=2)
rand = lambda: np.random.rand()
get_color = lambda: (rand()*230,rand()*230,rand()*230)

def hoek_brown(x,m,ucs):
    return x + (m*ucs*x + ucs**2)**0.5
def morh_coulomb(x,a,b):
    return a*x + b
def hoek_on_mohr_plane(s3,m,ucs):
    '''
    s3 = sigma3
    returns sigma_n, tau
    '''
    ds1ds3 = 1. + m*ucs/2/(m*ucs*s3 + ucs**2)**0.5
    s1 = hoek_brown(s3,m,ucs)
    # sigma n
    sn = s3 + (s1 - s3)/(ds1ds3 + 1.)
    # tau
    t = (s1-s3)*ds1ds3**0.5/(ds1ds3 + 1.)
    return sn,t

class MohrCircles(QtGui.QWidget):
    def __init__(self):
    	"""
        Plots Morh's Circles for given datapoints
    	"""
        QtGui.QWidget.__init__(self)
        self.s1 = []
        self.s3 = []
        self.nData = 0
        self.nEnvelopes = 0
        self.dCButtons = {}
        self.eCButtons = {}
        self.eBoxes = {}
        self.dNames = [] # names of Datasets
        self.eNames = [] # envelope names
        self.eTypes = {} # envelope types
        self.fBoxes = {} # boxes with friction angle values
        self.cBoxes = {} # boxes with cohesion values
        self.eItemNames = [] # item names inside envelope menus
        self.setupGUI()
        self.edit = EditEnvelopeWidget()
        self.addEnvelopeButton.clicked.connect(self.callEditWidget)
        self.edit.okButton.clicked.connect(self.callAddEnvelope)

    def callEditWidget(self):
        name = 'Env_%d'%(self.nEnvelopes)
        self.edit.setDefaultName(name)
        self.edit.show()
        self.edit.activateWindow()
    def callAddEnvelope(self):
        name = self.edit.nameBox.text()
        self.addEnvelope(etype=self.edit.value(),name=name)
        self.edit.hide()
    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        self.setWindowIcon(QtGui.QIcon('../images/Logo.png')) 
        self.setGeometry(80, 30, 1000, 700)
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

        self.tree = pg.TreeWidget()
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.sublayout)
        self.plt = self.sublayout.addPlot()
        setup_plot(self.plt)
        pg.setConfigOptions(antialias=True)

        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(False)
        self.tree.setIndentation(10)
        self.tree.setColumnCount(4)
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 20)
        self.tree.setColumnWidth(2, 90)
        self.tree.setColumnWidth(3, 50)
        # self.tree.setColumnWidth(3, 50)
        self.fpoints = pg.TreeWidgetItem(['Failure Points'])
        self.envelopes = pg.TreeWidgetItem(['Failure Envelopes'])
        self.tree.addTopLevelItem(self.fpoints)
        self.tree.addTopLevelItem(self.envelopes)
        self.tree.setDragEnabled(False)
        self.fpoints.setExpanded(True)
        self.envelopes.setExpanded(True)
        addEnvelopeItem = pg.TreeWidgetItem([''])
        self.tree.addTopLevelItem(addEnvelopeItem)
        self.addEnvelopeButton = QtGui.QPushButton('Add Envelope')
        addEnvelopeItem.setWidget(0,self.addEnvelopeButton)
        

    def addData(self,s1,s3,name=None):
        if name is None:
            name = 'Untitled_%d'%(self.nData)
        self.s1.append(s1)
        self.s3.append(s3)
        item = pg.TreeWidgetItem([name])
        self.dNames.append(name)
        self.fpoints.addChild(item)
        # self.tree.addTopLevelItem(item)
        color = (0,0,0)
        colorButton = ColorButton()
        item.setWidget(2,colorButton)
        self.dCButtons[name] = colorButton
        colorButton.setColor(color)
        colorButton.sigColorChanged.connect(self.plot)
        self.nData += 1
    def start(self):
        '''
        all the data is loaded 
        and it's time to work
        '''
        self.generateCircles()
        self.addEnvelope()
    def addEnvelope(self,etype='Coulomb',name='Env'):
        item = pg.TreeWidgetItem([name])
        self.envelopes.addChild(item)
        self.eNames.append(name)
        self.eTypes[name] = etype
        typeLabel = QtGui.QLabel(etype)
        item.setWidget(2,typeLabel)
        colorButton = ColorButton()
        self.eCButtons[name] = colorButton
        color = get_color()
        colorButton.setColor(color)
        item.setExpanded(True)
        self.eBoxes[name] = {}
        colorItem = pg.TreeWidgetItem(['Color'])
        if etype == 'Coulomb':
            item1 = pg.TreeWidgetItem(['Friction Angle'])
            item2 = pg.TreeWidgetItem(['Cohesion'])
            step1 = 1
            step2 = 50
        elif etype == 'Brown':
            item1 = pg.TreeWidgetItem(['m'])
            item2 = pg.TreeWidgetItem(['UCS'])
            step1 = 1
            step2 = 1
        else:
            print etype
            return 0
        item.addChild(colorItem)
        item.addChild(item1)
        item.addChild(item2)
        frictionBox = pg.SpinBox(value=50, step=step1)
        cohesionBox = pg.SpinBox(value=1e3, step=step2)
        frictionBox.sigValueChanged.connect(self.plot)
        cohesionBox.sigValueChanged.connect(self.plot)
        colorItem.setWidget(2,colorButton)
        item1.setWidget(2,frictionBox)
        item2.setWidget(2,cohesionBox)
        self.fBoxes[name] = frictionBox
        self.cBoxes[name] = cohesionBox
        for dname in self.dNames:
            child = pg.TreeWidgetItem([dname])
            item.addChild(child)
            box = CheckBox()
            child.setWidget(2,box)
            self.eBoxes[name][dname] = box
            box.click()
            box.clicked.connect(lambda:self.getEnvelope(name))
        removeEnvelopeItem = pg.TreeWidgetItem([''])
        item.addChild(removeEnvelopeItem)
        removeButton = QtGui.QPushButton('Remove')
        removeEnvelopeItem.setWidget(2,removeButton)
        removeButton.clicked.connect(lambda:self.removeEnvelope(item))
        colorButton.sigColorChanged.connect(self.plot)
        self.nEnvelopes += 1
        self.getEnvelope(eName=name)
    def removeEnvelope(self,envelope):
        '''
        removes Current Envelopes
        '''
        name = envelope.text(0)
        index = self.envelopes.indexOfChild(envelope)
        self.envelopes.takeChild(index)
        del self.eBoxes[name],self.eCButtons[name]
        del self.cBoxes[name],self.fBoxes[name]
        self.eNames.pop(index)
        self.plot()
    def getEnvelope(self,eName=None):
        if eName == None: eName = self.eNames[0]
        etype = self.eTypes[eName]
        s1 = []
        s3 = []
        for dName in self.dNames:
            val = self.eBoxes[eName][dName].value()
            if val:
                index = self.dNames.index(dName)
                s1.append(self.s1[index])
                s3.append(self.s3[index])
        if len(s1)==1:
            s1.append(500)
            s3.append(0)
        if (s1!=[]) and (s3!=[]):
            par1,par2 = self.computeEnvelope(s1,s3,etype)
            self.fBoxes[eName].setValue(par1)
            self.cBoxes[eName].setValue(par2)
    def computeEnvelope(self,s1,s3,etype='Coulomb'):
        s1 = np.array(s1)
        s3 = np.array(s3)
        if etype == 'Coulomb':
            popt, pcov = curve_fit(morh_coulomb,
             s3, s1,maxfev=int(1e5))
            a = popt[0]; b = popt[1]
            phi = np.arcsin((a-1.)/(a+1.))        
            cohesion = b/(2*np.cos(phi))*(1-np.sin(phi))
            angle = np.degrees(phi)
            return angle,cohesion
        elif etype == 'Brown':
            popt, pcov = curve_fit(hoek_brown,
             s3, s1,maxfev=int(1e5))
            return popt[0],popt[1]
        

    def generateCircles(self,npoints=1e4):
        self.s1 = np.array(self.s1)
        self.s3 = np.array(self.s3)
        self.centers = (self.s1 + self.s3)/2
        self.radii = abs(self.s1 - self.s3)/2
        # x and y of Mohr's circles
        self.x = {}
        self.y = {}
        self.env_x = {}
        for i in range(len(self.dNames)):
            R = self.radii[i]
            C = self.centers[i]
            x = np.linspace(self.s3[i],self.s1[i],npoints)
            self.x[self.dNames[i]] = x
            self.y[self.dNames[i]] = (R**2-(x-C)**2)**0.5
        minstess = min(np.minimum(self.s1,self.s3))
        maxstess = max(np.maximum(self.s1,self.s3))
        self.env_x = np.linspace(min(0,minstess),maxstess,npoints)

    def plot(self):
        self.plt.clear()
        self.plt.showGrid(x=True, y=True)
        self.plt.setYRange(0,max(self.s1))
        self.plt.setXRange(self.env_x.min(),self.env_x.max())
        for dName in self.dNames:
            color = self.dCButtons[dName].color()
            pen = pg.mkPen(color=color, width=2)
            self.plt.plot(self.x[dName],self.y[dName],pen=pen)
        for eName in self.eNames:
            color = self.eCButtons[eName].color()
            pen = pg.mkPen(color=color, width=2)
            a = self.fBoxes[eName].value()
            b = self.cBoxes[eName].value()
            x = self.env_x
            if self.eTypes[eName]=='Coulomb':
                tan_phi = np.tan(np.radians(a))
                y = tan_phi*x + b
            elif self.eTypes[eName]=='Brown':
                x,y = hoek_on_mohr_plane(x,a,b)

            self.plt.plot(x,y,pen=pen)

if __name__ == '__main__':
    sigma1 = 1100
    sigma3 = 100
    McApp = QtGui.QApplication(sys.argv)
    win = MohrCircles()
    win.addData(0,-300)
    win.addData(sigma1,sigma3)
    win.addData(sigma1*2,sigma3*2)
    win.start()
    win.show()
    McApp.exec_()
    

