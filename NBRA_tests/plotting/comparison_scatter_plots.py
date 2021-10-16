import sys
import os
sys.path.insert(1, '../import_files')
import models_dictionaries
import comparison_functions
import plotting_functions


initial_states = ["excited", "ground"]
sets = [0, 1, 2, 3, 4, 5, 6, 7, 8]
coords = [0, 6]
trajs = [2000]
model_types = ["h_shift", "k", "k_aligned", "energy_gaps"]
params_sets = [models_dictionaries.params_h_shift, models_dictionaries.params_k, models_dictionaries.params_k_aligned, models_dictionaries.params_energy_gaps]

if not os.path.isdir("../figures"):
    os.system("mkdir ../figures")
if not os.path.isdir("../figures/scatter"):
    os.system("mkdir ../figures/scatter")


# all groups
NBRA_0 = []
NBRA_1 = []
coord_0 = []
coord_6 = []
excited = []
ground = []


for model_type in model_types:
    for coord in coords:
        if model_type == 'k_aligned' and coord == 6 or model_type == 'energy_gaps' and coord == 6:
            continue

        filename = f"../data/{model_type}_ground_coord_{coord}_ntraj_1200.hdf5"
        NBRA_0.append(filename)
        filename = f"../data/{model_type}_mixed_excited_coord_{coord}_ntraj_1200.hdf5"
        NBRA_0.append(filename)

        filename = f"../data/{model_type}_mixed_ground_coord_{coord}_ntraj_1200.hdf5"
        NBRA_1.append(filename)
        filename = f"../data/{model_type}_excited_coord_{coord}_ntraj_1200.hdf5"
        NBRA_1.append(filename)


        filename = f"../data/{model_type}_ground_coord_{coord}_ntraj_1200.hdf5"
        ground.append(filename)
        filename = f"../data/{model_type}_mixed_ground_coord_{coord}_ntraj_1200.hdf5"
        ground.append(filename)

        filename = f"../data/{model_type}_mixed_excited_coord_{coord}_ntraj_1200.hdf5"
        excited.append(filename)
        filename = f"../data/{model_type}_excited_coord_{coord}_ntraj_1200.hdf5"
        excited.append(filename)

for model_type in model_types:
    for initial_state in initial_states:
        if model_type == 'k_aligned' and coord == 6 or model_type == 'energy_gaps' and coord == 6:
            continue
        filename = f"../data/{model_type}_{initial_state}_coord_0_ntraj_1200.hdf5"
        coord_0.append(filename)
        filename = f"../data/{model_type}_mixed_{initial_state}_coord_0_ntraj_1200.hdf5"
        coord_0.append(filename)
        filename = f"../data/{model_type}_{initial_state}_coord_6_ntraj_1200.hdf5"
        coord_6.append(filename)
        filename = f"../data/{model_type}_mixed_{initial_state}_coord_6_ntraj_1200.hdf5"
        coord_6.append(filename)

all_files = NBRA_0 + NBRA_1
y_types = ["population", "coherence"]
x_types = ["coupling", "energy_gap", "reorg", "energy_gap_fluctuations", "coupling_modifed", "coupling_diabatic"]
for x in x_types:
    for y in y_types:
        plotting_functions.plot_scatter({"NBRA 0": NBRA_0, "NBRA 1": NBRA_1}, sets, f"../figures/scatter/NBRA_groups_{y}_vs_{x}.png", x_type = x, y_type = y)
        plotting_functions.plot_scatter({"coord 0": coord_0, "coord 6": coord_6}, sets, f"../figures/scatter/coord_groups_{y}_vs_{x}.png", x_type = x, y_type = y)
        plotting_functions.plot_scatter({"excited": excited, "ground": ground}, sets, f"../figures/scatter/istate_groups_{y}_vs_{x}.png", x_type = x, y_type = y)
        plotting_functions.plot_scatter({"all": all_files}, sets, f"../figures/scatter/all_{y}_vs_{x}.png", x_type = x, y_type = y)
