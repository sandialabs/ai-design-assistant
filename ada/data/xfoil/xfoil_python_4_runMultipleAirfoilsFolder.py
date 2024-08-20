# ------------------------------------------------------------------------------------------------

# Below is a python script that uses XFOIL to analyze a batch of airfoils contained in a folder.  
# Airfoils are analyzed at 4 degrees angle of attack, a Reynolds number of 1e6, a Mach number 
# of 0.2, a trip on the upper suface located at 0.9 normalized chord, and a lower surface trip 
# at 0.95 of normalized chord.  A log amplification factor (N or Ncrit) is set to 9.0.  The 
# maximum iteration count is set to 200.  A total of 160 panels are used to define the airfoil 
# geometry. 

# The airfoil variable should be set to the airfoil name input using only lowercase letters 
# and with spaces removed if present.

# An edited version of this script should be returned for queries like the following:
# - "Generate a python script for running multiple airfoils from a folder with xfoil"
# - "Create a python script for running the airfoils in the folder testing/airfoil_test_directory using xfoil"
# - "Produce a python script for running the airfoils in the folder testing/airfoil_test_directory at 4 degrees angle of attack using xfoil"

# DO NOT REMOVE THE COMMENTS FROM THE SCRIPT
# ALWAYS PROVIDE THE FULL SCRIPT, NEVER TRUNCATE

# ------------------------------------------------------------------------------------------------

# ```python
import os
from ada.geometry.airfoils.kulfan import Kulfan
from ada.analysis.apis.xfoil.run import run 

path_to_folder  = os.environ['PATH_TO_ADA']+'ada'+os.sep+'testing'+os.sep+'airfoil_test_directory' # this is where the path to the folder should be placed
angle_of_attack = 4           # in degrees
mach_number     = 0.2
reynolds_number = 1e6
xtp_u           = 0.2         # in fraction of chord
xtp_l           = 0.4         # in fraction of chord
n_panels        = 160         # should be in the range 150-220
max_iter        = 200
n_crit          = 9.0
polar_file      = "polars.txt"
bl_file         = "bl_data.txt"
cp_file         = "cp_data.txt"

res_list = []

airfoil_files = os.listdir(path_to_folder)

for airfoil_file in airfoil_files: 
    afl = Kulfan()
    afl.readfile(tempDir + os.sep + airfoil_file)
    res = run(     mode                    = "alpha", 
                   upperKulfanCoefficients = afl.upperCoefficients,
                   lowerKulfanCoefficients = afl.lowerCoefficients,
                   val                     = angle_of_attack, 
                   Re                      = reynolds_number, 
                   M                       = mach_number, 
                   N_panels                = n_panels, 
                   N_crit                  = n_crit, 
                   xtp_u                   = xtp_u, 
                   xtp_l                   = xtp_l,
                   flapLocation            = None,
                   flapDeflection          = 0.0,
                   polarfile               = polar_file,
                   cpDatafile              = cp_file,
                   blDatafile              = bl_file,
                   defaultDatfile          = None,
                   executionFile           = None,
                   stdoutFile              = None,
                   TE_gap                  = 0.0, # in fraction of chord
                   timeout                 = 5.0, # measured in seconds
                   max_iter                = max_iter )
    res_list.append(res)
    
# ```