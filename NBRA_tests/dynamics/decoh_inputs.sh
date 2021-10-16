#!/bin/bash

initial_coords="0 6"
sets="0 1 2 3 4 5 6 7 8"
numbers="1 2 3 4"
trajs="250"
istates="excited ground"
model_types="k energy_gaps k_aligned h_shift"
#templates="msdm_EDC msdm_ave_gaps msdm_DR_1 msdm_DR_10 msdm_DR_25 msdm_DR_50 ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC dish_DR_1 dish_DR_10 dish_DR_25 dish_DR_50"
templates="msdm_EDC msdm_ave_gaps ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC"


if [ ! -d "../inputs" ] ; then
    mkdir "../inputs" ; fi

input_file=run.py
submit=../templates/submit.slm


for template in $templates ; do
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

          work_dir="../inputs/${template}_${model_type}_${istate}_coord_${coord}_set_${set}_ntraj_${ntraj}_number_${number}"
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
                  -e "s/MIXED_REPLACE/0/g" \
                  ../templates/${template}_template.py > $work_dir/$input_file
  	      cp $submit $work_dir
done
done
done
done
done
done
done
