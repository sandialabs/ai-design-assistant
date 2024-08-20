import numpy as np
from ada.geometry.airfoils.kulfan import Kulfan
from matplotlib.gridspec import GridSpec
import math

import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
plt.rcParams.update({'font.size': 15})
import matplotlib
colors = ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)
matplotlib.use('Agg')

from ada.analysis.apis.xfoil.helperFunctions import truncate_colormap, handleZeroDivide, get_colors, computeNormals


alternativeNameDict = {
    'none':'None',
    'None':'None', # needed for LLM model, which will return capitalized
    #
    'cp'                      : 'CP'      ,
    'pressure_coefficient'    : 'CP'      ,
    'coefficient_of_pressure' : 'CP'      ,
    'pressure'                : 'CP'      ,
    #
    'ue/vinf'                        : 'Ue/Vinf' ,
    'normalized_velocity'            : 'Ue/Vinf' , 
    'velocity'                       : 'Ue/Vinf' , 
    'edge_velocity'                  : 'Ue/Vinf' , 
    'u_edge'                         : 'Ue/Vinf' , 
    'ue_over_vinf'                   : 'Ue/Vinf' , 
    'ue_over_vinfinity'              : 'Ue/Vinf' , 
    'freestream_normalized_velocity' : 'Ue/Vinf' , 
    #
    'dstar'                   : 'Dstar'   ,
    'deltastar'               : 'Dstar'   ,
    'delta_star'              : 'Dstar'   ,
    'displacement_thickness'  : 'Dstar'   ,
    #
    'theta'              : 'Theta'   ,
    'momentum_thickness' : 'Theta'   ,
    #
    'tstar'                    : 'Tstar'   ,
    'theta_star'               : 'Tstar'   ,
    'kinetic_energy_thickness' : 'Tstar'   ,
    'kinetic_thickness'        : 'Tstar'   ,
    #
    'h*'                              : 'H*'      ,
    'kinetic_energy_shape_parameter'  : 'H*'      ,
    'kinetic_shape_parameter'         : 'H*'      ,
    'h_star'                          : 'H*'      ,
    'hstar'                           : 'H*'      ,
    'thetaStar_over_theta'            : 'H*'      ,
    #
    'h'                     : 'H'       ,
    'shape_parameter'       : 'H'       ,
    'dstar_over_theta'      : 'H'       ,
    'delta_over_theta'      : 'H'       ,
    'deltastar_over_theta'  : 'H'       ,
    #
    'm'           : 'm'       ,
    'mass_defect' : 'm'       ,
    #
    'p'               : 'P'       ,
    'momentum_defect' : 'P'       ,
    #
    'k'                     : 'K'       ,
    'kinetic_defect'        : 'K'       ,
    'kinetic_energy_defect' : 'K'       ,
    #
    'cf'                         : 'Cf'      ,
    'skin_friction'              : 'Cf'      ,
    'skin_friction_coefficient'  : 'Cf'      ,
    'friction_coefficient'       : 'Cf'      ,
    #
    'tau_w'               : 'tau_w'   ,
    'wall_shear_stress'   : 'tau_w'   ,
    'wall_stress'         : 'tau_w'   ,
    'shear_stress'        : 'tau_w'   ,
    'wall_shear'          : 'tau_w'   ,
}

def boundaryLayerPlot(dataList, parameter, dataIndicies = None):
    if dataIndicies is None:
        dataIndicies = [i+1 for i in range(0,len(dataList))]

    parameter = alternativeNameDict[parameter.lower()]
    
    blNames = ['H*', 'P', 'm', 'K', 'Tstar','Ue/Vinf', 'H', 'Dstar', 'Theta', 'Cf', 'tau_w']
    
    nameLookup = {
        'CP'    : r'$C_p$',                  # Coefficient of pressure
        'Ue/Vinf' : r'$U_e / V_{\infty}$' ,    # Edge velocity divided by free stream velocity
        'H*'      : r'$H^*$',                  # kinetic energy shape parameter (theta_star/theta)
        'H'       : r'$H$',                    # Shape parameter (Dstar/theta)
        'P'       : r'$P$',                    # momentum defect
        'm'       : r'$m$',                    # mass defect
        'Dstar'   : r'$\delta^*$',             # displacement thickness
        'Theta'   : r'$\theta$',               # momentum thickness 
        'Cf'      : r'$C_f$',                  # skin friction coefficient
        'K'       : r'$K$',                    # kenetic energy defect
        'Tstar'   : r'$\theta^*$',             # kenetic energy thickness
        'tau_w'   : r'$\tau_w$',               # wall shear stress
    }
    
    for data in dataList:
        data['bl_data']['tau_w'] = ( np.array(data['bl_data']['Cf']) * np.array(data['bl_data']['Ue/Vinf'])**2 ).tolist()
        data['bl_data']['Tstar'] = ( np.array(data['bl_data']['H*']) * np.array(data['bl_data']['Theta']) ).tolist()

        data['stagnation_index'] = data['cp_data']['cp'].index(max(data['cp_data']['cp']))
        data['wake_index']       = next(k for k, value in enumerate(data['bl_data']['x']) if value > 1)
        data['xmin_index']       = data['bl_data']['x'].index(min(data['bl_data']['x']))
        data['normals']          = computeNormals(data['bl_data']['x'],data['bl_data']['y'])

        data['lower_te_shift'] = 0.0
        if abs(data['bl_data']['x'][data['wake_index']] - 1.0) < 1e-3 and abs(data['bl_data']['y'][data['wake_index']])<1e-3:
            # blunt trailing egde
            data['lower_te_shift'] = data['bl_data']['y'][data['wake_index']-1]
        
        split_frac = None
        boundaryLayerPoints = []
        for i,nm in enumerate(data['normals']):
            x = data['bl_data']['x'][i]
            y = data['bl_data']['y'][i]
            dorun = True
            # if i>0:
            if data['bl_data']['x'][i]>=1 and data['bl_data']['x'][i-1]<=1 :
                # skip the points where the lower surface transitons to the wake, along with the first point (upper TE)
                dorun=False
                split_frac = data['bl_data']['Dstar'][0] / (data['bl_data']['Dstar'][i-1]+data['bl_data']['Dstar'][0])
                
            if dorun and i>0 and i != data['wake_index']:
                # skip the last two points on the trailing edge, and the first one in the wake
                # makes the plot smoother and avoids issues with the normal on a blunt trailing edge
                amp = 1
                sc = data['bl_data']['Dstar'][i]*amp
                if split_frac is not None:
                    xshift = x - nm[0]*sc*(1-split_frac)
                    yshift = y - nm[1]*sc*(1-split_frac) + data['lower_te_shift']
                    boundaryLayerPoints = [[xshift+nm[0]*sc, yshift+nm[1]*sc]] + boundaryLayerPoints
                    data['stagnation_index'] += 1
                    boundaryLayerPoints.append([xshift, yshift])
                else:
                    boundaryLayerPoints.append([x+nm[0]*sc, y+nm[1]*sc])

        # boundaryLayerPoints = np.array(boundaryLayerPoints)
        data['boundaryLayerPoints'] = boundaryLayerPoints
    
        data['stagnation_index'] -= 1
        data['x_upper']  = np.array(data['boundaryLayerPoints'])[0:data['stagnation_index']+1, 0].tolist()
        data['x_lower']  = np.array(data['boundaryLayerPoints'])[data['stagnation_index']:   , 0].tolist()
        data['ds_upper'] = np.array(data['boundaryLayerPoints'])[0:data['stagnation_index']+1, 1].tolist()
        data['ds_lower'] = np.array(data['boundaryLayerPoints'])[data['stagnation_index']:   , 1].tolist()
        
        
        data['stagnation_index'] = data['cp_data']['cp'].index(max(data['cp_data']['cp']))
        
        data['plot'] = {}
        data['plot']['CP'] = {}
        data['plot']['CP']['upper'] = [list(reversed(data['bl_data']['x'][0:data['stagnation_index']+1])),
                                       list(reversed(data['cp_data']['cp'][0:data['stagnation_index']+1]))]
        data['plot']['CP']['lower'] = [data['bl_data']['x'][data['stagnation_index']:data['wake_index']],
                                       data['cp_data']['cp'][data['stagnation_index']:]]
        data['plot']['CP']['wake'] = []
        data['plot']['CP']['invert_y'] = True
        data['plot']['CP']['y_label'] = nameLookup['CP']

        for nm in blNames:
            data['plot'][nm] = {}
            data['plot'][nm]['upper'] = []
            data['plot'][nm]['lower'] = []
            data['plot'][nm]['wake'] = []
            data['plot'][nm]['invert_y'] = False
            data['plot'][nm]['y_label'] = nameLookup[nm]
            
            if nm == 'Ue/Vinf':
                upper_x = list(reversed(data['bl_data']['x'][0:data['stagnation_index']+1]))
                upper_y = list(reversed(data['bl_data'][nm][0:data['stagnation_index']+1]))

                lower_x = data['bl_data']['x'][data['stagnation_index']:data['wake_index']]
                lower_y = data['bl_data'][nm][data['stagnation_index']:data['wake_index']]

                if lower_y[0] > 0:
                    if 0.0 not in lower_y:
                        for j, yval in enumerate(lower_y):
                            if yval < 0:
                                lower_y = lower_y[0:j] + [0.0] + lower_y[j:]
                                lower_x = lower_x[0:j] + [(lower_x[j-1] + lower_x[j]) /2.0] + lower_x[j:]
                                break
                    lower_y = abs(np.array(lower_y)).tolist()

                if upper_y[0] < 0:
                    if 0.0 not in upper_y:
                        for j, yval in enumerate(upper_y):
                            if yval > 0:
                                upper_y = upper_y[0:j] + [0.0] + upper_y[j:]
                                upper_x = upper_x[0:j] + [(upper_x[j-1] + upper_x[j]) /2.0] + upper_x[j:]
                                break
                    upper_y = abs(np.array(upper_y)).tolist()
                    lower_y = abs(np.array(lower_y)).tolist()
                    
                data['plot'][nm]['upper'] = [upper_x, upper_y]
                data['plot'][nm]['lower'] = [lower_x, lower_y]

            else:
                data['plot'][nm]['upper'] = [ list(reversed(data['bl_data']['x'][0:data['stagnation_index']+1])),
                                              list(reversed(data['bl_data'][nm][0:data['stagnation_index']+1]))     ] 
                data['plot'][nm]['lower'] = [ data['bl_data']['x'][data['stagnation_index']:data['wake_index']],
                                              data['bl_data'][nm][data['stagnation_index']:data['wake_index']]      ]

            if not np.isnan(data['bl_data'][nm][data['wake_index']]):
                data['plot'][nm]['wake'] = [ data['bl_data']['x'][data['wake_index']:],
                                             data['bl_data'][nm][data['wake_index']:]  ]
        
    blNames = ['CP'] + blNames
    
    if len(dataList) == 1:
        colors_lower = ['#d55e00']
        colors_upper = ['#0065cc']
        colors_wake  = ['#e69f00']
    elif len(dataList) == 2:
        colors_lower = ['#d55e00','#fca7c7']
        colors_upper = ['#0065cc','#56b4ff']
        colors_wake  = ['#e69f00','#ede13f']
    else:
        colors_upper=get_colors(len(dataList),'Blues_r')
        colors_lower=get_colors(len(dataList),'Reds_r')
        colors_wake=get_colors(len(dataList),'Oranges_r')
    
    
    if parameter is None or parameter == 'None':
        if len(dataList) == 1:
            fig = plt.figure(figsize=(10,14), dpi=300)
            axList = []
            gs = GridSpec(7, 2, figure=fig)
            axList.append(fig.add_subplot(gs[0, :]))
            axList.append(fig.add_subplot(gs[1, 0]))
            axList.append(fig.add_subplot(gs[2, 0]))
            axList.append(fig.add_subplot(gs[3, 0]))
            axList.append(fig.add_subplot(gs[4, 0]))
            axList.append(fig.add_subplot(gs[5, 0]))
            axList.append(fig.add_subplot(gs[6, 0]))
            axList.append(fig.add_subplot(gs[1, 1]))
            axList.append(fig.add_subplot(gs[2, 1]))
            axList.append(fig.add_subplot(gs[3, 1]))
            axList.append(fig.add_subplot(gs[4, 1]))
            axList.append(fig.add_subplot(gs[5, 1]))
            axList.append(fig.add_subplot(gs[6, 1]))

            axList[0].set_xlim([-0.01,1.1])
            axList[0].spines[['right', 'left', 'top', 'bottom']].set_visible(False)
            axList[0].set_aspect('equal')
            axList[0].set_xticks([])
            axList[0].set_yticks([])
        else:
            fig = plt.figure(figsize=(10,14), dpi=300)
            axList = []
            gs = GridSpec(6, 2, figure=fig)
            axList.append(fig.add_subplot(gs[0, 0]))
            axList.append(fig.add_subplot(gs[1, 0]))
            axList.append(fig.add_subplot(gs[2, 0]))
            axList.append(fig.add_subplot(gs[3, 0]))
            axList.append(fig.add_subplot(gs[4, 0]))
            axList.append(fig.add_subplot(gs[5, 0]))
            axList.append(fig.add_subplot(gs[0, 1]))
            axList.append(fig.add_subplot(gs[1, 1]))
            axList.append(fig.add_subplot(gs[2, 1]))
            axList.append(fig.add_subplot(gs[3, 1]))
            axList.append(fig.add_subplot(gs[4, 1]))
            axList.append(fig.add_subplot(gs[5, 1]))
        
        for j, data in enumerate(dataList):
            if len(dataList)<=1:
                axList[0].plot(data['bl_data']['x'],data['bl_data']['y'],'k')
                axList[0].plot(data['x_lower'], data['ds_lower'], color='#d55e00')
                axList[0].plot(data['x_upper'], data['ds_upper'], color='#0065cc')

                vshift = min(data['bl_data']['y'])-0.05
                dstr  = r''
                dstr += r'$'
                dstr += r"Re       = %.2e         \qquad "%(data['re'])
                dstr += r"\alpha   = %.4f^{\circ} \qquad "%(data['alpha'])
                dstr += r"C_L      = %.4f         \qquad "%(data['cl']) 
                dstr += r"C_M      = %.4f         \qquad "%(data['cm']) 
                dstr += r"C_D      = %.4f                "%(data['cd'])
                dstr += r'$'
                axList[0].text(0.0, vshift, dstr, fontsize=8)

                dstr2  = r''
                dstr2 += r'$'
                dstr2 += r"L/D      = %.4f         \qquad "%(data['cl']/data['cd'])
                dstr2 += r"N_{cr}   = %.4f         \qquad "%(data['n_crit'])
                dstr2 += r"X_{tr_u} = %.4f         \qquad "%(data['xtr_u'])
                dstr2 += r"X_{tr_l} = %.4f                "%(data['xtr_l'])
                dstr2 += r'$'
                axList[0].text(0.0, vshift-.02, dstr2, fontsize=8)

            for i, nm in enumerate(blNames):
                if len(dataList) > 1:
                    ii = i-1
                    axList[ii+1].plot(data['plot'][nm]['upper'][0],data['plot'][nm]['upper'][1], color=colors_upper[j], label='Data %d'%(dataIndicies[j]))
                else:
                    ii = i
                    axList[ii+1].plot(data['plot'][nm]['upper'][0],data['plot'][nm]['upper'][1], color=colors_upper[j])
                axList[ii+1].plot(data['plot'][nm]['lower'][0],data['plot'][nm]['lower'][1], color=colors_lower[j])
                if data['plot'][nm]['wake']!= []:
                    axList[ii+1].plot(data['plot'][nm]['wake'][0],data['plot'][nm]['wake'][1], color=colors_wake[j])
                if j == 0:
                    axList[ii+1].set_ylabel(data['plot'][nm]['y_label'])
                    if data['plot'][nm]['invert_y']:
                        axList[ii+1].invert_yaxis()
        for ax in axList:
            ax.grid(1)
        if len(dataList) > 1:
            axList[0].legend(fontsize=7)
        
    else:
        fig, ax = plt.subplots(figsize=(10,6), dpi=300)
        nm = parameter

        xlims = [0.0,math.ceil(max(data['plot'][nm]['upper'][0]))]
        
        for j, data in enumerate(dataList):
            if len(dataList)>1:
                plt.plot(data['plot'][nm]['upper'][0],data['plot'][nm]['upper'][1], color=colors_upper[j], label='Data %d'%(dataIndicies[j]))
            else:
                plt.plot(data['plot'][nm]['upper'][0],data['plot'][nm]['upper'][1], color=colors_upper[j])
            plt.plot(data['plot'][nm]['lower'][0],data['plot'][nm]['lower'][1], color=colors_lower[j])
            if data['plot'][nm]['wake']!= [] and nm not in ['tau_w','Cf']:
                plt.plot(data['plot'][nm]['wake'][0],data['plot'][nm]['wake'][1], color=colors_wake[j])
                if j == 0:
                    xlims[1] = math.ceil(max(data['plot'][nm]['wake'][0]))
            if j == 0:
                ax.set_ylabel(data['plot'][nm]['y_label'])
                if data['plot'][nm]['invert_y']:
                    ax.invert_yaxis()
        ax.grid(1)
        plt.xlim(xlims[0]-0.003,xlims[1]+0.003)
        plt.xlabel(r'$x$')
        if len(dataList) > 1:
            plt.legend()
        

    plt.tight_layout()

    return fig