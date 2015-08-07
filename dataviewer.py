# coding: UTF-8
## For build
# from pyqtgraphBundleUtils import *
# from pyqtgraph import setConfigOption
# setConfigOption('useOpenGL', False)
###############
import sys,os
# sys.path.append('dataviewer_lib') # comment this line on build and put files from the lib directly to the same folder
import numpy as np
import pyqtgraph as pg
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
# from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
from lib import pymat, readclf, CursorItem, MohrCircles, CParameterTree, ComboList
from lib.EffectiveStressSettings import EffectiveStressSettings
from lib.SettingsWidget import SettingsWidget
from lib.setupPlot import setup_plot
from lib.functions import *
from lib.CalculatorPlot import CalculatorPlot
from lib.Colors import DataViewerTreeColors
from lib.LabelStyles import *
ModifyingParameters = [
    {'name':'Plot vs.','type':'list','values':['x','y']},
    {'name':'Parameter', 'type':'list'},
    {'name':'Interval', 'type':'list'},
    {'name':'min', 'type':'float', 'value':0.0,'dec':True,'step':1.0},
    {'name':'max', 'type':'float', 'value':1.0,'dec':True,'step':1.0},
    {'name':'Null', 'type':'bool', 'value':False,'tip': "Press to null data"},
    {'name': 'Linear Trend', 'type': 'group', 'children': [
        {'name': 'Show trend', 'type': 'bool', 'value': False, 'tip': "Press to plot trend"},
        {'name':'Trend parameter', 'type':'list'},
        {'name':'Slope', 'type':'float', 'value':0.0,'dec':True},
        {'name':'Intersection', 'type':'float', 'value':0.0,'dec':True}
    ]},
]

TrendPen = pg.mkPen(color=(72,209,204), width=3)

class DataViewer(QtGui.QWidget):
    def __init__(self):
        super(DataViewer, self).__init__()
        self.comboList = ComboList.ComboList()
        self.settings = SettingsWidget()
        self.calcPlot = CalculatorPlot()
        self.setupGUI()
        # default plots will be drawn with multiple y and single x
        self.mainAxis = 'x'
        # no legend at first (there is no data)
        self.legend = None
        self.currentDataSetName = None
        # cursors are movable items to point the failure points
        self.cursors = []
        self.dataSetButtons = {} # list of items in the dataset section of the menu bar
        '''
        Note:
            indices = piece of all data indices, corresponding to the 
            values interval, contrained by the slider
            THE VIEWER PLOTTS DATA using indices!!!!
        '''
        self.data = None # dictionary with full current data set
        self.indices = None # array with indices for the current interval
        self.comments = {}
        self.allComments = {}
        self.allData = {} # here we keep data for different datasets
        self.allCursors = {} # cursors for different dataset
        self.allIndices = {} # contains all truncated indices
        self.allSampleLengths = {}
        self.settings.okButton.pressed.connect(self.settings.hide)
        self.exitButton.triggered.connect(sys.exit)
        self.settingsButton.triggered.connect(self.settings.show)
        self.loadButton.triggered.connect(self.requestLoad)
        self.addSceneButton.triggered.connect(self.addSceneToCombo)
        self.showComboDataButton.triggered.connect(self.comboList.show)
        self.calcPlotButton.triggered.connect(self.runCalcPlot)
        self.calcPlotButton.setDisabled(True)
        self.setStatus('Ready')
    def showComboList(self):
        self.comboList.show()
        self.comboList.activateWindow()
    def checkForLastDir(self):
        '''
        tries to open file 'lastdir'
        if it exists, returns the contents,
        else returns none
        '''
        try:
            with open('lastdir','r') as f:
                return f.read()
        except IOError:
            return ''
    def makeLastDir(self,filename):
        '''
        gets directory name from file absolute path
        create file 'lastdir' and writes 
        '''
        with open('lastdir','w') as f:
            f.write(os.path.dirname(filename))
    def requestLoad(self):
        '''
        opens file manager, gets filename,
        calls load
        '''
        self.lastdir = self.checkForLastDir()
        # second par - name of file dialog window
        # third parameter - default file name
        # forth parameter - file filter. types separated by ';;'
        filename = QtGui.QFileDialog.getOpenFileName(self, "",
         "%s"%(self.lastdir), "*.clf;;MAT files (*.mat)")
        self.load(filename)
    def load(self,filename):
        '''
        opens file manager, reads data from file,
        calls generateList to put into GUI
        '''
        if filename[0] == '': return
        if filename[1] == 'MAT files (*.mat)':
            self.data = pymat.load(filename[0])
        elif filename[1] == u'*.clf':
            data,comments,length = readclf.readclf(filename[0])
            # self.comments = comments
        else: raise IOError('Cannot read this file format.')
        # this is to remember this name when we wanna save file
        self.makeLastDir(filename[0]) # extract filename from absolute path
        self.filename = os.path.basename(filename[0])
        # remove extension from name
        self.filename = os.path.splitext(self.filename)[0]
        # Separate all digital data and units    
        self.units = data['Units']        
        del data['Units']
        self.data = data
        try:
            self.datalength = len(self.data[self.data.keys()[1]])
        except: self.datalength = 1
        self.setParameters()
        self.connectParameters()
        # self.cursors = []
        self.allData[self.filename] = data
        # get one name from array to get length of the data
        key = data.keys()[0]
        l = self.data[key].shape[0]
        self.allSampleLengths[self.filename] = length
        self.allIndices[self.filename] = np.arange(l)
        self.allComments[self.filename] = comments
        self.addDataSet(self.filename)
    def addDataSet(self,name):
        print 'Modifying GUI: adding data set button'
        dataSetButton = QtGui.QAction(name,self,checkable=True)
        dataSetButton.setActionGroup(self.dataSetGroup)
        dataSetButton.setChecked(True)
        self.dataSetMenu.addAction(dataSetButton)
        self.dataSetButtons[name] = dataSetButton
        self.allCursors[name] = []
        dataSetButton.triggered.connect(lambda: self.setCurrentDataSet(name))
        self.setCurrentDataSet(name)
    def setCurrentDataSet(self,name):
        print 'New data set is chosen'
        # if we switch to a different data set (if it's not the first),
        # remember cursors for the old one
        if self.currentDataSetName: 
            print 'Saving old data'
            self.allIndices[self.currentDataSetName] = self.indices
            self.allCursors[self.currentDataSetName] = self.cursors
            self.allComments[self.currentDataSetName] = self.comments
        print 'Setting new data'
        # set current data dictionaries to new values
        self.currentDataSetName = name
        self.data = self.allData[name]
        self.sampleLength = self.allSampleLengths[name]
        self.indices = self.allIndices[name]
        self.dataSetMenu.setDefaultAction(self.dataSetButtons[name])
        self.cursors = self.allCursors[name]
        self.comments = self.allComments[name]
        # self.mcSettings.setAvailableVariables(self.data.keys())
        self.settings.mcWidget.setAvailableVariables(self.data.keys())
    	self.calcPlotButton.setDisabled(False)
        if self.calcPlot.active:
        	self.calcPlot.setData(self.data)
        self.updatePlot()
    def save(self):
        self.lastdir = self.checkForLastDir()
        # second par - name of file dialog window
        # third parameter - default file name
        # forth parameter - file filter. types separated by ';;'
        filename = pg.QtGui.QFileDialog.getSaveFileName(self, 
            "Save to MATLAB format", "%s%s"%(self.lastdir,self.currentDataSetName), "MAT files (*.mat)")
        if filename[0] == '': return
        pymat.save(filename[0],self.data)

    def connectParameters(self):
        '''
        Makes new connection of list entries with plot after
        loading a new dataset.
        'Parameter' with name Time is default if it's in the list
        Default Interval variable is set to Time
        '''
        # set default values for modifying parameters
        self.modparams.param('Parameter').setValue('Time')
        self.modparams.param('Interval').setValue('Time')
        # connect signals to updating functions
        self.tree.sigStateChanged.connect(self.bindCursors)
        self.tree.sigStateChanged.connect(self.updatePlot)
        self.slider.sigGradientChanged.connect(self.truncate)
        self.modparams.param('Interval').sigValueChanged.connect(self.updatePlot)
        self.modparams.param('min').sigValueChanged.connect(self.setTicks)
        self.modparams.param('max').sigValueChanged.connect(self.setTicks)
        self.modparams.param('Parameter').sigValueChanged.connect(self.updatePlot)
        self.modparams.param('Plot vs.').sigValueChanged.connect(self.setMainAxis)
        # connection with trend computations        
        self.tree.sigStateChanged.connect(self.setTrendParameter)
        self.modparams.param('Parameter').sigValueChanged.connect(self.checkTrendUpdates)
        self.modparams.param('Plot vs.').sigValueChanged.connect(self.setTrendParameter)
        self.computeTrendFlag.sigValueChanged.connect(self.checkTrendUpdates)
        self.trendParameter.sigValueChanged.connect(self.setTrendParameter)
        # connect Null parameter
        self.nullFlag.sigValueChanged.connect(self.updatePlot)
        '''
        Connect to cursor buttons. Since it is a part of GUI, we need to connect them
        only once. That's why I added a condition, if len(alldatasets)==0
        '''
        if len(self.allData)==0: 
            self.plt.sigRangeChanged.connect(self.scaleCursors)
            self.addPointButton.triggered.connect(self.addCursor)
            self.removePointButton.triggered.connect(self.removeCursor)
            self.drawCirclesButton.triggered.connect(self.plotMohrCircles)
            #  Finally enable the save button
            self.saveButton.triggered.connect(self.save)
    def addCursor(self):
        print 'adding a Cursor'
        viewrange = self.plt.viewRange()
        # print viewrange
        rangeX = [viewrange[0][0],viewrange[0][1]]
        rangeY = [viewrange[1][0],viewrange[1][1]]
        pos = [(rangeX[0] + rangeX[1])/2,(rangeY[0] + rangeY[1])/2]
        xSize = float(rangeX[1]-rangeX[0])/50*800/self.plt.width()
        ySize = float(rangeY[1]-rangeY[0])/50*800/self.plt.height()
        Cursor = CursorItem.CursorItem(pos,[xSize,ySize],pen=(4,9))
        self.cursors.append(Cursor)
        self.allCursors[self.currentDataSetName] = self.cursors
        # bind cursor if there is something to plot
        plotlist = self.activeEntries()
        if len(plotlist)>0: 
            self.bindCursors()
            self.updatePlot()

    def removeCursor(self):
        if len(self.cursors)>0:
            self.cursors.pop(-1)
            self.updatePlot()

    def plotMohrCircles(self):
        global CirclesWidget
        CirclesWidget = MohrCircles.MohrCircles()
        params = self.settings.mcWidget.parameters()
        b = params[3] # biot coef
        names = []
        PorePressure = []
        AxialStress = []
        ConfiningStress = []
        ncircles = 0
        for DataSet in self.allCursors.keys():
            cursors = self.allCursors[DataSet]
            data = self.allData[DataSet]
            if cursors == []: 
                continue
            else: 
                indices = []
                for cursor in cursors:
                    indices.append(cursor.index)
                    ncircles += 1
                    Sig1 = data[params[0]][cursor.index] #axial stress
                    Pc = data[params[1]][cursor.index] # confining press
                    Pu = data[params[2]][cursor.index] # pore pressure
                    sigma1 = Sig1 - b*Pu
                    sigma3 = Pc - b*Pu
                    CirclesWidget.addData(sigma1,sigma3,name=DataSet +'_'+ str(ncircles))
        if ncircles == 0: return 0
        CirclesWidget.start()
        CirclesWidget.show()
        CirclesWidget.activateWindow()

    def scaleCursors(self):
        '''
        make cursors circles of an appropriate size when scaling plot
        '''
        viewrange = self.plt.viewRange()
        rangeX = [viewrange[0][0],viewrange[0][1]]
        rangeY = [viewrange[1][0],viewrange[1][1]]
        xSize = float(rangeX[1]-rangeX[0])/50*800/self.plt.width()
        ySize = float(rangeY[1]-rangeY[0])/50*800/self.plt.height()
        size = np.array([xSize,ySize])
        for cursor in self.cursors:
            oldSize = cursor.getSize() # workaround to force the cursor stay on the same place
            cursor.translate(oldSize/2,snap=None)
            cursor.setSize(size)
            cursor.translate(-size/2,snap=None)
    def drawCursors(self):
        '''
        add cursors again after clearing the plot window
        '''
        for cursor in self.cursors:
            self.plt.addItem(cursor)
    def bindCursors(self):
        '''
        make cursor slide along data
        '''
        # print self.sender()
        try: 
            plotlist = self.activeEntries()
            if self.mainAxis == 'y':
                xlabel = plotlist[-1]
                ylabel = self.modparams.param('Parameter').value()
            elif self.mainAxis == 'x':
                ylabel = plotlist[-1]
                xlabel = self.modparams.param('Parameter').value()
            x = self.data[xlabel][self.indices]
            y = self.data[ylabel][self.indices]

            for cursor in self.cursors:
                cursor.setData(x,y)
        except: pass

    def checkTrendUpdates(self):
        if self.computeTrendFlag.value(): 
            self.computeTrend()
            self.updatePlot()
        
    def setTrendParameter(self):
        entries = self.activeEntries() 
        for i in entries: pass
        if entries != []: self.trendParameter.setValue(i)
        self.checkTrendUpdates()

    def truncate(self):
        interval_parameter = self.modparams.param('Interval').value()
        interval = self.getSliderState()
        arr = self.data[interval_parameter]
        self.indices = (arr>=interval[0]) & (arr <= interval[1])
        self.checkTrendUpdates() 
        self.updatePlot()
    def setMainAxis(self):
        self.mainAxis = self.modparams.param('Plot vs.').value()
        self.updatePlot()
    def updateLimits(self):
        interval = self.getSliderState()
        self.modparams.param('min').sigValueChanged.disconnect(self.setTicks)
        self.modparams.param('max').sigValueChanged.disconnect(self.setTicks)
        self.modparams.param('min').setValue(interval[0])
        self.modparams.param('max').setValue(interval[1])
        self.modparams.param('min').sigValueChanged.connect(self.setTicks)
        self.modparams.param('max').sigValueChanged.connect(self.setTicks)
    def setTicks(self):
        '''
        sets ticks to state coressponding to  Interval min/max
        values, when they are manually changed
        '''
        interval_parameter = self.modparams.param('Interval').value()
        scale = self.data[interval_parameter].max()
        values = [float(self.modparams.param('min').value())/scale,
                  float(self.modparams.param('max').value())/scale
                 ]
        i = 0
        self.slider.sigGradientChanged.disconnect(self.updatePlot)
        for tick in self.slider.ticks:
            self.slider.setTickValue(tick, values[i])
            i += 1
        self.slider.sigGradientChanged.connect(self.updatePlot)
        self.updatePlot()

    def updatePlot(self):
        '''
        updates plot
        '''
        self.setAxisScale()
        self.updateLimits()
        ### Ready to update
        # self.setAutoFillBackground(True)
        self.clearPlotWindow()
        self.drawCursors()
        self.plt.showGrid(x=True, y=True)
        if self.mainAxis == 'x':
            self.plotVersusX()
        if self.mainAxis == 'y':
            self.plotVersusY()
        if self.computeTrendFlag.value():
            self.plotTrend()
        if self.calcPlot.active:
        	self.calcPlot.indices = self.indices
        	self.calcPlot.plot()

    def plotVersusX(self):
        '''
        plot when we have sevaral y's versus of x.
        '''
        # Get variables to plot
        data = self.data
        plotlist = self.activeEntries()
        xlabel = self.modparams.param('Parameter').value()
        null = self.nullFlag.value()
        for i in range(len(plotlist)):
            ylabel = plotlist[i]
            color = self.tree.colors[ylabel].getColor()
            linestyle = pg.mkPen(color=color, width=3)
            yunits = self.units[ylabel]
            xdata = data[xlabel][self.indices]
            ydata = data[ylabel][self.indices]
            if null: ydata -= ydata[0]
            self.plt.plot(xdata, ydata, 
                pen=linestyle, name=plotlist[i])
            self.plt.setLabel('left', plotlist[i],units=yunits,
                **AxisLabelStyle)
        xunits = self.units[xlabel]
        self.plt.setLabel('bottom', xlabel,units=xunits,**AxisLabelStyle)
        # if len(plotlist)>0: self.bindCursors(data[xlabel],data[ylabel])
    def plotVersusY(self):
        '''
        plot when we have sevaral y's versus of x.
        '''
        # Get variables to plot
        data = self.data
        plotlist = self.activeEntries()
        ylabel = self.modparams.param('Parameter').value()
        yunits = self.units[ylabel]
        null = self.nullFlag.value()
        for i in range(len(plotlist)):
            xlabel = plotlist[i]
            color = self.tree.colors[xlabel].getColor()
            linestyle = pg.mkPen(color=color, width=3)
            xunits = self.units[xlabel]
            xdata = data[xlabel][self.indices]
            ydata = data[ylabel][self.indices]
            if null: xdata -= xdata[0]
            self.plt.plot(xdata, ydata, 
                pen=linestyle, name=plotlist[i])
            self.plt.setLabel('bottom', xlabel,units=xunits,**AxisLabelStyle)
        self.plt.setLabel('left', ylabel,units=yunits,**AxisLabelStyle)

    def plotTrend(self):
        '''
        plots linear trend 
        '''
        if self.mainAxis == 'x':
            xpar = self.modparams.param('Parameter').value()
            ypar = self.trendParameter.value()
            self.plt.setLabel('bottom', xpar)
        if self.mainAxis == 'y':
            xpar = self.trendParameter.value()
            ypar = self.modparams.param('Parameter').value()
        x = self.data[xpar][self.indices]
        y = self.slope*x + self.intersection
        self.plt.plot(x,y,pen=TrendPen, name='%s Trend'%(self.trendParameter.value()))
        self.plt.setLabel('bottom', xpar)
        self.plt.setLabel('left', ypar)

    def clearPlotWindow(self):
        '''
        clears plot from data. clears legend.
        if there is no legend creates it
        '''
        # default legend position
        position = [30,30]
        # clear plot area
        self.plt.clear()
        # remove old legend
        if self.legend: 
            position = self.legend.pos()
            self.legend.scene().removeItem(self.legend)
        # creadte new legend
        self.plt.addLegend([90,20],offset=position)
        self.legend = self.plt.legend
        # print self.legend.pos()
    def setAxisScale(self):
        '''
        sets scale to the interval axis. if time, sets minimum value to 0,
        because it could have been cleared
        '''
        interval_parameter = self.modparams.param('Interval').value()
        if interval_parameter == 'Time':
            self.timeAxis.setRange(0,max(self.data['Time']))
        else:
            self.timeAxis.setRange(min(self.data[interval_parameter]),max(self.data[interval_parameter]))

    def getSliderState(self):
        '''
        returns numpt array 1x2 of slider ticks positions
        note: max position = 1, min = 0
        '''
        interval = []
        for i in self.slider.ticks:
            interval.append(self.slider.tickValue(i))
        interval_parameter = self.modparams.param('Interval').value()
        scale = self.data[interval_parameter].max()
        return np.array(sorted(interval))*scale
    def activeEntries(self):
        '''
        returns a list of active entries in the data bar
        '''
        plotlist = []
        # for i in self.data.keys():
        #     if self.params.param(i).value() == True:
        for item in self.data.keys():
            if self.tree.boxes[item].value() == True:
                plotlist.append(item)
        return plotlist
    def setParameters(self):
        print 'Modifying GUI: adding parameters to plot'
        # set modifying parameters
        self.modparamlist = ModifyingParameters
        self.modparamlist[1]['values'] = self.data.keys() # Parameter
        self.modparamlist[2]['values'] = self.data.keys() # Interval
        self.modparamlist[6]['children'][1]['values'] = self.data.keys() # Trend parameter
        # create parameter class instances()
        # self.params = Parameter.create(name='Data', type='group',children=self.paramlist)
        self.modparams = Parameter.create(name='Options', type='group',children=self.modparamlist)
        self.tree.clear()
        self.tree.addItems(self.data.keys(),DataViewerTreeColors)
        # self.tree.setParameters(self.params, showTop=True)
        self.modtree.setParameters(self.modparams, showTop=True)
        self.assignAttributes() # to get shorter names
    def assignAttributes(self):
        '''
        assign parameters from modparams tree to class DataViewer
        attributes to shorten code
        '''
        self.nullFlag = self.modparams.param('Null')
        # assign chilren of 'Linear Trend' group to class attributes
        self.computeTrendFlag = self.modparams.param('Linear Trend').children()[0]
        self.trendParameter = self.modparams.param('Linear Trend').children()[1]
        self.trendSlope = self.modparams.param('Linear Trend').children()[2]
        self.trendIntersection = self.modparams.param('Linear Trend').children()[3]
    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        self.setWindowIcon(QtGui.QIcon('images/Logo.png'))    
        # Global widget where we place our layout
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        # Create and add menu bar
        self.menuBar = QtGui.QMenuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.viewMenu = self.menuBar.addMenu('View')
        self.dataSetMenu = self.menuBar.addMenu('Dataset')
        self.mohrMenu = self.menuBar.addMenu('Mohr\' Circles')
        self.comboPlotMenu = self.menuBar.addMenu('Combo plot')
        self.prefMenu = self.menuBar.addMenu('Preferences')
        self.dataSetGroup = QtGui.QActionGroup(self)
        # create status bar
        self.layout.addWidget(self.menuBar,0)
        self.layout.setMenuBar(self.menuBar)
        # create submenu items
        self.loadButton = QtGui.QAction('Load',self)
        self.saveButton = QtGui.QAction('Save',self)
        self.exitButton = QtGui.QAction('Exit',self,shortcut="Alt+F4")
        self.calcPlotButton = QtGui.QAction('Calculator',self)
        self.autoScaleButton = QtGui.QAction('Auto scale',self)
        self.addPointButton = QtGui.QAction('Add point',self,shortcut='Ctrl+Q')
        self.removePointButton = QtGui.QAction('Remove point',self,shortcut='Ctrl+R')
        self.drawCirclesButton = QtGui.QAction('Draw Mohr\'s Circles',self,shortcut='Alt+M')
        self.showComboDataButton = QtGui.QAction('Show',self,shortcut='Ctrl+Shift+C')
        self.addSceneButton = QtGui.QAction('Add scene',self,shortcut='Ctrl+C')
        self.settingsButton = QtGui.QAction('Settings',self)
        # Add buttons to submenus
        self.fileMenu.addAction(self.loadButton)
        self.fileMenu.addAction(self.saveButton)
        self.fileMenu.addAction(self.exitButton)
        self.mohrMenu.addAction(self.addPointButton)
        self.mohrMenu.addAction(self.removePointButton)
        self.mohrMenu.addAction(self.drawCirclesButton)
        self.viewMenu.addAction(self.calcPlotButton)
        self.viewMenu.addAction(self.autoScaleButton)
        self.comboPlotMenu.addAction(self.showComboDataButton)
        self.comboPlotMenu.addAction(self.addSceneButton)
        self.prefMenu.addAction(self.settingsButton)
        # splitter is a widget, which handles the layout
        # it splits the main window into parameter window
        # and the plotting area
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # tree is a list of parameters to plot
        self.tree = CParameterTree.CParameterTree(name='Data')
        # modtree is a list of governing parameters to modify plot
        self.modtree = ParameterTree(showHeader=False)
        # sublayout is were we place our plot and slider
        self.sublayout = pg.GraphicsLayoutWidget()
        # treesplitter splits parameter window into 2 halfs
        self.treesplitter = QtGui.QSplitter()
        self.buttonsplitter = QtGui.QSplitter()
        self.treesplitter.setOrientation(QtCore.Qt.Vertical)
        self.treesplitter.addWidget(self.tree)
        self.treesplitter.addWidget(self.modtree)
        self.treesplitter.setSizes([int(self.height()*0.7),
                                    int(self.height()*0.3),
                                    20])
        self.treesplitter.setStretchFactor(0, 0)
        self.treesplitter.setStretchFactor(1, 0.9)

        self.splitter.addWidget(self.treesplitter)
        self.splitter.addWidget(self.sublayout)
        self.splitter.setSizes([int(self.width()*0.4), int(self.width()*0.6)])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.plt = self.sublayout.addPlot()
        setup_plot(self.plt)
        self.plt.setLabel('bottom', 'X Axis',**AxisLabelStyle)
        self.plt.setLabel('left', 'Y Axis',**AxisLabelStyle)
        self.plt.enableAutoRange(enable=True)
        self.autoScaleButton.triggered.connect(self.plt.enableAutoRange)
        self.slider = self.createSlider()
        self.timeAxis = pg.AxisItem('bottom')
        self.timeAxis.setStyle(tickTextOffset=TickOffset)
        self.timeAxis.tickFont = TickFont
        self.sublayout.nextRow()
        self.sublayout.addItem(self.slider)
        self.sublayout.nextRow()
        self.sublayout.addItem(self.timeAxis)
        self.statusBar = QtGui.QStatusBar()
        self.treesplitter.addWidget(self.statusBar)
        self.setGeometry(80, 50, 800, 600)
        self.treesplitter.setStretchFactor(2, 0)
        self.treesplitter.setCollapsible(2, 0)
        self.statusBar.setSizePolicy(QtGui.QSizePolicy.Ignored,
            QtGui.QSizePolicy.Fixed)
        self.setGeometry(80, 30, 1000, 700)
    def setStatus(self,message):
        self.statusBar.showMessage(message)
        print message
    def computeTrend(self):
        '''
        computer linear trend a and b and 
        from truncated data. 
        '''
        if self.mainAxis == 'x': # if multiple plots vs x
            xpar = self.modparams.param('Parameter').value()
            ypar = self.trendParameter.value()
        if self.mainAxis == 'y': # if multiple plots vs y
            ypar = self.modparams.param('Parameter').value()
            xpar = self.trendParameter.value()
        
        x = self.data[xpar][self.indices]
        y = self.data[ypar][self.indices]
        A = np.array([x, np.ones(len(y))]).T
        ## Solves the equation a x = b by computing a vector x that 
        ## minimizes the Euclidean 2-norm || b - a x ||^2. 
        self.slope,self.intersection = np.linalg.lstsq(A,y)[0]
        self.trendSlope.setValue(self.slope)
        self.trendIntersection.setValue(self.intersection)

    def createSlider(self):
        slider = pg.GradientEditorItem(orientation='top', allowAdd=False)
        # print slider.__dict__
        # slider.tickPen = pg.mkPen(color=(255,255,255))
        slider.tickSize = 0
        # print slider.gradRect
        slider.rectSize = 0
        for i in slider.ticks:
            slider.setTickColor(i, QtGui.QColor(150,150,150))
        return slider
    def closeEvent(self,event):
        '''
        When pressing X button, show quit dialog.
        if yes, closes the window and ends the process
        '''
        # reply = QtGui.QMessageBox.question(self, 'Quit Dataviewer',
        #     "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #     QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        # if reply == QtGui.QMessageBox.Yes:
        #     sys.exit()
        #     event.accept()
        # else:
        #     event.ignore()
        sys.exit()

    def addSceneToCombo(self):
        print 'adding scene to Combo plot'
        rootname = self.currentDataSetName
        for item in self.plt.listDataItems():
            name = rootname+'_'+item.name()
            x = item.xData
            y = item.yData
            self.comboList.addItem(name,x,y)
    def runCalcPlot(self):
    	self.calcPlot.active = True
    	self.calcPlot.setData(self.data)
        self.calcPlot.show()
    	self.calcPlot.activateWindow()

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    # pg.mkQApp()
    win = DataViewer()
    win.showMaximized()
    # win.showFullScreen()
    win.show()
    App.exec_()
    
    

