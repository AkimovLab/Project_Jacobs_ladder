#!/bin/bash

initial_coords="0 6"
sets="0 1 2 3 4 5 6 7 8"
numbers="1 2 3 4"
trajs="250"
#istates="excited ground"
istates="ground"
model_types="k energy_gaps"
#templates="msdm_EDC msdm_ave_gaps msdm_DR_1 msdm_DR_10 msdm_DR_25 msdm_DR_50 ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC dish_DR_1 dish_DR_10 dish_DR_25 dish_DR_50"
#templates="msdm_EDC msdm_ave_gaps ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC"
templates="ida_ave_gaps"

input_file=run.py
submit=submit.slm

cd "../inputs"

for template in $templates; do
  for model_type in $model_types ; do
    for coord in $initial_coords ; do

        if [ $coord = 6 ] && [ $model_type = "k_aligned" ] ; then
         continue ; fi
        if [ $coord = 6 ] && [  $model_type = "energy_gaps" ] ; then
         continue ; fi

        for istate in $istates ; do
          for set in $sets ; do
      	    for ntraj in $trajs ; do
              for number in $numbers ; do

          dir="${template}_${model_type}_mixed_${istate}_coord_${coord}_set_${set}_ntraj_${ntraj}_number_${number}"
          if [ -d $dir ] ; then
            cd $dir
            sbatch submit.slm
            cd ..
          fi


done
done
done
done
done
done
done
