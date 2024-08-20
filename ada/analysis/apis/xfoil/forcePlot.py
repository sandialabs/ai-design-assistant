import numpy as np
from ada.geometry.airfoils.kulfan import Kulfan
from matplotlib.gridspec import GridSpec

import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
plt.rcParams.update({'font.size': 15})
import matplotlib
colors = ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)
matplotlib.use('Agg')

from ada.analysis.apis.xfoil.helperFunctions import truncate_colormap, handleZeroDivide, get_colors, computeNormals


def forcePlot(data):
        
    fig = plt.figure(figsize=(10,6), dpi=300)

    xdata = data['bl_data']['x']
    ydata = data['bl_data']['y']
    wake_index = next(x[0] for x in enumerate(xdata) if x[1] > 1.0)
    xdata = xdata[0:wake_index]
    ydata = ydata[0:wake_index]
    normals = computeNormals(xdata,ydata)

    hasBlue = False
    hasRed = False
    for i,nm in enumerate(normals):
        x = xdata[i]
        y = ydata[i]

        amp = 0.25
        sc = data['cp_data']['cp'][i]*amp#/max(abs(np.array(data['cp_data']['cp'])))
        if sc > 0:
            clr = colors[0]
        else:
            clr = colors[3]

        if clr == colors[0] and not hasBlue:
            plt.plot([x,x+nm[0]*abs(sc)],[y,y+nm[1]*abs(sc)], clr, lw=1, label='Positive Pressure')
            hasBlue = True
        elif clr == colors[3] and not hasRed:
            plt.plot([x,x+nm[0]*abs(sc)],[y,y+nm[1]*abs(sc)], clr, lw=1, label='Suction')
            hasRed = True
        else:
            plt.plot([x,x+nm[0]*abs(sc)],[y,y+nm[1]*abs(sc)], clr, lw=1)

    plt.plot(xdata,ydata,'k')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.axis('equal')

    return fig
