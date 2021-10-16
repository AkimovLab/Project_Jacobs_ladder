#!/bin/bash


initial_coords="0 6"
istates="excited ground"
model_types="k k_aligned h_shift energy_gaps"
sets="0 1 2 3 4 5 6 7 8"

input_file=run.py
submit=submit.slm

cd ../inputs

for model_type in $model_types ; do
  for coord in $initial_coords ; do

      if [ $coord = 6 ] && [ $model_type = "k_aligned" ] ; then
       continue ; fi
      if [ $coord = 6 ] && [  $model_type = "energy_gaps" ] ; then
       continue ; fi

        for set in $sets ; do
          for istate in $istates ; do

             dir="combine_traj_adiabatic_md_${model_type}_${istate}_coord_${coord}_set_${set}"
             if [ -d $dir ] ; then
               cd $dir
               sbatch submit.slm
               cd ..
             fi
done
done
done
done
