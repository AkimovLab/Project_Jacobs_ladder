# Compute the dynamics

   by running the `run_namd_2state_models.py` script

   In it, you can change:

   * the model and parameters:

       - Landau-Zener type models (linear);
       - Holstein type models (quadratic) 

   * the type of calculations:

       - `ham_rep, is_nbra = 0, 0`   for the genuine TSH, non-NBRA
       - `ham_rep, is_nbra = 0, 2`   for on-the-fly NBRA - choose on wich state to evolve nuclear dynamics
       - `ham_rep, is_nbra = 1, 1`   for the file-based NBRA - need the hvib_adi.txt and St.txt available - e.g. from any of the above calculations


   * The simulation methodologies:

       - phase correction or not
       - state tracking algorithms, etc.

 
   * The methodology:
  
       - FSSH
       - IDA
       - mSDM
       - DISH

# Plot data

 
   by running the following scrip `plot_2sta.py`

   It will produce various kinds of output files

