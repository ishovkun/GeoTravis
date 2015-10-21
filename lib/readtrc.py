import numpy as np
import re

def read_TRC(filename):
	# with open(directory + files[0]) as f:
	with open(filename) as f:
		text = f.read()
		# print "reading %s ..."%(filename.split('/')[-1])
	"""
	regex corresponding to a line with 2 fload\scientific numbers separated by a whitespace or \t
	"""
	try:
		expr = '\n-?\d+\.?\d+\E?-?\d+.+[-+]?\d+\.?\d+\E?[-+]?\d+\n'
		match = re.search(expr,text) # get beginning of the data
		# print text[match.start()-2:match.end()+3]
		text = text[match.start():-1] # search starting from the beginning of the data
		expr = '[-+]?\d+\.\d+E?[-+]?\d{0,3}'
		data = re.findall(expr,text)
		time = np.array(data[::2])
		signal = np.array(data[1::2])
		# print signal
		values = np.column_stack((time,signal))
		values = values.astype(np.float)
		# print values
		return values
	except: print 'Error reading %s'%(filename)