#!/bin/bash

initial_coords="0 6"
istates="excited ground"
model_types="k k_aligned h_shift energy_gaps"


template_file=../templates/store_data_template.py
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

        work_dir="../inputs/store_data_${model_type}_${istate}_coord_${coord}"
            if [ ! -d $work_dir ] ; then
                mkdir $work_dir
            else
                rm -rf $work_dir
		            mkdir $work_dir
            fi
            sed -e "s/ISTATE_REPLACE/${istate}/g" \
                -e "s/COORD_REPLACE/${coord}/g" \
                -e "s/MODEL_TYPE_REPLACE/${model_type}/g" \
              $template_file > $work_dir/$input_file
	      cp $submit $work_dir

done
done
done
