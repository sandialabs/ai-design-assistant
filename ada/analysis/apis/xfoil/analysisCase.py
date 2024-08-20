from ada.analysis.apis import xfoil
from ada.analysis.analysisCase import AnalysisCase as BaseAnalysisCase


class AnalysisCase(BaseAnalysisCase):
    def __init__(self):
        super().__init__()
        self.toolName = 'xfoil'
        self.analysisType = '2D Airfoils' # should do something smart with this
        self.toolAPIpath = xfoil
        
        self.inputs.info['alpha']     = {'units':'deg', 
                                         'shape':0, 
                                         'description':'Angle of Attack', 
                                         'alternativeNames':['alpha','angleofattack', 'alfa', 'a'], 
                                         'preferredName': 'Alpha',
                                         'printFormat': r'%f'}
        self.inputs.info['cl']        = {'units':'', 
                                         'shape':0, 
                                         'description':'coefficient of lift', 
                                         'alternativeNames':['liftcoefficient', 'coefficientoflift', 'cl'], 
                                         'preferredName': 'CL',
                                         'printFormat': r'%f'}
        self.inputs.info['m']         = {'units':'', 
                                         'shape':0, 
                                         'description':'Mach number', 
                                         'alternativeNames':['mach','machnumber','m'], 
                                         'preferredName': 'Mach',
                                         'printFormat': r'%f'}
        self.inputs.info['n_crit']    = {'units':'', 
                                         'shape':0, 
                                         'description':'The log of the amplification factor of the most-amplified frequency which triggers transition', 
                                         'alternativeNames':['n','ncrit','ncritical','amplification','amplificationfactor','acrit','acritical'], 
                                         'preferredName': 'N_crit',
                                         'printFormat': r'%f'}
        self.inputs.info['n_panels']  = {'units':'', 
                                         'shape':0, 
                                         'description':'Number of panels that define the airfoil', 
                                         'alternativeNames':['npanels','numberofpanels','npane','npan','np','panelcount','panelnumber'], 
                                         'preferredName': 'N_panels',
                                         'printFormat': r'%d'}
        self.inputs.info['re']        = {'units':'', 
                                         'shape':0, 
                                         'description':'Reynolds number', 
                                         'alternativeNames':['re','r','reynolds number','reynolds'], 
                                         'preferredName': 'Re',
                                         'printFormat': r'%e'}
        self.inputs.info['xtp_l']     = {'units':'', 
                                         'shape':0, 
                                         'description':'Forced transition (or trip) location on the lower surface', 
                                         'alternativeNames':['xtrl','xtransitionlower','xtrlower', 'transitiononlowersurface', 'transitionlocationonthelowersurface', 'transitiononthelowersurface','transitionlocationlower',
                                                             'transitionl','transitionlower','transitionlowersurface', 'xtrbot', 'xtrb', 'xtpl', 'xtriplower', 'triponlowersurface','triplocationonthelowersurface','tripl','triplower'], 
                                         'preferredName': 'Xtp_l',
                                         'printFormat': r'%f'}
        self.inputs.info['xtp_u']     = {'units':'', 
                                         'shape':0, 
                                         'description':'Transition location (or trip) on the upper surface', 
                                         'alternativeNames':['xtru','xtransitionupper','xtrupper', 'transitiononuppersurface', 'transitionlocationontheuppersurface', 'transitionontheuppersurface','transitionlocationupper',
                                                             'transitionu','transitionupper','transitionuppersurface','xtrtop','xtrt', 'xtpu', 'xtripupper', 'triponuppersurface','triplocationontheuppersurface','tripu','tripupper',], 
                                         'preferredName': 'Xtp_u',
                                         'printFormat': r'%f'}
        
        self.inputs.mutuallyExclusive = [ ['alpha','cl'] ]
        
        self.outputs.info['alpha']    = {'units':'deg', 
                                         'shape':0, 
                                         'description':'Angle of Attack', 
                                         'alternativeNames':['alpha','angleofattack', 'alfa', 'a'], 
                                         'preferredName': 'Alpha',
                                         'printFormat': r'%f'}
        self.outputs.info['bl_data']  = {'units':'', 
                                         'shape':0, 
                                         'description':'Dictionary of boundary layer data', 
                                         'alternativeNames':[], 
                                         'preferredName': 'BL Data',
                                         'printFormat': None}
        self.outputs.info['cd']       = {'units':'', 
                                         'shape':0, 
                                         'description':'coefficient of drag', 
                                         'alternativeNames':['dragcoefficient', 'coefficientofdrag', 'cd'], 
                                         'preferredName': 'CD',
                                         'printFormat': r'%f'}
        self.outputs.info['cl']       = {'units':'', 
                                         'shape':0, 
                                         'description':'coefficient of lift', 
                                         'alternativeNames':['liftcoefficient', 'coefficientoflift', 'cl'], 
                                         'preferredName': 'CL',
                                         'printFormat': r'%f'}
        self.outputs.info['cm']       = {'units':'', 
                                         'shape':0, 
                                         'description':'moment coefficient', 
                                         'alternativeNames':['momentcoefficient', 'coefficientofmoment', 'cm'], 
                                         'preferredName': 'CM',
                                         'printFormat': r'%f'}
        self.outputs.info['cp_data']  = {'units':'', 
                                         'shape':0, 
                                         'description':'Dictionary of pressure coefficient data', 
                                         'alternativeNames':[], 
                                         'preferredName': 'CP Data',
                                         'printFormat': None}
        self.outputs.info['xtr_l']    = {'units':'', 
                                         'shape':0, 
                                         'description':'Transition location on the lower surface', 
                                         'alternativeNames':['xtrl','xtransitionlower','xtrlower', 'transitiononlowersurface', 'transitionlocationonthelowersurface', 'transitiononthelowersurface','transitionlocationlower',
                                                             'transitionl','transitionlower','transitionlowersurface', 'xtrbot', 'xtrb'], 
                                         'preferredName': 'Xtr_l',
                                         'printFormat': r'%f'}
        self.outputs.info['xtr_u']    = {'units':'', 
                                         'shape':0, 
                                         'description':'Transition location on the upper surface', 
                                         'alternativeNames':['xtru','xtransitionupper','xtrupper', 'transitiononuppersurface', 'transitionlocationontheuppersurface', 'transitionontheuppersurface','transitionlocationupper',
                                                             'transitionu','transitionupper','transitionuppersurface','xtrtop','xtrt'], 
                                         'preferredName': 'Xtr_u',
                                         'printFormat': r'%f'}

        self.outputs.mutuallyExclusive = [ ['alpha','cl'] ]
        
        
        self.set_defaults()
        
    def set_defaults(self):
        self.inputs['alpha']    = 0
        self.inputs['mach']     = 0
        self.inputs['re']       = 1e7
        self.inputs['n_crit']   = 9
        self.inputs['xtr_u']    = 1.0
        self.inputs['xtr_l']    = 1.0
        self.inputs['n_panels'] = 160
        
        # self.outputs['cl']      = None
        # self.outputs['bl_data'] = None
        # self.outputs['cd']      = None
        # self.outputs['cl']      = None
        # self.outputs['cm']      = None
        # self.outputs['cp_data'] = None
        # self.outputs['xtr_l']   = None
        # self.outputs['xtr_u']   = None