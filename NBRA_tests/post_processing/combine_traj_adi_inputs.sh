#!/bin/bash

initial_coords="0 6"
istates="excited ground"
model_types="k energy_gaps k_aligned h_shift"
sets="0 1 2 3 4 5 6 7 8"

if [ ! -d "../inputs" ] ; then
    mkdir "../inputs" ; fi

input_file=run.py
#submit=../templates/submit_2hr_valhalla.slm # these jobs are short so we use a diff submit file
submit=../templates/submit.slm 
template_file=../templates/combine_traj_template.py



  for model_type in $model_types ; do
    for coord in $initial_coords ; do

        if [ $coord = 6 ] && [ $model_type = "k_aligned" ] ; then
         continue ; fi
        if [ $coord = 6 ] && [  $model_type = "energy_gaps" ] ; then
         continue ; fi

          for set in $sets ; do
            for istate in $istates ; do

           work_dir="../inputs/combine_traj_adiabatic_md_${model_type}_${istate}_coord_${coord}_set_${set}"

                if [ ! -d $work_dir ] ; then
                    mkdir $work_dir
                else
                    rm -rf $work_dir
    		            mkdir $work_dir
                fi

                sed -e "s/ISTATE_REPLACE/${istate}/g" \
                    -e "s/COORD_REPLACE/${coord}/g" \
                    -e "s/MODEL_TYPE_REPLACE/${model_type}/g" \
                    -e "s/DYN_REPLACE/adiabatic_md/g" \
                    -e "s/SET_REPLACE/${set}/g" \
                    $template_file > $work_dir/$input_file
    	      cp $submit $work_dir/submit.slm

done
done
done
done
