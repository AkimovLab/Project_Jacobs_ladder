#!/bin/bash

initial_coords="0 6"
sets="0 1 2 3 4 5 6 7 8"
numbers="1 2 3"
trajs="300"
istates="excited ground"
model_types="k k_aligned h_shift energy_gaps"

input_file=run.py
submit=../templates/submit.slm

if [ ! -d "../inputs" ] ; then
    mkdir "../inputs" ; fi

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

        work_dir="../inputs/adi_${model_type}_${istate}_coord_${coord}_set_${set}_ntraj_${ntraj}_number_${number}"
            if [ ! -d $work_dir ] ; then
                mkdir $work_dir
            else
                rm -rf $work_dir
		            mkdir $work_dir
            fi
            sed -e "s/ISTATE_REPLACE/${istate}/g" \
                -e "s/COORD_REPLACE/${coord}/g" \
                -e "s/TRAJ_REPLACE/${ntraj}/g" \
                -e "s/SET_REPLACE/${set}/g" \
                -e "s/NUMBER_REPLACE/${number}/g" \
                -e "s/MODEL_TYPE_REPLACE/${model_type}/g" \
              ../templates/adiabatic_template.py > $work_dir/$input_file
	      cp $submit $work_dir
done
done
done
done
done
done
