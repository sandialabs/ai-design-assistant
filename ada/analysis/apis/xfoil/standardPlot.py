import numpy as np
from ada.geometry.airfoils.kulfan import Kulfan
from matplotlib.gridspec import GridSpec

import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
plt.rcParams.update({'font.size': 15})
import matplotlib
colors = ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)
from matplotlib.colors import ListedColormap
matplotlib.use('Agg')

from ada.analysis.apis.xfoil.helperFunctions import truncate_colormap, handleZeroDivide, get_colors, computeNormals

def standardPlot(dataList):
    if len(dataList) > 3:
        raise ValueError('You really dont want to do this, compare fewer data sets (please dont do more than 2, but this function will allow 3)')
        
    if len(dataList)==1:
        figHeight = 8
    elif len(dataList)==2:
        figHeight = 10
    else:
        figHeight = 6+2*len(dataList)
    fig = plt.figure(figsize=(10,figHeight), dpi=300)

    gs = GridSpec(len(dataList)+2, 1, figure=fig)
    ax1 = fig.add_subplot(gs[0:2, 0])
    afl_axes = [fig.add_subplot(gs[2+i, 0]) for i in range(0,len(dataList))]

    ax1.plot([-0.1,1.1],[0,0],color='k')
    tickHeight = 0.05
    for xtick in np.linspace(0,1,11):
        ax1.plot([xtick,xtick],[-tickHeight,tickHeight],color='k')

    xlims = [-0.1,1.1]
    ax1.set_xlim(xlims)

    ax1.set_ylabel(r'$C_p$')
    ax1.spines[['right', 'top', 'bottom']].set_visible(False)
    ax1.set_xticks([])

    for ax in afl_axes:
        ax.spines[['right', 'left', 'top', 'bottom']].set_visible(False)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
    
    if len(dataList) == 1:
        colors_lower = ['#d55e00']
        colors_upper = ['#0065cc']
    elif len(dataList) == 2:
        colors_lower = ['#d55e00','#fca7c7']
        colors_upper = ['#0065cc','#56b4ff']
    else:
        colors_upper=get_colors(len(dataList),'Blues_r')
        colors_lower=get_colors(len(dataList),'Reds_r')
        
    for ii,data in enumerate(dataList):
        # data has:
        #    data['alpha'] 
        #    data['cl']
        #    data['cm']
        #    data['cd']
        #    data['re']
        #    data['n_crit']
        #    data['xtr_u']
        #    data['xtr_l']
        #    data['cp_data']['x']
        #    data['cp_data']['cp']
        #    data['bl_data']['x']
        #    data['bl_data']['y']
        #    data['bl_data']['Dstar']
        
        wake_index = next(k for k, value in enumerate(data['bl_data']['x']) if value > 1)
        lower_te_shift = 0.0
        if abs(data['bl_data']['x'][wake_index] - 1.0) < 1e-3 and abs(data['bl_data']['y'][wake_index])<1e-3:
            # blunt trailing egde
            lower_te_shift = data['bl_data']['y'][wake_index-1]
        
        stagnation_index = data['cp_data']['cp'].index(max(data['cp_data']['cp']))
        x_upper  = data['cp_data']['x'][0:stagnation_index+1]
        x_lower  = data['cp_data']['x'][stagnation_index:]
        cp_upper = data['cp_data']['cp'][0:stagnation_index+1]
        cp_lower = data['cp_data']['cp'][stagnation_index:]

        # stagnation_index = data['cp_data']['cp'].index(max(data['cp_data']['cp']))
        x_upper  = data['cp_data']['x'][0:stagnation_index+1]
        x_lower  = data['cp_data']['x'][stagnation_index:]
        cp_upper = data['cp_data']['cp'][0:stagnation_index+1]
        cp_lower = data['cp_data']['cp'][stagnation_index:]

        ax1.plot(x_lower, cp_lower, color = colors_lower[ii])
        ax1.plot(x_upper, cp_upper, color = colors_upper[ii])

        ax1.set_ylim([min([-2,min(cp_upper)-0.1]),1.1])
        
        afl_axes[ii].set_xlim(xlims)
        if lower_te_shift != 0:
            afl_axes[ii].plot([data['bl_data']['x'][0]]+data['bl_data']['x'],[lower_te_shift]+data['bl_data']['y'],'k')
        else:
            afl_axes[ii].plot(data['bl_data']['x'],data['bl_data']['y'],'k')

        xmin_index = data['bl_data']['x'].index(min(data['bl_data']['x']))

        normals = computeNormals(data['bl_data']['x'],data['bl_data']['y'])

        split_frac = None
        boundaryLayerPoints = []
        for i,nm in enumerate(normals):
            x = data['bl_data']['x'][i]
            y = data['bl_data']['y'][i]
            dorun = True
            # if i>0:
            if data['bl_data']['x'][i]>=1 and data['bl_data']['x'][i-1]<=1 :
                # skip the points where the lower surface transitons to the wake, along with the first point (upper TE)
                dorun=False
                split_frac = data['bl_data']['Dstar'][0] / (data['bl_data']['Dstar'][i-1]+data['bl_data']['Dstar'][0])
                
            if dorun and i>0 and i != wake_index:
                # skip the last two points on the trailing edge, and the first one in the wake
                # makes the plot smoother and avoids issues with the normal on a blunt trailing edge
                amp = 1
                sc = data['bl_data']['Dstar'][i]*amp
                if split_frac is not None:
                    xshift = x - nm[0]*sc*(1-split_frac)
                    yshift = y - nm[1]*sc*(1-split_frac) + lower_te_shift
                    boundaryLayerPoints = [[xshift+nm[0]*sc, yshift+nm[1]*sc]] + boundaryLayerPoints
                    stagnation_index += 1
                    boundaryLayerPoints.append([xshift, yshift])
                else:
                    boundaryLayerPoints.append([x+nm[0]*sc, y+nm[1]*sc])

        boundaryLayerPoints = np.array(boundaryLayerPoints)

        stagnation_index -= 1
        x_upper  = boundaryLayerPoints[0:stagnation_index+1, 0]
        x_lower  = boundaryLayerPoints[stagnation_index:   , 0]
        ds_upper = boundaryLayerPoints[0:stagnation_index+1, 1]
        ds_lower = boundaryLayerPoints[stagnation_index:   , 1]

        afl_axes[ii].plot(x_lower, ds_lower, color = colors_lower[ii])
        afl_axes[ii].plot(x_upper, ds_upper, color = colors_upper[ii])

        if len(dataList) == 1:
            dstr  = r''
            dstr += r"\begin{eqnarray*}"
            dstr += r"Re       &=& %.2e         \\"%(data['re'])
            dstr += r"\alpha   &=& %.4f^{\circ} \\"%(data['alpha'])
            dstr += r"C_L      &=& %.4f         \\"%(data['cl']) 
            dstr += r"C_M      &=& %.4f         \\"%(data['cm']) 
            dstr += r"C_D      &=& %.4f         \\"%(data['cd'])
            dstr += r"L/D      &=& %.4f         \\"%(data['cl']/data['cd'])
            dstr += r"N_{cr}   &=& %.4f         \\"%(data['n_crit'])
            dstr += r"X_{tr_u} &=& %.4f         \\"%(data['xtr_u'])
            dstr += r"X_{tr_l} &=& %.4f         \\"%(data['xtr_l'])
            dstr += r"\end{eqnarray*}"
            
            ax1.text(0.8, 0.95, dstr,  transform=ax1.transAxes) 
        else:
            vshift = max(data['bl_data']['y'])+0.04
            dstr  = r''
            dstr += r'$'
            dstr += r"Re       = %.2e         \qquad "%(data['re'])
            dstr += r"\alpha   = %.4f^{\circ} \qquad "%(data['alpha'])
            dstr += r"C_L      = %.4f         \qquad "%(data['cl']) 
            dstr += r"C_M      = %.4f         \qquad "%(data['cm']) 
            dstr += r"C_D      = %.4f                "%(data['cd'])
            dstr += r'$'
            afl_axes[ii].text(0.15, vshift, dstr, fontsize=8)
            
            dstr2  = r''
            dstr2 += r'$'
            dstr2 += r"L/D      = %.4f         \qquad "%(data['cl']/data['cd'])
            dstr2 += r"N_{cr}   = %.4f         \qquad "%(data['n_crit'])
            dstr2 += r"X_{tr_u} = %.4f         \qquad "%(data['xtr_u'])
            dstr2 += r"X_{tr_l} = %.4f                "%(data['xtr_l'])
            dstr2 += r'$'
            afl_axes[ii].text(0.15, vshift-.02, dstr2, fontsize=8)

    ax1.invert_yaxis()
    plt.tight_layout()

    return fig