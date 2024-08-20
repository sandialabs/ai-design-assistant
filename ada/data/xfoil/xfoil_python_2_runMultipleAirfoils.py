# ------------------------------------------------------------------------------------------------

# Below is a python script that uses XFOIL to analyze a list of airfoils at 4 degrees angle of 
# attack, a Reynolds number of 1e6, a Mach number of 0.2, a trip on the upper suface located at 
# 0.9 normalized chord, and a lower surface trip at 0.95 of normalized chord.  A log amplification 
# factor (N or Ncrit) is set to 9.0.  The maximum iteration count is set to 200.  A total of 160 
# panels are used to define the airfoil geometry. 

# The airfoil variable should be set to the airfoil name input using only lowercase letters and 
# with spaces removed if present.

# An edited version of this script should be returned for queries like the following:
# - "Generate a python script for running multiple airfoils with xfoil"
# - "Create a python script for running the NACA 2412, NACA 2416, and NACA 2420 airfoils using xfoil"
# - "Produce a python script for running the NACA 2412, NACA 2416, and NACA 2420 airfoils at 4 degrees angle of attack using xfoil"

# DO NOT REMOVE THE COMMENTS FROM THE SCRIPT
# ALWAYS PROVIDE THE FULL SCRIPT, NEVER TRUNCATE

# ------------------------------------------------------------------------------------------------

# ```python
from ada.analysis.apis.xfoil.run import run
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
polar_file      = "polars.txt"
bl_file         = "bl_data.txt"
cp_file         = "cp_data.txt"

res_list = []

for airfoil in airfoil_list: 
    afl = generateAirfoil(airfoil)
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
