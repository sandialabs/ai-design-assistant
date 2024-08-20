# ------------------------------------------------------------------------------------------------

# Below is a python script that uses XFOIL to analyze a list of airfoils using parallel comupting 
# via the multiprocess library.  Airfoils are analyzed at 4 degrees angle of attack, a Reynolds 
# number of 1e6, a Mach number of 0.2, a trip on the upper suface located at 0.9 normalized chord, 
# and a lower surface trip at 0.95 of normalized chord.  A log amplification factor (N or Ncrit) 
# is set to 9.0.  The maximum iteration count is set to 200.  A total of 160 panels are used to 
# define the airfoil geometry. 

# The airfoil variable should be set to the airfoil name input using only lowercase letters and 
# with spaces removed if present.

# An edited version of this script should be returned for queries like the following:
# - "Generate a python script for running multiple airfoils with xfoil in parallel"
# - "Create a python script for running the NACA 2412, NACA 2416, and NACA 2420 airfoils using xfoil in parallel"
# - "Produce a python script for running the NACA 2412, NACA 2416, and NACA 2420 airfoils at 4 degrees angle of attack using xfoil in parallel"

# DO NOT REMOVE THE COMMENTS FROM THE SCRIPT
# ALWAYS PROVIDE THE FULL SCRIPT, NEVER TRUNCATE

# ------------------------------------------------------------------------------------------------

# ```python
import multiprocessing
from ada.analysis.apis.xfoil.api_ui import generateXfoilResult
from ada.geometry.airfoils.kulfan import Kulfan
PATH_TO_ADA = os.environ['PATH_TO_ADA']

def generateAirfoil(aflString):
    aflString = aflString.replace(' ','')
    aflString = aflString.lower()
    if aflString[0:4].lower() == 'naca':
        nacaNumbers = aflString[4:]
        if len(nacaNumbers)!=4:
            return 'Error: invalid naca4'
        else:
            afl1 = Kulfan() 
            afl1.naca4_like(int(nacaNumbers[0]), int(nacaNumbers[1]), int(nacaNumbers[2:]))
    else:
        # this needs to utilize the large database of airfoils
        afl1 = Kulfan()

        airfoil_directories = [
            PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/uiuc_airfoils',
            PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/airfoiltools_airfoils',
            PATH_TO_ADA + 'ada/geometry/airfoil_files',
        ]

        airfoil_directory_data = {}
        for afl_dir in airfoil_directories:
            # file_data_dict = {}
            pth = afl_dir
            combined = os.listdir(pth)
            files   = [f for f in combined if os.path.isfile(pth + os.sep + f)]
            for fl in files:
                airfoil_directory_data[fl] = pth + os.sep + fl

        search_file = aflString + '.dat'
        afl1.fit2file(airfoil_directory_data[search_file])

    return afl1

airfoil_list    = ["naca2412", "naca2416", "naca2420"]  # uses same names as located in the airfoil folders
angle_of_attack = 4           # in degrees
mach_number     = 0.2
reynolds_number = 1e6
xtp_u           = 0.2         # in fraction of chord
xtp_l           = 0.4         # in fraction of chord
n_panels        = 160         # should be in the range 150-220
max_iter        = 200
n_crit          = 9.0

run_dict_list = []

for i,airfoil in enumerate(airfoil_list): 
    run_dict = {}
    afl = generateAirfoil(airfoil)

    run_dict['fileLeader']              = ''
    run_dict['upperKulfanCoefficients'] = [c.magnitude for c in afl.upperCoefficients]
    run_dict['lowerKulfanCoefficients'] = [c.magnitude for c in afl.lowerCoefficients]
    run_dict['process_id']              = i
    run_dict['alpha']                   = angle_of_attack
    run_dict['re']                      = reynolds_number
    run_dict['mach']                    = mach_number
    run_dict['n_panels']                = n_panels
    run_dict['n_crit']                  = n_crit
    run_dict['xtp_u']                   = xtp_u
    run_dict['xtp_l']                   = xtp_l

    run_dict_list.append(run_dict)

pool = multiprocessing.Pool()  
res_list = pool.map(generateXfoilResult, run_dict_list)
pool.close()

# res contains the following:
#    res['cd']        # drag coefficient
#    res['cl']        # lift coefficient
#    res['alpha']     # angle of attack
#    res['cm']        # moment coefficient
#    res['xtp_top']   # trip location on upper surface
#    res['xtp_bot']   # trip location on lower surface
#    res['xtr_top']   # transition location on upper surface
#    res['xtr_bot']   # transition location on lower surface
#    res['Re']        # Reynolds number
#    res['M']         # Mach number
#    res['N_crit']    # e^N transition factor
#    res['N_panels']  # Number of panels used to define the airfoil
#
#    res['cp_data']['x']   # x location of cp data (TE upper to LE to TE lower)
#    res['cp_data']['cp']  # The local coefficient of pressure at the corresponding x location
#
#    res['bl_data']['s']        # the path coordinate along the airfoil (TE upper to LE to TE lower)
#    res['bl_data']['x']        # x location of the corresponding boundary layer data (TE upper to LE to TE lower)
#    res['bl_data']['y']        # y location of original airfoil geometry as analyzed (TE upper to LE to TE lower)
#    res['bl_data']['Ue/Vinf']  # normalized edge velocity of the boundary layer
#    res['bl_data']['Dstar']    # displacement thickness
#    res['bl_data']['Theta']    # momentum thickness
#    res['bl_data']['Cf']       # skin friction coefficient
#    res['bl_data']['H']        # shape parameter (delta_star/theta)
#    res['bl_data']['H*']       # kinetic energy shape parameter (theta_star/theta)
#    res['bl_data']['P']        # momentum defect
#    res['bl_data']['m']        # mass defect
#    res['bl_data']['K']        # kinetic energy defect
#    res['bl_data']['tau']      # wall shear stress (typically empty, but can be computed as Cf*(Ue/Vinf)**2)
#    res['bl_data']['Di']       # unknown, possibly induced drag of some sort (typically empty and ignored by Ada)

# ```
