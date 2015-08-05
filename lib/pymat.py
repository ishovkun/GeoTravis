import scipy.io

def savemat(filename,dic):
	'''
	saves dictionary to matlab binary format
	'''
	scipy.io.savemat(filename, dic)
def loadmat(filename):
	'''
	loads .mat file as a dictionary
	'''
	d = scipy.io.loadmat(filename)
	del d['__globals__']
	del d['__header__']
	del d['__version__']
	for i in d.keys():
		d[i] = d[i][0]
	return d