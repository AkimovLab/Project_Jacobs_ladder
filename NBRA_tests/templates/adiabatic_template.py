#!/usr/bin/env python
# coding: utf-8

# ### Setup

# In[ ]:


import sys
import cmath
import math
import os
import h5py

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

import libra_py.dynamics.tsh.compute as tsh_dynamics

if not os.path.isdir("../../out"):
    os.system("mkdir ../../out")

warnings.filterwarnings('ignore')

def compute_model(q, params, full_id):

    model = params["model"]
    res = None

    if model==1:
        res = Holstein.Holstein2(q, params, full_id)
    elif model==2:
        res = compute_model_nbra(q, params, full_id)
    elif model==3:
        res = Holstein.Holstein4(q, params, full_id)

    return res


def potential(q, params):
    """
    Thin wrapper of the model Hamiltonians that can be used in
    the fully-quantum calculations
    """

    # Diabatic properties
    obj = compute_model(q, params, Py2Cpp_int([0,0]))

    # Adiabatic properties
    nadi = len(params["E_n"])
    ndof = 1
    ham = nHamiltonian(nadi, nadi, ndof) # ndia, nadi, nnucl
    ham.init_all(2)


    ham.compute_diabatic(compute_model, q, params)
    ham.compute_adiabatic(1);


    obj.ham_adi = ham.get_ham_adi()
    obj.dc1_adi = CMATRIXList()

    for n in range(ndof):
        x = ham.get_dc1_adi(n)
        for i in range(nadi):
            for j in range(nadi):
                if i!=j:
                    #pass
                    if math.fabs(x.get(i,j).real)>1e+10:
                        x.set(i,j, 0.0+0.0j)
                        x.set(j,i, 0.0+0.0j)

        obj.dc1_adi.append( x )


    return obj


class tmp:
    pass

def compute_model_nbra(q, params, full_id):
    """

    Read in the vibronic Hamiltonians along the trajectories

    Args:
        q ( MATRIX(1,1) ): coordinates of the particle, ndof, but they do not really affect anything
        params ( dictionary ): model parameters

            * **params["timestep"]** ( int ):  [ index of the file to read ]
            * **params["prefix"]**   ( string ):  [ the directory where the hdf5 file is located ]
            * **params["filename"]** ( string ):  [ the name of the HDF5 file ]


    Returns:
        PyObject: obj, with the members:

            * obj.hvib_adi ( CMATRIX(n,n) ): adiabatic vibronic Hamiltonian

    """


    hvib_adi, basis_transform, time_overlap_adi = None, None, None

    Id = Cpp2Py(full_id)
    indx = Id[-1]
    timestep = params["timestep"]
    filename = params["filename"]

    with h5py.File(F"{filename}", 'r') as f:

        nadi = int(f["hvib_adi/data"].shape[2] )

        #============ Vibronic Hamiltonian ===========
        hvib_adi = CMATRIX(nadi, nadi)
        for i in range(nadi):
            for j in range(nadi):
                hvib_adi.set(i,j, complex( f["hvib_adi/data"][timestep, indx, i, j]) )


        #=========== Basis transform, if available =====
        basis_transform = CMATRIX(nadi, nadi)
        for i in range(nadi):
            for j in range(nadi):
                basis_transform.set(i,j, complex( f["basis_transform/data"][timestep, indx, i, j]) )


        #========= Time-overlap matrices ===================
        time_overlap_adi = CMATRIX(nadi, nadi)
        for i in range(nadi):
            for j in range(nadi):
                time_overlap_adi.set(i,j, complex( f["St/data"][timestep, indx, i, j]) )

    obj = tmp()
    obj.hvib_adi = hvib_adi
    obj.basis_transform = basis_transform
    obj.time_overlap_adi = time_overlap_adi


    return obj


def run_tsh(common_params, model_params, prefix):

    params = dict(common_params)


    # Random numbers generator object
    rnd = Random()

    #============ Initialize dynamical variables ==================
    x0 = params["x0"]
    p0 = params["p0"]
    masses = params["masses"]
    k0 = params["k"]
    ntraj = params["ntraj"]
    nstates = params["nstates"]

    # Nuclear
    init_nucl = {"init_type":3, "force_constant":k0, "ntraj":ntraj}
    q, p, iM = tsh_dynamics.init_nuclear_dyn_var(x0, p0, masses, init_nucl, rnd)

    # Electronic
    istate = params["istate"]
    istates = []
    for i in range(nstates):
        istates.append(0.0)
    istates[ istate[1] ] = 1.0
    _init_elec = { "init_type":3, "nstates":nstates, "istates":istates, "rep":istate[0],  "ntraj":ntraj   }


    #============= Dynamical variables ==============
    dyn_params = dict(common_params)

    # This should update only the properties that aren't defined, but not override the existing values!
    critical_params = [  ]
    default_params = { "prefix":prefix, "mem_output_level":4 }
    comn.check_input(dyn_params, default_params, critical_params)

    _model_params = dict(model_params)
    _model_params.update({"model0": model_params["model"] })

    res = tsh_dynamics.generic_recipe(q, p, iM, dyn_params, compute_model, _model_params,_init_elec, rnd)







couplings = [ [0.0, 0.001],
              [0.001, 0.0] ]

params_h_shift = [{"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 4],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5.5],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 6],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 6.5],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 7],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 8],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 8.5],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
                  {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 9],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2}]

params_k = [{"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.0065],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.006],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.0055],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.005],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.0045],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.003],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.0025],
                "V":couplings,
                "nstates":2},
            {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.002],
                "V":couplings,
                "nstates":2}]


couplings_list = [0.01, 0.0075, 0.005, 0.0025, 0.001, 0.00075, 0.0005, 0.00025, 0.0001]

couplings_0 = [ [0.0, couplings_list[0]],
              [couplings_list[0], 0.0] ]

couplings_1 = [ [0.0, couplings_list[1]],
              [couplings_list[1], 0.0] ]

couplings_2 = [ [0.0, couplings_list[2]],
              [couplings_list[2], 0.0] ]

couplings_3 = [ [0.0, couplings_list[3]],
              [couplings_list[3], 0.0] ]

couplings_4 = [ [0.0, couplings_list[4]],
              [couplings_list[4], 0.0] ]

couplings_5 = [ [0.0, couplings_list[5]],
              [couplings_list[5], 0.0] ]

couplings_6 = [ [0.0, couplings_list[6]],
              [couplings_list[6], 0.0] ]

couplings_7 = [ [0.0, couplings_list[7]],
              [couplings_list[7], 0.0] ]

couplings_8 = [ [0.0, couplings_list[8]],
              [couplings_list[8], 0.0] ]

params_energy_gaps = [{"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_0,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_1,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_2,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_3,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_4,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_5,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_6,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_7,
                "nstates":2},
                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 5],
                "k_n":[0.002, 0.004],
                "V":couplings_8,
                "nstates":2},
                ]

couplings = [ [0.0, 0.001],
              [0.001, 0.0] ]
params_k_aligned = [{"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.006],
                "V":couplings,
                "nstates":2},

                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.005],
                "V":couplings,
                "nstates":2},


              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.004],
                "V":couplings,
                "nstates":2},

              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.003],
                "V":couplings,
                "nstates":2},

              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.002],
                "V":couplings,
                "nstates":2},


              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.0045],
                "V":couplings,
                "nstates":2},

              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.0055],
                "V":couplings,
                "nstates":2},

              {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.0025],
                "V":couplings,
                "nstates":2},


                {"model":3,
                "E_n":[0.0,  0.0],
                "x_n":[3, 3],
                "k_n":[0.002, 0.0065],
                "V":couplings,
                "nstates":2}
                ]

def model_parameter_energy_gap(params):
    # this only works for 2 state systems
    file = params["ref_prefix"]

    with h5py.File(f'{file}/mem_data.hdf', 'r') as f:
        hvib = np.array(f['hvib_adi/data']) # [timestep][traj][i][j]
    timesteps = (np.shape(hvib))[0]
    ntraj = (np.shape(hvib))[1]

    sum_over_time = 0.0
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            metric = abs(hvib[timestep][traj][0][0] - hvib[timestep][traj][1][1])
            sum_over_traj += metric
        sum_over_time += sum_over_traj / ntraj
    sum_over_time = math.sqrt(sum_over_time / timesteps)
    return sum_over_time

m, k = 2000.0, 0.001

common_params = { "rep_ham":0, "force_method":1,  "nac_update_method":1,
                  "tsh_method":0, "hop_acceptance_algo":20,   "momenta_rescaling_algo":201,
                  "nsteps":4000, "dt":10.0,
                  "p0":[0.0],
                  "masses":[m],
                  "k":[k],
                  "nstates":2, "istate":[1, 0],
                  "which_adi_states":range(2), "which_dia_states":range(2)}

istates = ["ISTATE_REPLACE"]
initial_coords = [COORD_REPLACE]
trajs = [TRAJ_REPLACE]
numbers = [NUMBER_REPLACE]
sets = [SET_REPLACE]
param_sets = params_MODEL_TYPE_REPLACE
model_types = ["MODEL_TYPE_REPLACE"]

for model_type in model_types:
    for i in sets:
        for istate in istates:
            for coord in initial_coords:
                for traj in trajs:
                    for number in numbers:
                        if istate == "excited":
                            common_params.update({"istate":[1, 1], "ntraj":traj})
                        else:
                            common_params.update({"istate":[1, 0], "ntraj":traj})

                        name = f'{model_type}_{istate}_coord_{coord}_set_{i}_ntraj_{traj}_number_{number}'
                        params_adiabatic = dict(common_params)
                        params_adiabatic.update({ "tsh_method":-1, "x0":[coord]})
                        run_tsh(params_adiabatic, param_sets[i], f"../../out/adiabatic_md_{name}")
