import sys
import cmath
import math
import os
import h5py
import matplotlib.pyplot as plt   # plots
import numpy as np
import time
import warnings

from liblibra_core import *
import util.libutil as comn
from libra_py import units
import libra_py.models.Holstein as Holstein
import libra_py.models.Morse as Morse
from libra_py import dynamics_plotting
import libra_py.dynamics.tsh.compute as tsh_dynamics
import libra_py.dynamics.tsh.plot as tsh_dynamics_plot

import libra_py.dynamics.exact.compute as dvr
import libra_py.dynamics.exact.save as dvr_save

import libra_py.data_savers as data_savers
import argparse

#from matplotlib.mlab import griddata
#%matplotlib inline 
warnings.filterwarnings('ignore')

colors = {}
colors.update({"11": "#8b1a0e"})  # red       
colors.update({"12": "#FF4500"})  # orangered 
colors.update({"13": "#B22222"})  # firebrick 
colors.update({"14": "#DC143C"})  # crimson   
colors.update({"21": "#5e9c36"})  # green
colors.update({"22": "#006400"})  # darkgreen  
colors.update({"23": "#228B22"})  # forestgreen
colors.update({"24": "#808000"})  # olive      
colors.update({"31": "#8A2BE2"})  # blueviolet
colors.update({"32": "#00008B"})  # darkblue  
colors.update({"41": "#2F4F4F"})  # darkslategray

clrs_index = ["11", "21", "31", "41", "12", "22", "32", "13","23", "14", "24"]

def compute_model(q, params, full_id):

    model = params["model"]
    res = None
    
    if model==1:        
        res = Holstein.Holstein2(q, params, full_id) 
    elif model==2:
        pass #res = compute_model_nbra(q, params, full_id)
    elif model==3:
        pass #res = compute_model_nbra_files(q, params, full_id)        
    elif model==4:
        res = Morse.general(q, params, full_id)    

    return res

def potential(q, params):
    full_id = Py2Cpp_int([0,0]) 
    
    return compute_model(q, params, full_id)

#parser = argparse.ArgumentParser(description="Args for exact dynamics using Libra...")
#parser.add_argument("--nsteps", default=2500, type=int) 
#action="store_true", help="Flag to do something")
#parser.add_argument("--dx", default=0.025, type=float) 
#parser.add_argument("--dt", default=10.0, type=float) 
#parser.add_argument("--model-indx", default=1, type=int)
#args = parser.parse_args()

dt = 10.0
dx = 0.025
nsteps = 2500
model_indx = 0

model_params1 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.000, "nstates":2}
model_params2 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.001, "nstates":2}
model_params3 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.01, "nstates":2}
model_params4 = {"model":1, "model0":1, "E_n":[0.0,  -0.01], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.01, "nstates":2}

all_model_params = [model_params1, model_params2, model_params3, model_params4]

#model_indx = args.model_indx
model_params = all_model_params[model_indx]

exact_params = { "nsteps": nsteps, "dt": dt, "progress_frequency":1.0/nsteps,
                 "rmin":[-15.0], "rmax":[15.0], "dx":[dx], "nstates":2,
                  "x0":[-4.0], "p0":[0.0], "istate":[1, 0], "masses":[2000.0], "k":[0.01],
                  "integrator":"SOFT",
                  "mem_output_level":0, "txt_output_level":0, "txt2_output_level":0, "hdf5_output_level":2, 
                  "properties_to_save":[ "timestep", "time", "Epot_dia", "Ekin_dia", "Etot_dia",
                                         "Epot_adi", "Ekin_adi", "Etot_adi", "norm_dia", "norm_adi",
                                         "pop_dia", "pop_adi", "q_dia", "q_adi", "p_dia", "p_adi" ],
                  "prefix": F"exact-model-{model_indx}-dt-{dt}-dx-{dx}-nsteps-{nsteps}", "prefix2": F"exact-model-{model_indx}-dt-{dt}-dx-{dx}-nsteps-{nsteps}", 
                  "use_compression":0, "compression_level":[0, 0, 0]
               }

wfc = dvr.init_wfc(exact_params, potential, model_params)
savers = dvr_save.init_tsh_savers(exact_params, model_params, exact_params["nsteps"], wfc)
dvr.run_dynamics(wfc, exact_params, model_params, savers)


