import re
import numpy as np
from scipy.stats.mstats import mode
# from numba import jit # for optimization

# @jit 
def truncatedata(dic,key,interval):
    '''
    truncates data to values corresponding only to the interval of 
    values in dic[key]
    '''
    newdic = {}
    t = dic[key]
    for i in dic.keys():
        newdic[i] =  dic[i][(t>=interval[0]) & (t<=interval[1])]
    return newdic

def reducedata(dic,order):
    '''
    reduces data. returns data with only n-th (order) datapoint.
    '''
    if order == 1: return dic
    newdic = {}
    for i in dic.keys():
        # ind = np.arange()
        n = len(dic[i])
        newdic[i] =  dic[i][np.arange(0,n,order)]
    return newdic

# @jit
def compare_dict_array(dictionary,array):
    '''
    returns part of the dictionary with the keys which are in the array
    '''
    matched_dictionary = dict.fromkeys(array)
    for i in array:
        matched_dictionary[i] = dictionary[i]
    return matched_dictionary

# @jit
def get_table(dictionary):
    '''
    Converts dictionary to a numpy array and list of names
    Input: dictionary with 
    (1) string keys
    (2) each entries is a nparray (Nx2) 1 - time,2 - amplitude
    Output:
    3D numpy array. 1st dimension - time or amplitude
    2nd dimension - number of file
    3rd dimension - datapoints
    '''
    # get length of arrays (must be the same)
    Npoints = dictionary.values()[0].shape[0]
    # get # of arrays
    names = dictionary.keys()
    names.sort(key=natural_keys)
    # print names
    Nfiles = len(names)
    # allocate space
    x = np.zeros((Nfiles,Npoints))
    y = np.zeros((Nfiles,Npoints))
    # loop over files
    for k in range(Nfiles): # use for cause needs to be sorted
        x[k] = dictionary[names[k]][:,0]
        y[k] = dictionary[names[k]][:,1] 
    # Create table
    table = np.array((x,y))
    # print table
    return table

# No jit doesn't work for some reason
# @jit
def compare_arrays(array1,array2):
    '''
    returns indices of items in array1 whcich are also entries of 
    array2
    '''
    x = [i for i,item in enumerate(array1) if item in array2]
    return np.array(x)

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

# Usage
# alist=[
#     "something1",
#     "something12",
#     "something17",
#     "something2",
#     "something25",
#     "something29"]

# alist.sort(key=natural_keys)
# print(alist)

def findInDict(value,dic):
    for key,val in dic.items():
            if val == value:
                return key
    raise ValueError('Item not found')

def handle_comments(d):
    c = d['Comments']
    t = d['Time']
    nc = []
    nt = []
    unique = np.unique(c)
    for u in unique:
        indices = np.argwhere(c==u)
        ind = indices[-1]
        nc.append(c[ind][0])
        nt.append(t[ind][0])
    nc = np.array(nc)
    nt = np.array(nt)
    new_comments = {'Time':nt,'Comments':nc}
    return new_comments


def multi_window(sig,win):
    '''
    algorithm picking arrival times
    the maximum amplitudes correspond
    to sending and arriving times
    n-dimensional extension
    sig - (N,M) numpy array
    N - number of sonic tracks
    M - data points of oscilloscope
    win - 3-element list
    '''
    sig0 = sig - mode(sig,axis=1)[0] # remove shift in amplitude
    E = sig0**2
    N = E.shape[1]-win[2]-win[0]-1
    BTA = np.zeros((E.shape[0],N)) # before term average
    ATA = np.zeros((E.shape[0],N)) # after term average
    DTA = np.zeros((E.shape[0],N)) # delayed term average
    iterator = np.arange(N)
    for i in np.nditer(iterator):
        BTA[:,i] = np.mean(E[:,i:i+win[0]],axis=1)
        ATA[:,i] = np.mean(E[:,i+win[0]:i+win[0]+win[1]],axis=1)
        DTA[:,i] = np.mean(E[:,i+win[0]:i+win[0]+win[2]],axis=1)
    r = ATA/BTA + DTA/BTA
    return r/10

def get_list(yAxisName,WaveTypes):
    # l = [yAxisName + ,WaveTypes[0],]
    l1 = yAxisName + ' ' + WaveTypes[0]
    l2 = yAxisName + ' ' + WaveTypes[1]
    l3 = yAxisName + ' ' + WaveTypes[2]
    l4 = WaveTypes[0]
    l5 = WaveTypes[1]
    l6 = WaveTypes[2]
    return [l1,l2,l3,l4,l5,l6]