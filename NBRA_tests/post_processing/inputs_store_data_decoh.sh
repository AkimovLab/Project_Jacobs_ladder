#!/bin/bash

initial_coords="0 6"
#istates="excited ground"
istates="ground"
model_types="k k_aligned h_shift energy_gaps" # no _mixed here
#templates="msdm_EDC msdm_ave_gaps msdm_DR_1 msdm_DR_10 msdm_DR_25 msdm_DR_50 ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC dish_DR_1 dish_DR_10 dish_DR_25 dish_DR_50"
templates="msdm_EDC msdm_ave_gaps ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC"

template_file=../templates/store_data_decoh_template.py
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
        for template in $templates ; do
        work_dir="../inputs/store_data_${template}_${model_type}_${istate}_coord_${coord}"
            if [ ! -d $work_dir ] ; then
                mkdir $work_dir
            else
                rm -rf $work_dir
		            mkdir $work_dir
            fi
            sed -e "s/ISTATE_REPLACE/${istate}/g" \
                -e "s/COORD_REPLACE/${coord}/g" \
                -e "s/MODEL_TYPE_REPLACE/${model_type}/g" \
                -e "s/TEMPLATE_REPLACE/${template}/g" \
              $template_file > $work_dir/$input_file
	      cp $submit $work_dir

done
done
done
done
