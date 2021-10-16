"""
This file calls `plot_comparison_wrapper` from plotting_functions to create
comparison plots for all models, initial conditions, and metric types. 
"""

import sys
import cmath
import math
import os
import h5py
import matplotlib.pyplot as plt   # plots
plt.rcParams['figure.facecolor'] = 'w'

import models_dictionaries
import plotting_functions

#from matplotlib.mlab import griddata
plt.rcParams['figure.facecolor'] = 'w'

initial_states = ["excited", "ground"]
sets = [0, 1, 2, 3, 4, 5, 6, 7, 8]
coords = [0, 6]
trajs = [2000]
model_types = ["h_shift", "k", "k_aligned", "energy_gaps"]
params_sets = [models_dictionaries.params_h_shift, models_dictionaries.params_k, models_dictionaries.params_k_aligned, models_dictionaries.params_energy_gaps]

# this loop plots a comparison plot for each type of metric for each set of models at each initial condition with either type of NBRA
for type in ["population", "energy_gap", "coupling", "coherence"]:
    for model_type in model_types:
        for starting_state in initial_states:
            for coord in coords:
                if model_type == 'k_aligned' and coord == 6 or model_type == 'energy_gaps' and coord == 6:
                    continue # those models only run at coord 0 
                if model_type == "energy_gaps":
                    labels = "set" # they all have the same reorg energy
                else:
                    labels = "reorg"
                title = f"{model_type} models, {starting_state}, x$_0$ = {coord} \n {type}"
                savename = f"figures/comparison/{model_type}/{type}_{starting_state}_coord_{coord}_traj_2000.png"
                savename_mixed = f"figures/comparison/{model_type}/{type}_{starting_state}_mixed_coord_{coord}_traj_2000.png" 
                # "mixed" refers to different initial state for adiabatic trajectories and tsh
                filename = f"data/{model_type}_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                filename_mixed = f"data/{model_type}_mixed_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                plotting_functions.plot_comparison_wrapper([filename], [0,1,2,3,4,5,6,7,8], title, savename, integrated=1,
                         type = type, time_normalized = 1, labels = labels)
                plotting_functions.plot_comparison_wrapper([filename_mixed], [0,1,2,3,4,5,6,7,8], title, savename_mixed, integrated=1,
                         type = type, time_normalized = 1, labels = labels)

# this look make a plot for each metric that includes all models, initial conditions, and NBRA type
sets = [0,1,2,3,4,5,6,7,8]
for type in ["population", "energy_gap", "coupling", "coherence"]:
    filelist = []
    title = f'All Sets, {type.capitalize()} comparison'
    for model_type in model_types:
        for starting_state in initial_states:
            for coord in coords:
                if model_type == 'k_aligned' and coord == 6 or model_type == 'energy_gaps' and coord == 6:
                    continue
                if starting_state == "ground":
                    state_num = 0
                    mixed = 1
                else:
                    state_num = 1
                    mixed = 0                    
                filename = f"data/{model_type}_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                filelist.append(filename)
                filename = f"data/{model_type}_mixed_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                filelist.append(filename)

    plotting_functions.plot_comparison_wrapper(filelist, sets, title, f"figures/comparison/{type}_comparison_all.png", labels = 0, integrated=1,
                         type = type, time_normalized = 1)

# this loop creates a figure for each model type and metric type, including all initial conditions and NBRA types
for type in ["population", "energy_gap", "coupling", "coherence"]:
    for model_type in model_types:
        filelist = []
        labels = []
        title = f'All {model_type.capitalize()}, {type.capitalize()} Comparison'
        for starting_state in initial_states:
            for coord in coords:
                if model_type == 'k_aligned' and coord == 6 or model_type == 'energy_gaps' and coord == 6:
                    continue
                if starting_state == "ground":
                    state_num = 0
                    mixed = 1
                else:
                    state_num = 1
                    mixed = 0
                filename = f"data/{model_type}_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                filelist.append(filename)
                filename = f"data/{model_type}_mixed_{starting_state}_coord_{coord}_ntraj_2000.hdf5"
                filelist.append(filename)
        plotting_functions.plot_comparison_wrapper(filelist, sets, title, f"figures/comparison/{model_type}/{type}_comparison_all.png", labels = 0, integrated=1,
                             type = type, time_normalized = 1)