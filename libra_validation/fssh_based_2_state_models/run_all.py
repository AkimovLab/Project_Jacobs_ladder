import os
import sys
from itertools import product
from recipes import submit_jobs


#============================== Manual set 1: Hop acceptance methods without decoherence
models = [0,1,2,3]
#======= Initial conditions, Both coords and momenta are sampled, istate=[1,0]
iconds = [2]
#======= Adiabatic initialization, Adiabatic TDSE
reps    = [0]
#======= TSH, Ehrenfest
tsh_ehr = [0,1]
#======= FSSH, GFSH, MSSH
sh_opt = [1,2,3]
#======= No decoherence
deco_opt = [0]
#======= Decoherence time option
deco_time_opt = [0]
#======= E+, E-, D+, D-, F+, F-
hop_acc = [0,1,2,3,4,5]
#======= NAC calculations type, Explicit
nac_update = [0]
#======= SSY correction
ssy = [0]
# Make the recipes as below so that we can feed through Python arg parser
recipes = list(product(models, iconds, reps, tsh_ehr, sh_opt, deco_opt, deco_time_opt, hop_acc, nac_update, ssy)) 
print(len(recipes)) 
print(recipes) 
submit_jobs('submit.slm', 'run_namd_2states_models.py', recipes, dt=10.0, nsteps=2500, ntraj=100)
#sys.exit(0)

#============================== Manual set 2: Decoherence methods
models = [0,1,2,3]
#======= Initial conditions, Both coords and momenta are sampled, istate=[1,0]
iconds = [2]
#======= Adiabatic initialization, Adiabatic TDSE
reps    = [0]
#======= TSH, Ehrenfest
tsh_ehr = [0,1]
#======= FSSH, GFSH, MSSH
sh_opt = [1]
#======= No decoherence
deco_opt = [1,2,3,4]
#======= Decoherence time option
# Schwartz v1
deco_time_opt = [2]
#======= E+
hop_acc = [0]
#======= NAC calculations type, Explicit
nac_update = [0]
#======= SSY correction
ssy = [0]
# Make the recipes as below so that we can feed through Python arg parser
recipes = list(product(models, iconds, reps, tsh_ehr, sh_opt, deco_opt, deco_time_opt, hop_acc, nac_update, ssy))
#======= Append DISH manusally
for i in range(4):
    recipes.append((i,5,0,0,6,0,0,0,0,0))
print(len(recipes))
print(recipes)
submit_jobs('submit.slm', 'run_namd_2states_models.py', recipes, dt=10.0, nsteps=2500, ntraj=100)


