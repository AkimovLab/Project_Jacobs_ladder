"""
This file contains all functions required for comparing TSH data. The functions for
calculating the four metrics are here as well as the function for computing the
reorganziaton energy and its dependencies. The time normalizing function is also here.

"""

import sys
import numpy as np
import math
import h5py
import matplotlib.pyplot as plt   # plots

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *

import util.libutil as comn
from libra_py import units
import libra_py.models.Holstein as Holstein

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

def reorg_energy(_compute_model, _param_sets, states_of_interest, xmin, xmax, dx, _ndof=1, _active_dof=0, _all_coordinates=[0.0]):


    X = []
    nsteps = int((xmax - xmin) / dx) + 1

    for i in range(nsteps):
        X.append(xmin + i * dx)




    sz = len(_param_sets)
    for iset in range(sz):

        # The "nstates" field must be specified
        comn.check_input(_param_sets[iset], {}, ["nstates"])
        n = _param_sets[iset]["nstates"]
        nstates = n

        ham = nHamiltonian(nstates, nstates, _ndof) # ndia, nadi, nnucl
        ham.init_all(2)


        hdia, hadi  = [], []
        uij = []              # projecitions of the MOs onto elementary basis

        for k1 in range(nstates):
            hdia.append([])
            uij_k1 = []
            for k2 in range(nstates):
                uij_k1.append([])
            uij.append(uij_k1)


        for i in range(nsteps):

            scan_coord = MATRIX(_ndof, 1);
            for j in range(_ndof):
                scan_coord.set(j, 0, _all_coordinates[j])
            scan_coord.set(_active_dof, 0, X[i])

            # Diabatic properties
            ham.compute_diabatic(_compute_model, scan_coord, _param_sets[iset])


            for k1 in range(nstates):
                hdia[k1].append(ham.get_ham_dia().get(k1, k1).real)



        nstates = len(hdia)
        reorg_E = []
        for i in range(nstates):
            for j in range(nstates):
                if i != j:
                    X_at_min_i = hdia[i].index(min(hdia[i]))
                    X_at_min_j = hdia[j].index(min(hdia[j]))
                    reorg = abs(hdia[i][X_at_min_i] - hdia[i][X_at_min_j])

                    reorg_E.append(reorg)

        return reorg_E

def time_normalize(data, dt):
    # use dt that will be used for plotting (i.e. in a.u. or fs)
    timesteps = len(data)
    for i in range(timesteps):
        data[i] = data[i] / ((i+1) * dt)
    return data

def population_metric(params):

    ref_prefix = params["ref_prefix"]
    test_prefix =  params["test_prefix"]

    with h5py.File(F"{ref_prefix}/mem_data.hdf", 'r') as f:
        reference_pop = np.array(f['SH_pop_raw/data'])
    with h5py.File(F"{test_prefix}/mem_data.hdf", 'r') as f:
        comparison_pop = np.array(f['SH_pop_raw/data'])
    print(np.shape(reference_pop))
    timesteps = (np.shape(reference_pop))[0]
    nstates = (np.shape(reference_pop))[1]

    # note that the saved population data is already trajectory averaged,
    # so we don't loop over trajectories
    metric_at_timesteps = []
    for timestep in range(timesteps):
        sum_over_states = 0.0
        for i in range(nstates):
            ref = reference_pop[timestep][i][0]
            comp = comparison_pop[timestep][i][0]
            sum_over_states += (abs(comp - ref))**2
        sum_over_states = math.sqrt(sum_over_states / nstates)
        metric_at_timesteps.append(sum_over_states)
    return metric_at_timesteps

def coherence_metric(params):

    #[F"{pop_type}/data"][timesteps, istate, istate]

    ref_prefix = params["ref_prefix"]
    test_prefix =  params["test_prefix"]

    with h5py.File(F"{ref_prefix}/mem_data.hdf", 'r') as f:
        reference_pop = np.array(f['D_adi_raw/data'])
    with h5py.File(F"{test_prefix}/mem_data.hdf", 'r') as f:
        comparison_pop = np.array(f['D_adi_raw/data'])

    timesteps = (np.shape(reference_pop))[0]
    nstates = (np.shape(reference_pop))[1]

    metric_at_timesteps = []
    for timestep in range(timesteps):
        sum_over_states = 0.0
        cnt = 0
        for i in range(nstates):
            for j in range(nstates):
                if i < j:
                    ref = reference_pop[timestep][i][j]
                    comp = comparison_pop[timestep][i][j]
                    sum_over_states += (abs(comp - ref))**2
                    cnt += 1
        sum_over_states = math.sqrt(sum_over_states / cnt)
        metric_at_timesteps.append(sum_over_states)

    return metric_at_timesteps

def coupling_metric(params):

    reference_file = params["ref_prefix"]
    comparison_file =  params["test_prefix"]

    with h5py.File(f'{reference_file}/mem_data.hdf', 'r') as f:
        reference_hvib = np.array(f['hvib_adi/data']) # [timestep][traj][i][j]
    with h5py.File(f'{comparison_file}/mem_data.hdf', 'r') as f:
        comparison_hvib = np.array(f['hvib_adi/data'])
    print(np.shape(reference_hvib))
    timesteps = (np.shape(reference_hvib))[0]
    ntraj = (np.shape(reference_hvib))[1]
    nstates = (np.shape(reference_hvib))[2]

    # hvib is not already trajectory averaged, so we loop over trajectories here
    metric_at_timesteps = []
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            sum_over_states = 0.0
            cnt = 0
            for i in range(nstates):
                for j in range(nstates):
                    if i < j:
                        ref = reference_hvib[timestep][traj][i][j]
                        comp = comparison_hvib[timestep][traj][i][j]
                        sum_over_states += (abs(comp - ref))**2
                        cnt += 1
            sum_over_traj += sum_over_states / cnt
        metric_at_timesteps.append(math.sqrt(sum_over_traj / ntraj))

    return metric_at_timesteps

def energy_gap_metric(params):

    reference_file = params["ref_prefix"]
    comparison_file =  params["test_prefix"]

    with h5py.File(f'{reference_file}/mem_data.hdf', 'r') as f:
        reference_hvib = np.array(f['hvib_adi/data']) # [timestep][traj][i][j]
    with h5py.File(f'{comparison_file}/mem_data.hdf', 'r') as f:
        comparison_hvib = np.array(f['hvib_adi/data'])
    timesteps = (np.shape(reference_hvib))[0]
    ntraj = (np.shape(reference_hvib))[1]
    nstates = (np.shape(reference_hvib))[2]

    metric_at_timesteps = []
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            sum_over_states = 0.0
            for i in range(nstates):
                ref = reference_hvib[timestep][traj][i][i]
                comp = comparison_hvib[timestep][traj][i][i]
                sum_over_states += (abs(comp - ref))**2
            sum_over_traj += sum_over_states / nstates
        metric_at_timesteps.append(math.sqrt(sum_over_traj / ntraj))

    return metric_at_timesteps

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

def model_parameter_coupling(params):
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
            metric = abs(hvib[timestep][traj][0][1])
            sum_over_traj += metric
        sum_over_time += sum_over_traj / ntraj
    sum_over_time = math.sqrt(sum_over_time / timesteps)

    return sum_over_time

def model_parameter_coupling_modified(params):
    # |coupling|^2 * exp(- dE/kT)
    # this only works for 2 state systems
    k = 1.38*(10**-23)
    T = 300
    file = params["ref_prefix"]

    with h5py.File(f'{file}/mem_data.hdf', 'r') as f:
        hvib = np.array(f['hvib_adi/data']) # [timestep][traj][i][j]
    timesteps = (np.shape(hvib))[0]
    ntraj = (np.shape(hvib))[1]

    sum_over_time = 0.0
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            metric = abs(hvib[timestep][traj][0][1])**2 * math.exp(-1 * abs(hvib[timestep][traj][0][0] - hvib[timestep][traj][1][1]) / (k*T))
            sum_over_traj += metric
        sum_over_time += sum_over_traj / ntraj
    sum_over_time = math.sqrt(sum_over_time / timesteps)

    return sum_over_time

def model_parameter_coupling_diabatic(params):
    # this only works for 2 state systems
    file = params["ref_prefix"]

    with h5py.File(f'{file}/mem_data.hdf', 'r') as f:
        hvib = np.array(f['hvib_dia/data']) # [timestep][traj][i][j]
    timesteps = (np.shape(hvib))[0]
    ntraj = (np.shape(hvib))[1]

    sum_over_time = 0.0
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            metric = abs(hvib[timestep][traj][0][1])
            sum_over_traj += metric
        sum_over_time += sum_over_traj / ntraj
    sum_over_time = math.sqrt(sum_over_time / timesteps)

    return sum_over_time

def model_parameter_energy_gap_fluctuations(params, energy_gap_param):
    # this only works for 2 state systems
    #  delE = srt( < (dE - <dE> )^2 >)
    file = params["ref_prefix"]

    with h5py.File(f'{file}/mem_data.hdf', 'r') as f:
        hvib = np.array(f['hvib_adi/data']) # [timestep][traj][i][j]
    timesteps = (np.shape(hvib))[0]
    ntraj = (np.shape(hvib))[1]

    sum_over_time = 0.0
    for timestep in range(timesteps):
        sum_over_traj = 0.0
        for traj in range(ntraj):
            metric = ((abs(hvib[timestep][traj][0][0] - hvib[timestep][traj][1][1])) - energy_gap_param)**2
            sum_over_traj += metric
        sum_over_time += sum_over_traj / ntraj
    sum_over_time = math.sqrt(sum_over_time / timesteps)

    return sum_over_time
