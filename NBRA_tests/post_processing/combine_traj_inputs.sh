#!/bin/bash

initial_coords="0 6"
istates="excited ground"
model_types="k k_aligned h_shift energy_gaps k_mixed k_aligned_mixed h_shift_mixed energy_gaps_mixed"
dyn_types="nbra_fssh fssh"
sets="0 1 2 3 4 5 6 7 8"

if [ ! -d "../inputs" ] ; then
    mkdir "../inputs" ; fi

template_file=../templates/combine_traj_template.py
input_file=run.py
#submit=../templates/submit_2hr_valhalla.slm # these jobs are short so we use a diff submit file
submit=../templates/submit.slm

  for dyn_type in $dyn_types ; do
    for model_type in $model_types ; do
      for coord in $initial_coords ; do

          if [ $coord = 6 ] && [ $model_type = "k_aligned" ] ; then
           continue ; fi
          if [ $coord = 6 ] && [  $model_type = "energy_gaps" ] ; then
           continue ; fi
           if [[ $model_type == *"mixed"* ]] && [ $dyn_type != "nbra_fssh" ] ; then
             continue ; fi

            for set in $sets ; do
              for istate in $istates ; do

	               work_dir="../inputs/combine_traj_${dyn_type}_${model_type}_${istate}_coord_${coord}_set_${set}"
                  if [ ! -d $work_dir ] ; then
                      mkdir $work_dir
                  else
                      rm -rf $work_dir
      		            mkdir $work_dir
                  fi

                  sed -e "s/ISTATE_REPLACE/${istate}/g" \
                      -e "s/COORD_REPLACE/${coord}/g" \
                      -e "s/MODEL_TYPE_REPLACE/${model_type}/g" \
                      -e "s/DYN_REPLACE/${dyn_type}/g" \
                      -e "s/SET_REPLACE/${set}/g" \
                      $template_file > $work_dir/$input_file
      	      cp $submit $work_dir/submit.slm

done
done
done
done
done
