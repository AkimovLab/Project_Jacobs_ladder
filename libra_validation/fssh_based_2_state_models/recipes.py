import os
import sys

def set_recipe(recipe):

    # Format for the `recipe` (int list)

    name = ""
    params = { "rep_ham":0 }                              # Hamiltonian is definied in the diabatic basis initially
    params.update( {"force_method":1, "rep_force":1} )    # state-specific forces, compute them in the adiabatic rep
    params.update( {"nac_update_method":1} )              # update NACs based on derivative couplings and momenta
    params.update( {"time_overlap_method":0} )            # state-tracking based on the on-the-fly time-overlaps                         


    # ======= Hop proposal algo ======
    if recipe[0] == 0:
        name = F"{name}_FSSH"
        params.update( {"tsh_method": 0} )                    # FSSH prop algo 


    # ======= Hop acceptance =========
    if recipe[1] == 0:
        name = F"{name}_E"
        params.update( {"hop_acceptance_algo":10} )           # acceptance on the adiabatic energy conservation
    elif recipe[1] == 1:
        name = F"{name}_D"
        params.update( {"hop_acceptance_algo":20} )           # acceptance on the ability to rescale along NAC
    elif recipe[1] == 2:
        name = F"{name}_F"
        params.update( {"hop_acceptance_algo":21} )           # acceptance on the ability to rescale along dF
    elif recipe[1] == 3:
        name = F"{name}_B"
        params.update( {"hop_acceptance_algo":31} )           # acceptance with Boltzmann probability


    # ======= Velocity rescaling =========
    if recipe[2] == 0:
        name = F"{name}_V+"
        params.update( {"momenta_rescaling_algo":100} )          # rescale along V, no reversal on frustr. hops
    elif recipe[2] == 1:
        name = F"{name}_V-"
        params.update( {"momenta_rescaling_algo":101} )          # rescale along V, reversal on frustr. hops
    elif recipe[2] == 2:
        name = F"{name}_D+"
        params.update( {"momenta_rescaling_algo":200} )          # rescale along D, no reversal on frustr. hops
    elif recipe[2] == 3:
        name = F"{name}_D-"
        params.update( {"momenta_rescaling_algo":201} )          # rescale along D, reversal on frustr. hops
    elif recipe[2] == 4:
        name = F"{name}_F+"
        params.update( {"momenta_rescaling_algo":210} )          # rescale along dF, no reversal on frustr. hops
    elif recipe[2] == 5:
        name = F"{name}_F-"
        params.update( {"momenta_rescaling_algo":211} )          # rescale along dF, reversal on frustr. hops


    # ======= Decoherence options =========
    if recipe[3] == 0:
        name = F"{name}_no_decoh"
        params.update( {"decoherence_algo":-1 } )             # no decoherence
        params.update( {"decoherence_times_type":-1 } )       # no need for dephasing times
        params.update( {"dephasing_informed":0 } )            # no deph-informed

    elif recipe[3] == 1:
        name = F"{name}_IDA"
        params.update( {"decoherence_algo":1 } )              # IDA
        params.update( {"decoherence_times_type":-1 } )       # no need for dephasing times
        params.update( {"dephasing_informed":0 } )            # no deph-informed - doesn't matter

    elif recipe[3] == 2:
        name = F"{name}_mSDM_user_tau"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":0 } )        # provided by user
        params.update( {"dephasing_informed":0 } )            # no deph-informed

    elif recipe[3] == 3:
        name = F"{name}_mSDM_user_tau_deph-inf"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":0 } )        # provided by user
        params.update( {"dephasing_informed":1 } )            # deph-informed

    elif recipe[3] == 4:
        name = F"{name}_mSDM_EDC"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":0 } )        # EDC
        params.update( {"dephasing_informed":0 } )            # no deph-informed

    elif recipe[3] == 5:
        name = F"{name}_mSDM_EDC_deph-inf"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":0 } )        # EDC
        params.update( {"dephasing_informed":1 } )            # deph-informed
     
    elif recipe[3] == 6:
        name = F"{name}_mSDM_Schwartz"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":3 } )        # Schwartz
        params.update( {"dephasing_informed":0 } )            # no deph-informed

    elif recipe[3] == 7:
        name = F"{name}_mSDM_Schwartz_deph-inf"
        params.update( {"decoherence_algo":0 } )              # mSDM
        params.update( {"decoherence_times_type":3 } )        # Schwartz
        params.update( {"dephasing_informed":1 } )            # deph-informed

    elif recipe[3] == 8:
        name = F"{name}_BC"
        params.update( {"decoherence_algo":3 } )              # Branching-corrected FSSH
        params.update( {"decoherence_times_type":-1 } )       # no need for dephasing times
        params.update( {"dephasing_informed":0 } )            # no deph-informed, doesn't matter

    elif recipe[3] == 9:
        name = F"{name}_AFSSH"
        params.update( {"decoherence_algo":2 } )              # Aumented FSSH
        params.update( {"decoherence_times_type":-1 } )       # no need for dephasing times
        params.update( {"dephasing_informed":0 } )            # no deph-informed, doesn't matter



    return name, params

def recipe_mapping(recipe):
    # mapping: [a, b, c, d] -> a * 240 + b * 60 + c * 10 + d
    # Normal FSSH: a = 0, b = 1, c = 3, d = 0   => indx = 0*240 + 1*60 + 3*10+ 0 = 90

    a, b, c, d = recipe[0], recipe[1], recipe[2], recipe[3]

    indx = 240*a + 60*b + 10*c + d

    return indx



def recipe_inv_mapping(indx):
    # mapping: [a, b, c, d] -> a * 240 + b * 60 + c * 10 + d

    r1 = indx % 240  # 60*b + 10*c + d
    r2 = r1 % 60     # 10*c + d
    d = r2 % 10
    c = (r2 - d)/10
    b = (r1 - r2)/60
    a = (indx - r1)/240
    
    return [a,b,c,d]
     

def make_all_sets():

    # ============== So far, 240 methods ============
    # mapping: [a, b, c, d] -> a * 240 + b * 60 + c * 10 + d
    # Normal FSSH: a = 0, b = 1, c = 3, d = 0   => indx = 0*240 + 1*60 + 3*10+ 0 = 90

    all_sets = []
    for a in [0]:
        for b in [0, 1, 2, 3]:
            for c in [0, 1, 2, 3, 4, 5]:
                for d in range(0, 10):
                    all_sets.append([a, b, c, d]) 

    return all_sets

def set_recipe_v2(dyn_general, recipe, name=""):
    """
    This function sets a recipe for which the calculations should be run.
    Args:
        dyn_general (dictionary): This dictionary contains necessary variables to perform nonadiabatic dynamics.
                                 It will be updated and returned. 
        recipe (integer list): This list contains 10 values
                               1st: Model (A)
                                   There are currently 4 options for the models
                               2nd: Initial conditions (B)
                                   0: Coords are identical, but momenta are sampled, istates: [1.0, 0.0]
                                   1: Coords are sampled, but momenta are identical, istates: [1.0, 0.0]
                                   2: Both coords and momenta are sampled, istates: [1.0, 0.0]
                                   3: Coords are identical, but momenta are sampled, istates: [0.0, 1.0]
                                   4: Coords are sampled, but momenta are identical, istates: [0.0, 1.0]
                                   5: Coords are identical, but momenta are sampled, istates: [0.0, 1.0] 
                               3rd: Representation (case) (c)
                                   0: adiabatic init, adiabatic TDSE
                                   1: diabatic init, adiabatic TDSE
                                   2: adiabatic init, diabatic TDSE
                                   3: diabatic init, diabatic TDSE
                                   4: adiabatic init, adiabatic Liouville
                                   5: diabatic init, adiabatic Liouville
                                   6: adiabatic init, diabatic Liouville
                                   7: diabatic init, diabatic Liouville
                               4th: Ehrenfest or state-resolved options (D)
                                   0: state-resolved (e.g. TSH) with adiabatic forces
                                   1: for Ehrenfest in adiabatic rep
                                   2: for Ehrenfest in diabatic rep
                               5th: Surface hopping options (E)
                                   0: adiabatic, no surface hopping
                                   1: FSSH
                                   2: GFSH
                                   3: MSSH
                                   4: LZ
                                   5: ZN
                                   6: DISH
                               6th: Decoherence options (F)
                                   0: no decoherence
                                   1: mSDM
                                   2: ID-A
                                   3: MF-SD
                                   4: BCSH
                               7th: Decoherence times option (G)
                                   0: No decoherence times, infinite decoherence times
                                   1: EDC + default params
                                   2: Schwartz version 1
                                   3: Schwartz version 2
                               8th: Hop acceptance method (H)
                                   0: E+, accept and rescale based on total energy, do not reverse on frustrated
                                   1: E-, accept and rescale based on total energy, reverse on frustrated
                                   2: D+, accept and rescale based on NAC vectors, do not reverse on frustrated
                                   3: D-, accept and rescale based on NAC vectors, reverse on frustrated
                                   4: F+, accept and rescale based on force differences, do not reverse on frustrated
                                   5: F-, accept and rescale based on force differences, reverse on frustrated
                               9th: NAC update method (I)
                                   0: Explicit
                                   1: HST
                                   2: NPI
                               10th: Nuclear phase correction by Shenvi, Subotnik, and Yang (SSY) (J)
                                   0: do not use the SSY correction - that's the default
                                   1: use the SSY correction
    Returns:
        dyn_general (dictionary): Updated dyn_general based on recipe.
        elec_params (dictionary): Dictionary for electronic parameters
        nucl_params (dictionary): Dictionary for nuclear parameters
        name (string): A descriptive name for the recipe
    """

    #============================ 1st: Models
    model_params1 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.000, "nstates":2}
    model_params2 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.001, "nstates":2}
    model_params3 = {"model":1, "model0":1, "E_n":[0.0,  0.0], "x_n":[0.0,  2.5],"k_n":[0.002, 0.005],"V":0.01, "nstates":2}
    model_params4 = {"model":1, "model0":1, "E_n":[0.0, -0.01], "x_n":[0.0,  0.5],"k_n":[0.002, 0.008],"V":0.001, "nstates":2}

    all_model_params = [model_params1, model_params2, model_params3, model_params4]
    
    
    model_indx = recipe[0]
    name = F"{name}_model_{model_indx}"
    model_params = all_model_params[model_indx]
    #============================ 1st: Models

    #============================ 2nd: Initial conditions
    init_cond_indx = recipe[1]
    name = F"{name}_icond_{init_cond_indx}"

    nucl_params = {}
    elec_params = {"verbosity": 0, "init_dm_type":0 }

    if init_cond_indx==0:    
        # Coords are identical, but momenta are sampled
        nucl_params = {"ndof":1, "init_type":1, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[1.0, 0.0]})
    elif init_cond_indx==1:
        # Coords are sampled, but momenta are identical
        nucl_params = {"ndof":1, "init_type":2, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[1.0, 0.0]})
    elif init_cond_indx==2:
        # Both coords and momenta are sampled
        nucl_params = {"ndof":1, "init_type":3, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[1.0, 0.0]})    

    elif init_cond_indx==3:    
        # Coords are identical, but momenta are sampled
        nucl_params = {"ndof":1, "init_type":1, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[0.0, 1.0]})
    elif init_cond_indx==4:
        # Coords are sampled, but momenta are identical
        nucl_params = {"ndof":1, "init_type":2, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[0.0, 1.0]})
    elif init_cond_indx==5:
        # Both coords and momenta are sampled
        nucl_params = {"ndof":1, "init_type":3, "q":[-4.0], "p":[0.0], "mass":[2000.0], "force_constant":[0.01] }
        elec_params.update({"ndia":2, "nadi":2, "init_type":3, "istates":[0.0, 1.0]})
    else:
        print("Error occured! No such option available for initial condition. Exiting now!")
        sys.exit(0)

    #============================ 2nd: Initial conditions

    #============================ 3rd: Representation (case)

    case = recipe[2]
    name = F"{name}_case_{case}"

    if case==0:  # adiabatic init, adiabatic TDSE
        elec_params.update( {"rep":1} ) 
        dyn_general.update({"rep_tdse":1, "electronic_integrator":0  }) 
    elif case==1: # diabatic init, adiabatic TDSE
        elec_params.update( {"rep":0} )     
        dyn_general.update({"rep_tdse":1, "electronic_integrator":0 })  
    elif case==2:  # adiabatic init, diabatic TDSE
        elec_params.update( {"rep":1} ) 
        dyn_general.update({"rep_tdse":0, "electronic_integrator":3  })  
    elif case==3:  # diabatic init, diabatic TDSE
        elec_params.update( {"rep":0} ) 
        dyn_general.update({"rep_tdse":0, "electronic_integrator":3  })  
    elif case==4:  # adiabatic init, adiabatic Liouville
        elec_params.update( {"rep":1} )     
        dyn_general.update({"rep_tdse":3, "electronic_integrator":0  }) 
    elif case==5:  # diabatic init, adiabatic Liouville
        elec_params.update( {"rep":0} )     
        dyn_general.update({"rep_tdse":3, "electronic_integrator":0  }) 
    elif case==6:  # adiabatic init, diabatic Liouville
        elec_params.update( {"rep":1} )
        dyn_general.update({"rep_tdse":2, "electronic_integrator":0  }) 
    elif case==7:  # diabatic init, diabatic Liouville
        elec_params.update( {"rep":0} )     
        dyn_general.update({"rep_tdse":2, "electronic_integrator":0  }) 
    else:
        print("Error occured! No such option available for representation. Exiting now!")
        sys.exit(0)
    #============================ 3rd: Representation (case)
    
    #============================ 4th: Ehrenfest or state-resolved options
    # This is what we use with any of the TSH-based methods - in all cases here, we would 
    # use "rep_force":1 so that we are guided by the forces derived from the adiabatic surfaces.
    # In Ehrenfest cases though, the forces can be computed using only diabatic properties though 
    rep_force = recipe[3]

    if rep_force==0:
        dyn_general.update( {"force_method":1, "rep_force":1} ) # state-resolved (e.g. TSH) with adiabatic forces
        name = F"{name}_tsh_"
    elif rep_force==1:
        dyn_general.update( {"force_method":2, "rep_force":1} ) # for Ehrenfest in adiabatic rep
        name = F"{name}_ehrenfest_adi_"
    elif rep_force==2:
        dyn_general.update( {"force_method":2, "rep_force":0} ) # for Ehrenfest in diabatic rep
        name = F"{name}_ehrenfest_adi_"
    else:
        print("Error occured! No such option available for Ehrenfest or state-resolved. Exiting now!")
        sys.exit(0)
    #============================ 4th: Ehrenfest or state-resolved options

    #============================ 5th: Surface hopping options
    sh_opt = recipe[4]

    if sh_opt==0:
        dyn_general.update({"tsh_method":-1 }) # adiabatic, no surface hopping
        name = F"{name}_noSH_"
    elif sh_opt==1:
        dyn_general.update({"tsh_method":0 }) # FSSH
        name = F"{name}_FSSH_"
    elif sh_opt==2:
        dyn_general.update({"tsh_method":1 }) # GFSH
        name = F"{name}_GFSH_"
    elif sh_opt==3:
        dyn_general.update({"tsh_method":2 }) # MSSH
        name = F"{name}_MSSH_"
    elif sh_opt==4:
        dyn_general.update({"tsh_method":3, "rep_lz":0 })  # LZ options
        name = F"{name}_LZ_"
    elif sh_opt==5:
        dyn_general.update({"tsh_method":4, "rep_lz":0 }) # ZN
        name = F"{name}_ZN_"
    elif sh_opt==6:
        dyn_general.update({"tsh_method":5 }) # DISH
        name = F"{name}_DISH_"
    else:
        print("Error occured! No such option available for surface hopping. Exiting now!")
        sys.exit(0)
    #============================ 5th: Surface hopping options

    #============================ 6th: Decoherence options
    deco_opt = recipe[5]

    if deco_opt==0:
        dyn_general.update({ "decoherence_algo":-1}) # no decoherence
        name = F"{name}_noDeco_"
    elif deco_opt==1:
        dyn_general.update({ "decoherence_algo":0}) # msdm  
        name = F"{name}_mSDM_"
    elif deco_opt==2:
        dyn_general.update({ "decoherence_algo":1}) # IDA
        name = F"{name}_ID-A_"
    elif deco_opt==3:
        dyn_general.update({ "decoherence_algo":4}) # mfsd
        name = F"{name}_MF-SD_"
    elif deco_opt==4:
        dyn_general.update({ "decoherence_algo":3}) # BCSH
        name = F"{name}_BCSH_"
    else:
        print("Error occured! No such option available for decoherence. Exiting now!")
        sys.exit(0)
    #============================ 6th: Decoherence options
    
    #============================ 7th: Decoherence times option
    deco_time_opt = recipe[6]
    schwartz_decoherence_inv_alpha = MATRIX(1,1)
    schwartz_decoherence_inv_alpha.set(0, 0, 1.0)
    if deco_time_opt==0:
        dyn_general.update({"decoherence_times_type":-1 }) # No decoherence times, infinite decoherence times
        name = F"{name}_infDecoTime_"
    elif deco_time_opt==1:
        dyn_general.update( { "decoherence_times_type":1, "decoherence_C_param": 1.0, "decoherence_eps_param":0.1 } )  # EDC + default params
        name = F"{name}_EDC_"
    elif deco_time_opt==2:
        dyn_general.update( { "decoherence_times_type":2, "schwartz_decoherence_inv_alpha": schwartz_decoherence_inv_alpha } ) # Schwartz version 1
        name = F"{name}_Schwartz1_"
    elif deco_time_opt==3:
        dyn_general.update( { "decoherence_times_type":3, "schwartz_decoherence_inv_alpha": schwartz_decoherence_inv_alpha } ) # Schwartz version 2
        name = F"{name}_Schwartz2_"
    else:
        print("Error occured! No such option available for decoherence times. Exiting now!")
        sys.exit(0)
    #============================ 7th: Decoherence times option
    
    #============================ 8th: Hop acceptance method
    hop_acceptance = recipe[7]

    if hop_acceptance==0:
        dyn_general.update({"hop_acceptance_algo":10, "momenta_rescaling_algo":100 })  # accept and rescale based on total energy, do not reverse on frustrated
        name = F"{name}_E+_"
    elif hop_acceptance==1:
        dyn_general.update({"hop_acceptance_algo":10, "momenta_rescaling_algo":101 })  # accept and rescale based on total energy, reverse on frustrated
        name = F"{name}_E-_"
    elif hop_acceptance==2:
        dyn_general.update({"hop_acceptance_algo":20, "momenta_rescaling_algo":200 })  # accept and rescale based on NAC vectors, do not reverse on frustrated
        name = F"{name}_D+_"
    elif hop_acceptance==3:
        dyn_general.update({"hop_acceptance_algo":20, "momenta_rescaling_algo":201 })  # accept and rescale based on NAC vectors, reverse on frustrated
        name = F"{name}_D-_"
    elif hop_acceptance==4:
        dyn_general.update({"hop_acceptance_algo":21, "momenta_rescaling_algo":200 })  # accept and rescale based on force differences, do not reverse on frustrated
        name = F"{name}_F+_"
    elif hop_acceptance==5:
        dyn_general.update({"hop_acceptance_algo":21, "momenta_rescaling_algo":201 })  # accept and rescale based on force differences, reverse on frustrated
        name = F"{name}_F-_"
    else:
        print("Error occured! No such option available for hop acceptance method. Exiting now!")
        sys.exit(0)
    #============================ 8th: Hop acceptance method

    #============================ 9th: NAC update method
    nac_update_method = recipe[8]

    if nac_update_method==0:
        dyn_general.update({"nac_update_method":1})  # explicit NAC calculations - let's just focus on this one for now
        name = F"{name}_expplicit_"
    elif nac_update_method==1:
        dyn_general.update({"nac_update_method":2, "nac_algo":0})  # HST algo
        name = F"{name}_HST_"
    elif nac_update_method==2:
        dyn_general.update({"nac_update_method":2, "nac_algo":1})  # NPI algo
        name = F"{name}_NPI_"
    else:
        print("Error occured! No such option available for computing NACs. Exiting now!")
        sys.exit(0)
    #============================ 9th: NAC update method
    
    #============================ 10th: Nuclear phase correction by Shenvi, Subotnik, and Yang (SSY)
    ssy = recipe[9]

    if ssy==0:
        dyn_general.update({"do_ssy":0 }) # do no use it - that's the default
        name = F"{name}_noSSY"
    elif ssy==1:
        dyn_general.update({"do_ssy":1})
        name = F"{name}_SSY"
    else:
        print("Error occured! No such option available for SSY. Exiting now!")
        sys.exit(0)
    #============================ 10th: Nuclear phase correction by Shenvi, Subotnik, and Yang (SSY)
    
    dyn_general.update({ "prefix":name, "prefix2":name })
    
    return dyn_general, elec_params, nucl_params, name

