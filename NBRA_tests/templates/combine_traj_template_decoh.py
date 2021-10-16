import sys
import cmath
import math
import os
import h5py
import numpy as np


def combine_trajectories(file_list, newfile, data_types = ["SH_pop_raw", "SH_pop", "D_adi", "D_adi_raw"], data_types_traj = ["hvib_adi", "hvib_dia", "states", "projector"]):
    # first, average data sets that are already trajectory averaged,
    # and therefore a stored as one trajectory
    # these data types are defined by argument `data_types`
    with h5py.File(f'{newfile}', 'w') as f:
        #f.create_dataset("files_combined", data = file_list)
        pass

    nsets = len(file_list)


    for data_type in data_types:
        datasets = []
        for file in file_list:
            with h5py.File(f'{file}', 'r') as f:
                datasets.append(np.array(f[f"{data_type}/data"])) #[time, state, 1]
                shape = f[f"{data_type}/data"].shape
        nsteps = shape[0]
        nstates = shape[1]
        nstates_2 = shape[2]
        new_dataset = np.empty((nsteps, nstates, nstates_2))
        for step in range(nsteps):
            for state in range(nstates):
                for state_2 in range(nstates_2):
                    sum = 0
                    for i in range(nsets):
                        sum += datasets[i][step,state,state_2]
                    new_dataset[step,state,state_2] = sum / nsets
        with h5py.File(f'{newfile}', 'a') as f:
            f.create_dataset(f"{data_type}/data", data = new_dataset)


    # now we take datasets that weren't trajectory averaged and append
    # all trajectories to a single dataset
    for data_type in data_types_traj:
        with h5py.File(f'{file_list[0]}', 'r') as f:
            new_array = np.array(f[f'{data_type}/data'])
        for file in file_list[1:]:
            with h5py.File(f'{file}', 'r') as f:
                new_array = np.append(new_array, np.array(f[f'{data_type}/data']), axis=1)
        with h5py.File(f'{newfile}', 'a') as f:
            f.create_dataset(f"{data_type}/data", data = new_array)

    with h5py.File(f'{file_list[0]}', 'r') as f:
        time = (np.array(f[f"time/data"])) #[time, state, 1]
    with h5py.File(f'{newfile}', 'a') as f:
        f.create_dataset("time/data", data = time)
    return

tuple_sets = [ [(250, 1), (250, 2), (250, 3), (250, 4)] ]

istates = ["ISTATE_REPLACE"]
sets = [SET_REPLACE]
coords = [COORD_REPLACE]
dyn_types = ["DYN_REPLACE"]
model_types = ["MODEL_TYPE_REPLACE"]
templates = ["TEMPLATE_REPLACE"]

for model_type in model_types:
    for dyn_type in dyn_types:
        for istate in istates:
            for coord in coords:
                for set in sets:
                    for template in templates:
                        for tuple_set in tuple_sets:
                            filelist = []
                            new_traj = 0
                            for tuple in tuple_set:
                                filelist.append(f"../../out/{dyn_type}_{template}_{model_type}_{istate}_coord_{coord}_set_{set}_ntraj_{tuple[0]}_number_{tuple[1]}/mem_data.hdf")
                                new_traj += tuple[0]
                            location = f"../../out/{dyn_type}_{template}_{model_type}_{istate}_coord_{coord}_set_{set}_ntraj_{new_traj}_number_1"

                            if os.path.isfile(f"{location}/mem_data.hdf"):
                                os.system(f"rm {location}/mem_data.hdf")
                                combine_trajectories(filelist, f"{location}/mem_data.hdf")
                            else:
                                if not os.path.isdir(location):
                                    os.system(f"mkdir {location}")
                                combine_trajectories(filelist, f"{location}/mem_data.hdf")
