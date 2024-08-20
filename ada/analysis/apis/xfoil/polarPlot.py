import numpy as np
import pandas as pd
from ada.geometry.airfoils.kulfan import Kulfan
from matplotlib.gridspec import GridSpec

import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True
plt.rcParams.update({'font.size': 15})
import matplotlib
colors = ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)
matplotlib.use('Agg')

from ada.analysis.apis.xfoil.helperFunctions import truncate_colormap, handleZeroDivide, get_colors, computeNormals, get_fractional_color

def polarPlot(dataList):
    for data in dataList:
        assert(isinstance(data,list))
        for de in data:
            assert(isinstance(de,dict))

    colorCycle = ['Blues','Oranges','Greens','Purples','Reds']
    assert(len(dataList)<=len(colorCycle))

    dataframeList = []
    for data in dataList:
        dataDict = {}
        dataDict['alpha']    = [] #np.zeros(len(data))
        dataDict['cl']       = [] #np.zeros(len(data))
        dataDict['cd']       = [] #np.zeros(len(data))
        dataDict['cm']       = [] #np.zeros(len(data))
        dataDict['xtp_u']    = [] #np.zeros(len(data))
        dataDict['xtp_l']    = [] #np.zeros(len(data))    
        dataDict['xtr_u']    = [] #np.zeros(len(data))
        dataDict['xtr_l']    = [] #np.zeros(len(data))
        dataDict['re']       = [] #np.zeros(len(data))
        dataDict['m']        = [] #np.zeros(len(data))
        dataDict['n_crit']   = [] #np.zeros(len(data))
        dataDict['n_panels'] = [] #np.zeros(len(data))

        for i,rdata in enumerate(data):
            if rdata is not None:
                for ky in dataDict.keys():
                    if ky in list(rdata.keys()):
                        vl = rdata[ky]
                    else:
                        raise ValueError('Could not find key: %s'%(ky))
                    dataDict[ky].append( vl )

        assert( len(np.unique(dataDict['m'])) == 1)
        assert( len(np.unique(dataDict['xtp_u'])) == 1)
        assert( len(np.unique(dataDict['xtp_l'])) == 1)
        assert( len(np.unique(dataDict['n_crit'])) == 1)
        assert( len(np.unique(dataDict['n_panels'])) == 1)

        df = pd.DataFrame.from_dict(dataDict)
        dataframeList.append(df)

    re_min = np.inf
    re_max = 0.0

    for df in dataframeList:
        re_arr = np.array(df['re'].to_list())
        re_min = min([re_min, min(re_arr)])
        re_max = max([re_max, max(re_arr)])

    fig = plt.figure(figsize=(20,16), dpi=300)
    gs = GridSpec(2,2, figure=fig)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])
    ax3 = fig.add_subplot(gs[1,1])

    for i,df in enumerate(dataframeList):
        for Re_value in np.unique(np.array(df['re'].to_list()).round(0)):
            if re_min == re_max:
                plot_color = get_fractional_color(1.0, colorCycle[i], lower=0.6, upper=0.6)
            else:
                color_frac = (np.log10(Re_value) - np.log10(re_min)) / (np.log10(re_max)-np.log10(re_min))
                plot_color = get_fractional_color(color_frac, colorCycle[i], lower=0.3, upper=0.8)

            commonRe = df.loc[(abs(df['re'] - Re_value) <= 1)]
            commonRe.sort_values('alpha')
            if i==0:
                ax1.plot(commonRe['cd'],commonRe['cl'], label='Re=%.2e'%(Re_value), color = plot_color)
            else:
                ax1.plot(commonRe['cd'],commonRe['cl'], color = plot_color)
            ax1.set_xlim([0,0.05])
            ax1.set_ylabel('$C_L$')
            ax1.set_xlabel('$C_D$')
            ax1.grid(1)
            ax1.legend()

            if i==0:
                ax2.plot(commonRe['alpha'],commonRe['cl'], label='Re=%.2e'%(Re_value), color = plot_color)
            else:
                ax2.plot(commonRe['alpha'],commonRe['cl'], color = plot_color)
            ax2.set_ylabel('$C_L$')
            ax2.set_xlabel(r'$\alpha$')
            ax2.grid(1)
            ax2.legend()

            if i==0:
                ax3.plot(commonRe['alpha'],commonRe['cm'], label='Re=%.2e'%(Re_value), color = plot_color)
            else:
                ax3.plot(commonRe['alpha'],commonRe['cm'], color = plot_color)
            ax3.set_ylabel('$C_M$')
            ax3.set_xlabel(r'$\alpha$')
            ax3.grid(1)
            ax3.legend()

    plt.tight_layout()

    return fig








