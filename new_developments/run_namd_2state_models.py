import os
import sys
import math
import time

import multiprocessing as mp
import numpy as np
import matplotlib.pyplot as plt

from liblibra_core import *
import util.libutil as comn
from libra_py import units as units
from libra_py import data_conv, data_stat, data_outs, data_read
import libra_py.workflows.nbra.decoherence_times as decoherence_times
import libra_py.workflows.nbra.step4 as step4
import libra_py.models.Holstein as Holstein
import libra_py.models.Esch_Levine as EL
import libra_py.dynamics.tsh.compute as tsh
import libra_py.dynamics.tsh.recipes as recipes

def get_all(nstates, prefix):

    Hadi, Hvib, nac, St = [], [], [], []
    dummy = MATRIX(nstates, nstates)

 
    tmp = data_read.get_data_from_file2(F"{prefix}/hvib_adi.txt", list(range(2*nstates*nstates)) )
    tmp2 = data_read.get_data_from_file2(F"{prefix}/St.txt", list(range(2*nstates*nstates)) )
    nsteps = len(tmp[0])

    for step in range(nsteps):
        # Hvib
        hvib = CMATRIX(nstates, nstates)
        for i in range(nstates):
            for j in range(nstates):
                re = tmp[2*(i*nstates+j) + 0][step]
                im = tmp[2*(i*nstates+j) + 1][step]
                hvib.set(i, j, re+1j*im)
        Hvib.append(hvib)

        # Hadi
        Hadi.append( CMATRIX(hvib.real(), dummy) )

        # NAC
        nac.append( CMATRIX(-1.0*hvib.imag(), dummy) )

        # St
        st = CMATRIX(nstates, nstates)
        for i in range(nstates):
            for j in range(nstates):
                re = tmp2[2*(i*nstates+j) + 0][step]
                im = tmp2[2*(i*nstates+j) + 1][step]
                st.set(i, j, re+1j*im)
        St.append(st)

    return Hadi, Hvib, nac, St


class tmp:
    pass

def compute_model_nbra_files(q, params, full_id):
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
                                    
    timestep = params["timestep"]
    
    #=========== Basis transform, if available =====
    basis_transform = CMATRIX(2, 2)            
    basis_transform.identity()        
                                                
    #========= Time-overlap matrices ===================
    #time_overlap_adi = CMATRIX(2, 2)            
    #time_overlap_adi.identity()    
        
    obj = tmp()
    obj.ham_adi = params["HADI"][timestep]
    obj.nac_adi = params["NAC"][timestep]
    obj.hvib_adi = params["HVIB"][timestep]
    obj.basis_transform = basis_transform
    obj.time_overlap_adi = params["ST"][timestep]
            
    return obj






def compute_model(q, params, full_id):
    model = params["model"]
    res = None    

    if model==1:        
        res = EL.JCP_2020(q, params, full_id)
    elif model==2:
        res = Holstein.Holstein5(q, params, full_id)
    elif model==3:
        res = compute_model_nbra_files(q, params, full_id)

    return res



def main():
    
    nthreads = 4
    methods_map = {0:"FSSH", 1:"IDA", 2:"mSDM", 3:"DISH" }
    init_states = [1]
    methods = [0]
    batches = list(range(1))

    #================== SET UP THE DYNAMICS AND DISTRIBUTED COMPUTING SCHEME  ===============                      

    rnd = Random()   
    # Time overlap method = 0 = genuine dynamics
   
    dyn_params = { "nsteps":1999, "dt":0.1*units.fs2au, 
                   "ntraj":25, "x0":[-1.0], "p0":[10.0], "masses":[1822.0], "k":[0.01], 
                   "nstates":2, "istate":[1, 0],
                   "which_adi_states":range(2), "which_dia_states":range(2),
                   "time_overlap_method":1, "mem_output_level":-1,  "txt_output_level":4,
                   "properties_to_save": ['timestep', 'time', 'SH_pop', 'SH_pop_raw', 'hvib_adi', 'q', 'p', "Ekin_ave", "Epot_ave", 
                                          'Etot_ave', 'Cadi', 'projector', 'states', 'St' ],
                   "state_tracking_algo":2, "convergence":0,  "max_number_attempts":1000, "min_probability_reordering":0.01,
                   "do_phase_correction":1,
                   "decoherence_algo":0, "Temperature": 300.0                    
                 }
    print(dyn_params)

    model_params = {"nstates":2, "filename":None, "istep":0, "E_n":[0.0,  -0.001], "x_n":[0.0, 4.0], 
                    "k_n":[0.002, 0.004], "V": [ [0.0, 0.001],  [0.001, 0.0] ],
                    "alpha": [ [0.00, 0.00], [0.00, 0.00] ],  "x_nm": [ [0.00, 0.00], [0.00, 0.00] ] ,
                    "w0":0.25, "w1":0.25, "eps":0.0, "i_crit":0, "delta":0.0
                   }

    model_params.update({"model":1, "V":0.00})    # LZ type
    #model_params.update({"model":2})             # Holstein
    print(model_params)


    Hadi, Hvib, nac, St = get_all(2, "adia")
    model_params.update({"model":3, "HVIB":Hvib, "HADI":Hadi, "NAC":nac, "ST":St })
    

    # FSSH 
    # ham_rep, is_nbra = 0, 0  # non-NBRA
    ham_rep, is_nbra = 1, 1 # file-based NBRA
    #ham_rep, is_nbra = 0, 2 # on-the-fly NBRA

    os.system("mkdir FSSH")
    dyn_params.update({ "dir_prefix":"FSSH" })
    step4.namd_workflow(dyn_params, compute_model, model_params, rnd, nthreads, 
                        methods_map, init_states, methods, batches, "fork", True, ham_rep, is_nbra)

    #step4.nice_plots(dyn_params, init_states, methods, methods_map, batches, fig_label="FSSH")


main()


