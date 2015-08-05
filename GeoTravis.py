# coding: UTF-8
## For build
# from pyqtgraphBundleUtils import *
# from pyqtgraph import setConfigOption
# setConfigOption('useOpenGL', False)
###############
#!/usr/bin/env python

import sys,os
# sys.path.append('dataviewer_lib') # comment this line on build and put files from the lib directly to the same folder
import pyqtgraph as pg
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
import numpy as np

import pickle

# from copy import copy,deepcopy
from dataviewer import DataViewer
from lib.readtrc import read_TRC
from lib.MultiLine import MultiLine
from lib.SonicViewer import SonicViewer
from lib.functions import *

WaveTypes = ['P','Sx','Sy']

BadBindingMessage = '''
Duplicates found in the comments column.
This is bad. I will do my best to 
square things away, but don't rely on me.
'''

class GeoTravis(DataViewer):
    """docstring for ClassName"""
    def __init__(self):
        super(GeoTravis, self).__init__()
        self.SViewer = SonicViewer(self)
        # self.SViewer.setWindowIcon(QtGui.QIcon('images/Logo.png'))
        # dict for sonic data
        self.sonicData = {'P':{},'Sx':{},'Sy':{}}
        self.trSonicNames = {'P':{},'Sx':{},'Sy':{}}
        self.allSonicData = {}
        self.allComments = {}
        # indices in geo data corresponding to sonic times within truncated interval
        self.gsIndices = {}

    def setupGUI(self):
        print 'Setting up GUI'
        super(GeoTravis, self).setupGUI()
        self.setWindowTitle('GeoTravis')
        self.fileMenu.clear()
        self.loadSonicButton = QtGui.QAction('Load sonic data',self)
        self.loadSonicButton.triggered.connect(self.loadSonicData)
        self.fileMenu.addAction(self.loadButton)
        self.fileMenu.addAction(self.loadSonicButton)
        self.fileMenu.addAction(self.saveButton)
        self.fileMenu.addAction(self.exitButton)
        # we connect sonic button now since but don't show it yet
        self.showSonicButton = QtGui.QAction('Sonic',self,shortcut='Alt+S')
        self.showSonicButton.setDisabled(True)
        self.viewMenu.addAction(self.showSonicButton)
        # self.sonicMenu.addAction(self.showSonicButton)
        self.showSonicButton.triggered.connect(self.showSonicData)
        self.pBar = QtGui.QProgressDialog()
        self.pBar.setWindowTitle("Loading sonic data")
        self.pBar.setAutoClose(True)

    def loadSonicData(self):
        '''
        When 'Load sonic data' button is pressed,
        opens a file dialog which enables of loading multiple files
        saves data from those files into three variables
        '''
        # print 'Loading sonic data'
        self.setStatus('Loading sonic data')
        # reset sonic data
        self.sonicData = {'P':{},'Sx':{},'Sy':{}}

        self.lastdir = self.checkForLastDir()
        caption = 'Open file'
        # use current/working directory
        # directory = './'
        filter_mask = "Sonic data files (*.TRC *.txt)"
        filenames = QtGui.QFileDialog.getOpenFileNames(None,
            caption, "%s"%(self.lastdir), filter_mask)[0]
        Nfiles = len(filenames)
        self.pBar.show()
        i = 0.
        for pathToFile in filenames:
            directory = os.path.split(pathToFile)[0]
            filename = os.path.split(pathToFile)[1]
            if '.TRC' in filename:
                if 'P'  in filename:
                    pwaves = read_TRC(directory +'\\'+ filename)
                    self.sonicData['P'][filename] = pwaves
                elif 'Sx' in filename:
                    sxwaves = read_TRC(directory +'\\' + filename)
                    self.sonicData['Sx'][filename] = sxwaves
                elif 'Sy' in filename:
                    sywaves = read_TRC(directory +'\\' + filename)
                    self.sonicData['Sy'][filename] = sywaves
                else: print ('wierd filename')
            else: print ('wrong datatype')
            self.pBar.setValue(i/Nfiles*100)
            i += 1
        self.setStatus('Ready')
        self.pBar.setValue(100)
        self.pBar.hide()

        # Associate sonic data with a geomechanic experiment data
        #
        self.disconnectSonicViewer()
        self.SViewer.setData(self.sonicData)
        if self.currentDataSetName:
            self.bindSonicTable()
            self.SViewer.setYAxisParameters(self.data.keys())
            self.connectYAxisParameters()
        self.SViewer.showArrivalsButton.setChecked(False)
        self.connectSonicViewer()
        self.enableSonicButton()
        self.plotSonicData()

    def connectYAxisParameters(self):
        for p in self.SViewer.yAxisButtons.keys():
            self.SViewer.yAxisButtons[p].triggered.connect(self.setSonicViewerYAxis)
        # self.SViewer.showArrivalsButton.triggered.connect(self.plotSonicData)


    def disconnectYAxisParameters(self):
        for p in self.SViewer.yAxisButtons.keys():
            self.SViewer.yAxisButtons[p].triggered.disconnect()
        # self.SViewer.showArrivalsButton.triggered.disconnect(self.plotSonicData)

    def setSonicViewerYAxis(self):
        # sender is a button, which sent the signal
        sender = self.sender()
        parameter = sender.text()
        print 'Setting y axis to: %s'%(parameter)
        button = self.SViewer.yAxisButtons[parameter]
        self.SViewer.yAxis = parameter
        self.plotSonicData()

    def connectParameters(self):
        '''
        inherited method.
        lines added to connect slider to range of 
        wave tracks 
        '''
        super(GeoTravis, self).connectParameters()
        self.slider.sigGradientChanged.connect(self.truncateSonicData)

    def setCurrentDataSet(self,name):
        '''
        Method inherited from dataviewer class. subject to 
        some changes
        '''
        if self.currentDataSetName: # save old sonic data and comments
            print 'Saving old Sonic Data'
            self.allSonicData[self.currentDataSetName] = self.sonicData
        super(GeoTravis, self).setCurrentDataSet(name)
        print 'Setting Sonic Data'
        try:
            self.sonicData = self.allSonicData[name]
            self.SViewer.currentShifts = {'P':0,'Sx':0,'Sy':0}
            print 'Found sonic data for the current data set'
        except: 
            print 'No sonic data for the current data set found'
            self.sonicData = {'P':{},'Sx':{},'Sy':{}}
            self.SViewer.currentShifts = {'P':0,'Sx':0,'Sy':0}
        self.SViewer.setData(self.sonicData)
        self.enableSonicButton()
        self.disconnectSonicViewer()
        if self.SViewer.hasData(): 
            self.createSonicTable()
            self.bindSonicTable()
            self.SViewer.setYAxisParameters(self.data.keys())
            self.connectYAxisParameters()
            self.connectSonicViewer()
            self.plotSonicData()

    def setSonicViewerMode(self,mode):
        print 'Connecting sonic viewer interface'
        self.SViewer.setMode(mode)
        self.connectYAxisParameters()
        self.plotSonicData()

    def disconnectSonicViewer(self):
        try:
            print 'Disconnecting sonic viewer interface'
            self.SViewer.waveFormButton.triggered.disconnect()
            self.SViewer.contourButton.triggered.disconnect()
        except: 
            pass
    def connectSonicViewer(self):
        self.SViewer.waveFormButton.triggered.connect(lambda: self.setSonicViewerMode('WaveForms'))
        self.SViewer.contourButton.triggered.connect(lambda: self.setSonicViewerMode('Contours'))
    def truncateSonicData(self):
        '''
        truncate sonic times for each wave, then get indices 
        from sonic table
        '''
        if self.SViewer.hasData():
            self.gsIndices = {}
            interval = self.getSliderState()
            for wave in WaveTypes:
                # Indices of geom data corresponding to sonic output
                #
                time = self.data['Time'][self.sindices[wave]]

                # Get indices of geomechanical data for the time interval
                #
                mask = (time>=interval[0]) & (time<=interval[1])
                self.gsIndices[wave] = self.sindices[wave][mask]

                # Get indices of sonic data for the time interval
                #
                mask = (self.sTimes[wave] >= interval[0]) & (self.sTimes[wave] <= interval[1])
                self.trsIndices[wave] = np.where(mask)[0]
                # self.trsIndices[wave] = self
            self.plotSonicData()
    def createSonicTable(self):
        '''
        create 3D arrays for each wave to better store data,
        get performance and match it with experiment time
        '''
        self.SViewer.createTable()

    def bindSonicTable(self):
        if not self.SViewer.hasData(): return 0 # if no data pass
        print 'Binding sonic  with geomechanical data'
        self.gsIndices = {}
        self.sTimes = {}
        self.sindices = {}
        self.trsIndices = {}
        # check for consistency
        l = self.comments['Comments'].shape[0]
        l1 = len(set(self.comments['Comments']))
        if l1!=l:
            reply = QtGui.QMessageBox.warning(self,
             'Bad geomechanical Binding',
            BadBindingMessage, QtGui.QMessageBox.Ok )
            print('Bad geomechanical binding.\
                Duplicates found in comments')
            self.comments = handle_comments(self.comments)

        for wave in WaveTypes:
            sonicDataKeys = self.sonicData[wave].keys()
            indices = compare_arrays(self.comments['Comments'],sonicDataKeys)
            # times in comments dict which correspond to sonic waves
            self.sTimes[wave] = self.comments['Time'][indices]
            # get indices in geomechanics dataset which correspond to
            # these times
            self.sindices[wave] = compare_arrays(self.data['Time'],self.sTimes[wave])
            # trsIndices for now are just all indices for sonic table
            self.trsIndices[wave] = np.arange(len(self.sTimes[wave]))
        self.gsIndices = self.sindices


    def enableSonicButton(self):
        self.showSonicButton.setDisabled(True)
        if self.SViewer.hasData():
            self.showSonicButton.setDisabled(False)
        else: self.SViewer.hide()
    def showSonicData(self):
        self.SViewer.show()
        self.SViewer.activateWindow()

    def plotSonicData(self):
        if hasattr(self.data,'keys') and self.SViewer.yAxis != 'Track #':
            yAxis = self.SViewer.yAxis
            self.SViewer.y['P']  = self.data[yAxis][self.gsIndices['P']]
            self.SViewer.y['Sx'] = self.data[yAxis][self.gsIndices['Sx']]
            self.SViewer.y['Sy'] = self.data[yAxis][self.gsIndices['Sy']]
            self.SViewer.plot(indices=self.trsIndices,
                yarray=self.data[yAxis],yindices=self.gsIndices,yAxisName=yAxis)
        else:
            self.SViewer.y['P']  = np.arange(self.SViewer.table['P'].shape[1])
            self.SViewer.y['Sx'] = np.arange(self.SViewer.table['Sx'].shape[1])
            self.SViewer.y['Sy'] = np.arange(self.SViewer.table['Sy'].shape[1])
            self.SViewer.plot(yAxisName = 'Track #')



if __name__ == '__main__':
    ViewerApp = QtGui.QApplication(sys.argv)
    win = GeoTravis()
    win.show()
    win.showMaximized()
    ViewerApp.exec_()
    sys.exit(ViewerApp.exec_())