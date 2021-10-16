#!/bin/bash

initial_coords="0 6"
istates="excited ground"
model_types="k energy_gaps h_shift k_algined"
#templates="msdm_EDC msdm_ave_gaps msdm_DR_1 msdm_DR_10 msdm_DR_25 msdm_DR_50 ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC dish_DR_1 dish_DR_10 dish_DR_25 dish_DR_50"
templates="msdm_EDC msdm_ave_gaps ida_EDC ida_ave_gaps dish_ave_gaps dish_EDC"

cd ../inputs

for model_type in $model_types ; do
  for coord in $initial_coords ; do

        if [ $coord = 6 ] && [ $model_type = "k_aligned" ] ; then
         continue ; fi
        if [ $coord = 6 ] && [  $model_type = "energy_gaps" ] ; then
         continue ; fi

        for istate in $istates ; do
          for template in $templates ; do

          dir="store_data_${template}_${model_type}_${istate}_coord_${coord}"
          if [ -d $dir ] ; then
            cd $dir
            sbatch submit.slm
            cd ..
          fi

done
done
done
done
