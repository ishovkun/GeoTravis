from human_sorting import natural_keys
import numpy as np
from numba import jit # for optimization

@jit
def get_graphic_path(dictionary,yarray=None,offset = 1):
	'''
	Option 1: yarray = None
	combines arrays from dict into x & y multiline arrays
	input: dictionary, each entry - Nx2 array
	2 columns - x and y
	Option 2: returns graphic path
	'''
	# get length of each array (must be the same)
	Npoints = len(dictionary[dictionary.keys()[0]])
	# get # of arrays
	names = dictionary.keys()
	names.sort(key=natural_keys)
	# print names
	Nfiles = len(names)
	# allocate space
	x = np.zeros((Nfiles,Npoints))
	y = np.zeros((Nfiles,Npoints))
	for k in range(Nfiles):
			x[k] = dictionary[names[k]][:,0]
			y[k] = dictionary[names[k]][:,1]
	if not yarray:
		offset_array = np.arrange(0,Npoints*offset,offset).reshape(Npoints,1)
	else:
		offset_array = yarray.reshape(Npoints,1)
	y += offset_array
	return x,y