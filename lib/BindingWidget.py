import sys
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PySide import QtGui, QtCore
import setupPlot
from CParameterTree import CParameterTree
from LabelStyles import AxisLabelStyle
WaveTypes = ['P','Sx','Sy']
psi = 6894.75729

class BindingWidget(QtGui.QWidget):
    def __init__(self,parents=[None,None]):
        super(BindingWidget, self).__init__(None,
            )
        	# QtCore.Qt.WindowStaysOnTopHint)
        self.setupGUI()
        self.smoduli = {} # static moduli
        self.dmoduli = {} # dynamic moduli
        self.gv = parents[0] # Geomechanics viewer
        self.sv = parents[1] # Sonic viewer
        try:
            self.gv.slider.sigGradientChanged.connect(self.plot)
        except: pass
        self.autoScaleAction.triggered.connect(self.plot)
        self.plotVsXAction.triggered.connect(self.plot)
        self.plotVsYAction.triggered.connect(self.plot)
    def setConfig(self):
        config = {}
        config['moduli'] = {}
        config['moduli']['Young'] = {}
        config['moduli']['Young']['x'] = 'Ex'
        config['moduli']['Young']['y'] = 'SigD'
        config['moduli']['Young']['units'] = 'psi'
        config['units'] = {}
        config['units']['Young'] = 'psi'
        config['units']['Young_x'] = 'psi'
        config['units']['Young_y'] = 'psi'
        config['units']['Shear'] = 'psi'
        config['units']['Shear_x'] = 'psi'
        config['units']['Shear_y'] = 'psi'
        config['units']['Poisson'] = ''
        config['units']['Poisson_x'] = ''
        config['units']['Poisson_y'] = ''
        self.config = config
        self.time = self.gv.data['Time']
        self.interval = 100.
        self.sampLength = 0.12
        self.density = 270
    def run(self):
        self.show()
        self.setConfig()
        self.getSonicTimes()
        self.interpolateGData()
        self.getSlopes()
        self.getDynamic()
        self.setupTree()
        self.setupMenu()
        self.tree.sigStateChanged.connect(self.plot)
        self.plot()

    def interpolateGData(self):
        self.gdata = {}
        print 'Interpolating geomechanical data'
        for key in self.gv.data.keys():
            interp = interp1d(self.gv.data['Time'],self.gv.data[key],
                bounds_error=False)
            self.gdata[key] = interp(self.itimes)

    def setupMenu(self):
        # clear y axis menu and groups
        self.parMenu.clear()
        for action in self.parameterGroup.actions():
            self.parameterGroup.removeAction(action)
        self.parameterActions = {}
        # assign new actions
        for key in self.gv.data.keys():
            action = QtGui.QAction(key,self,checkable=True)
            action.setActionGroup(self.parameterGroup)
            self.parMenu.addAction(action)
            self.parameterActions[key] = action
            action.triggered.connect(self.plot)
        try:
            self.parameterActions['Time'].setChecked(True)
        except: pass

    def getSonicTimes(self):
        '''
        every wave has its own recording time
        geomecanic time range includes all sonic times
        no need to plot all geomechanics
        take average recording times for sonic data
        plot geomechanics at them
        also, there can be different amount of sonic data
        for each wave. so must make arrays same length.
        '''
        print 'Computing times for output'
        l = []
        for wave in WaveTypes:
            l.append(len(self.gv.sTimes[wave]))
        l = min(l)
        gtimes = np.zeros(l)
        for wave in WaveTypes:
            gtimes += self.gv.sTimes[wave][:l]
        gtimes /= 3
        self.itimes = gtimes

    def getSlopes(self):
        '''
        Get moduli from geomechanical data 
        '''
        N = len(self.itimes)
        config = self.config
        for mod in self.config['moduli'].keys():
            self.smoduli[mod] = np.zeros(N)
            xarr = self.gv.data[config['moduli']['Young']['x']]
            yarr = self.gv.data[config['moduli']['Young']['y']]
            for i in xrange(N):
                ind = abs(self.time-self.itimes[i])<self.interval/2
                x = xarr[ind]
                y = yarr[ind]
                A = np.array([x, np.ones(len(y))]).T
                slope,intersection = np.linalg.lstsq(A,y)[0]
                self.smoduli[mod][i] = slope

    def getDynamic(self):
        ispeeds = {}
        for wave in WaveTypes:
            speed = self.sampLength/self.sv.aTimes[wave]*1e+6
            interp = interp1d(self.gv.sTimes[wave],speed,bounds_error=False)
            ispeeds[wave] = interp(self.itimes)
        Ctx = ispeeds['Sx'] 
        Cty = ispeeds['Sy'] 
        Cl = ispeeds['P'] 
        rho = self.density
        Gx = Ctx**2*rho
        Gy = Cty**2*rho
        lambx = (Cl**2-Ctx**2)*rho
        lamby = (Cl**2-Cty**2)*rho
        Ex = Gx*(3*lambx + 2*Gx)/(lambx + Gx)
        Ey = Gy*(3*lamby + 2*Gy)/(lamby + Gy)
        nux = lambx/2/(lambx + Gx)
        nuy = lamby/2/(lamby + Gy)
        if self.config['units']['Young'] == 'psi':
            self.dmoduli['Young_x'] = Ex/psi
            self.dmoduli['Young_y'] = Ey/psi
        elif self.config['units']['Young'] == 'Pa':
            self.dmoduli['Young_x'] = Ex
            self.dmoduli['Young_y'] = Ey
        if self.config['units']['Shear'] == 'psi':
            self.dmoduli['Shear_x'] = Gx/psi
            self.dmoduli['Shear_y'] = Gy/psi
        if self.config['units']['Shear'] == 'Pa':
            self.dmoduli['Shear_x'] = Gx
            self.dmoduli['Shear_y'] = Gy
        if self.config['units']['Poisson'] == '':
            self.dmoduli['Poisson_x'] = nux
            self.dmoduli['Poisson_y'] = nuy

    def plot(self):
        if not self.isVisible(): return 0
        self.plt.clear()
        self.plt.showGrid(x=True, y=True)
        interval_parameter = self.gv.modparams.param('Interval').value()
        interval = self.gv.getSliderState()
        ind = (self.itimes>=interval[0]) & (self.itimes<=interval[1])
        active = self.tree.activeItems()
        par = self.parameter()
        if self.plotVsXAction.isChecked():
            x = self.gdata[par][ind]
            xName = par + ' (' + self.gv.units[par] + ')'
        elif self.plotVsYAction.isChecked():
            y = self.gdata[par][ind]
            yName = par + ' (' + self.gv.units[par] + ')'
        for group in active.keys():
            for key in active[group]:
                color = self.tree.groups[group]['colors'][key].getColor()
                linestyle = pg.mkPen(color=color, width=3)
                if group=='Static':
                    if self.plotVsXAction.isChecked():
                        y = self.smoduli[key][ind]
                    elif self.plotVsYAction.isChecked():
                        x = self.smoduli[key][ind]
                elif group=='Dynamic':
                    if self.plotVsXAction.isChecked():
                        y = self.dmoduli[key][ind]
                        yName = key + ' (' + self.config['units'][key] + ')'
                    elif self.plotVsYAction.isChecked():
                        x = self.dmoduli[key][ind]
                        xName = key + ' (' + self.config['units'][key[:-2]] + ')'
                self.plt.plot(x,y,pen=linestyle)
                self.plt.setLabel('left',yName,**AxisLabelStyle)
                self.plt.setLabel('bottom',xName,**AxisLabelStyle)

        if self.autoScaleAction.isChecked():
            self.plt.enableAutoRange()

    def setupTree(self):
        # for mod in self.dmoduli:
        self.tree.clear()
        self.tree.addItems(self.dmoduli.keys(),group='Dynamic')
        self.tree.addItems(self.smoduli.keys(),group='Static')

    def parameter(self):
        for key in self.parameterActions.keys():
            if self.parameterActions[key].isChecked(): return key
    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        # menu
        self.menuBar = QtGui.QMenuBar()
        self.layout.setMenuBar(self.menuBar)
        # menu actions
        self.viewMenu = self.menuBar.addMenu('View')
        self.parMenu = self.viewMenu.addMenu('Parameter')
        self.plotVsMenu = self.viewMenu.addMenu('Plot versus')
        self.plotVsXAction = QtGui.QAction('x',self,checkable=True)
        self.plotVsYAction = QtGui.QAction('y',self,checkable=True)
        self.plotVsGroup = QtGui.QActionGroup(self)
        self.plotVsXAction.setActionGroup(self.plotVsGroup)
        self.plotVsYAction.setActionGroup(self.plotVsGroup)
        self.plotVsMenu.addAction(self.plotVsXAction)
        self.plotVsMenu.addAction(self.plotVsYAction)
        self.plotVsXAction.setChecked(True)
        self.autoScaleAction = QtGui.QAction('Auto scale',self,checkable=True)
        self.autoScaleAction.setChecked(True)
        self.viewMenu.addAction(self.autoScaleAction)
        self.parameterGroup = QtGui.QActionGroup(self)
        # widgets
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tree = CParameterTree(name='Elastic moduli')
        self.sublayout = pg.GraphicsLayoutWidget()
        # 
        self.layout.addWidget(splitter)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.sublayout)
        self.plt = self.sublayout.addPlot()
        setupPlot.setup_plot(self.plt)
        #
        splitter.setSizes([int(self.width()*0.3),
            int(self.width()*0.7),
            ])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    win = BindingWidget()
    # win.showMaximized()
    # win.showFullScreen()
    win.show()
    App.exec_()
