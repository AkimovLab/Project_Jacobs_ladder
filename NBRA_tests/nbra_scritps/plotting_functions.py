"""
This file contains functions for plotting the comparison metrics. The `plot_comparison`
function plots 1 specified data set while the `plot_comparison_wrapper` function
calls the `plot_comparison` function for each desired data set to be plotted.
These functions are called in comparison_plotting.py
"""

import sys
import cmath
import math
import h5py
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'w'

import models_dictionaries
import comparison_functions

import numpy as np
import time
import warnings

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *

import util.libutil as comn
from libra_py import units
import libra_py.models.Holstein as Holstein

from libra_py import dynamics_plotting

#from matplotlib.mlab import griddata
plt.rcParams['figure.facecolor'] = 'w'


cnames = {
    0: '#FF1493',
    1: '#7FFFD4',
    2: '#000000',
    3: '#8A2BE2',
    4: '#A52A2A',
    5: '#5F9EA0',
    6: '#7FFF00',
    7: '#FF7F50',
    8: '#00BFFF',
    9: '#696969',
    10: '#B22222',
    11: '#228B22',
    12: '#DC143C',
    13: '#FF00FF',
    14: '#B8860B',
    15: '#A9A9A9',
    16: '#006400',
    17: '#BDB76B',
    18: '#8B008B',
    19: '#556B2F',
    20: '#FF8C00',
    21: '#9932CC',
    22: '#8B0000',
    23: '#E9967A',
    24: '#8FBC8F',
    25: '#483D8B',
    26: '#9400D3'}

def plot_comparison(filename, param_set,  labels, color_index, type = 'population', integrated=1, time_normalized=0):
    # labels options are input, reorg, and set. input requires a list the length of param_sets
    with h5py.File(f'{filename}', 'r') as f:
        time = list(f[f'0/time'])
        dt = time[1] - time[0]
        
        label = 0
        if labels == "reorg":
            label = (f[f'{param_set}/reorg'][0])
        elif labels == "input":
            label_list = labels[cnt]
        elif labels == "set":
            label = param_set
        elif labels == "reorg+set":
            label = "{:.2e}".format(f[f'{param_set}/reorg'][0]) + f", Set {i}"
                        
        if integrated:
            metric = list(f[f'{param_set}/{type}_metric_integrated'])
        else:
            metric = list(f[f'{param_set}/{type}_metric_raw'])
        if time_normalized:
            metric = comparison_functions.time_normalize(metric, dt)
            
        for t in range(len(time)):
            time[t] = time[t] * units.au2fs
        plt.plot(time, metric, label = label, linewidth = 8, color = cnames[color_index])

def plot_comparison_wrapper(filenames, params_sets, title, savename, type = 'population', integrated=1, labels = "reorg", time_normalized=0, label_list = None):
    # labels options are input, reorg, set, or reorg+set. input requires a list the length of param_sets
    data = {}
    cnt = 0
    label = 0
    fig = plt.figure(figsize=(12, 8))
    plt.title(title, fontsize=32)
    plt.xlabel('Time, fs',fontsize=28)
    plt.ylabel('Metric',fontsize=28)
    ax = plt.gca()
    ax.tick_params(labelsize=24, width=5, length=8)
    for filename in filenames:
        print(f"accessing {filename}")
        for i in params_sets:
            plot_comparison(filename, i, labels, cnt, type = type, integrated=integrated, time_normalized=time_normalized)
            cnt += 1
            if cnt > 26:
                cnt = 0 # this resets color count - reuses colors if more than 27 lines

    # reorder the legend in ascending order if the labels are reorg energy and formats labels in sci notation
    if labels == "reorg":
        handles, labels = ax.get_legend_handles_labels()
        tuples = []
        for i in range(len(labels)):
            tuples.append((handles[i],float(labels[i])))
        tuples.sort(key=lambda x:x[1]) # reoders list of tuples in ascending order of index 1
        new_labels = []
        new_handles = []
        for i in range(len(labels)):
            new_labels.append("{:.2e}".format(tuples[i][1]))
            new_handles.append(tuples[i][0])
        plt.legend(new_handles,new_labels, fontsize = 24, loc=2)
    elif labels:
        plt.legend(fontsize = 24, loc=2)
        
    plt.autoscale()
    plt.savefig(f"{savename}", bbox_inches='tight')
    plt.show()
    plt.close()
  