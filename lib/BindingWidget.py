import sys
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PySide import QtGui, QtCore
import setupPlot
from CParameterTree import CParameterTree
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
    def setConfig(self):
        config = {}
        config['moduli'] = {}
        config['moduli']['Young'] = {}
        config['moduli']['Young']['x'] = 'Ex'
        config['moduli']['Young']['y'] = 'SigD'
        self.config = config
        self.time = self.gv.data['Time']
        self.interval = 100.
        self.sampLength = 0.12
        self.density = 2700
    def run(self):
        self.show()
        self.setConfig()
        self.getSonicTimes()
        self.getSlopes()
        self.getDynamic()
        self.setupTree()
        self.tree.sigStateChanged.connect(self.plot)
        self.plot()
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
        Ct = ispeeds['Sy'] 
        Cl = ispeeds['P'] 
        rho = self.density
        G = Ct**2*rho
        lamb = (Cl**2-Ct**2)*rho
        E = G*(3*lamb + 2*G)/(lamb + G)
        nu = lamb/2/(lamb + G)
        self.dmoduli['Young'] = E/psi
        self.dmoduli['Shear'] = G/psi
        self.dmoduli['Poisson'] = nu

    def plot(self):
        if not self.isVisible(): return 0
        self.plt.clear()
        interval_parameter = self.gv.modparams.param('Interval').value()
        interval = self.gv.getSliderState()
        ind = (self.itimes>=interval[0]) & (self.itimes<=interval[1])
        active = self.tree.activeItems()
        for group in active.keys():
            for key in active[group]:
                color = self.tree.groups[group]['colors'][key].getColor()
                linestyle = pg.mkPen(color=color, width=3)
                if group=='Static':
                    self.plt.plot(self.itimes[ind],self.smoduli[key][ind],pen=linestyle)
                elif group=='Dynamic':
                    self.plt.plot(self.itimes[ind],self.dmoduli[key][ind],pen=linestyle)
        self.plt.enableAutoRange()

    def setupTree(self):
        # for mod in self.dmoduli:
        self.tree.clear()
        self.tree.addItems(self.dmoduli.keys(),group='Dynamic')
        self.tree.addItems(self.smoduli.keys(),group='Static')

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
        self.yAxisMenu = self.viewMenu.addMenu('y axis')
        self.autoScaleAction = QtGui.QAction('Auto scale',self)
        self.viewMenu.addAction(self.autoScaleAction)
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
