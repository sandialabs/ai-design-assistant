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

def polarPlot(data):

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
                if ky in list(rdata.inputs.keys()):
                    vl = rdata.inputs[ky]
                elif ky in list(rdata.outputs.keys()):
                    vl = rdata.outputs[ky]
                else:
                    raise ValueError('Could not find key: %s'%(ky))
                dataDict[ky].append( vl )

    df = pd.DataFrame.from_dict(dataDict)
    
    fig = plt.figure(figsize=(20,16), dpi=300)
    gs = GridSpec(2,2, figure=fig)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])
    ax3 = fig.add_subplot(gs[1,1])
    

    for Re_value in np.unique(np.array(df['re'].to_list()).round(0)):

        commonRe = df.loc[(abs(df['re'] - Re_value) <= 1)]
        commonRe.sort_values('alpha')
        ax1.plot(commonRe['cd'],commonRe['cl'], label='Re=%.2e'%(Re_value))
        ax1.set_xlim([0,0.05])
        ax1.set_ylabel('$C_L$')
        ax1.set_xlabel('$C_D$')
        ax1.grid(1)
        ax1.legend()

        ax2.plot(commonRe['alpha'],commonRe['cl'], label='Re=%.2e'%(Re_value))
        ax2.set_ylabel('$C_L$')
        ax2.set_xlabel(r'$\alpha$')
        ax2.grid(1)
        ax2.legend()

        ax3.plot(commonRe['alpha'],commonRe['cm'], label='Re=%.2e'%(Re_value))
        ax3.set_ylabel('$C_M$')
        ax3.set_xlabel(r'$\alpha$')
        ax3.grid(1)
        ax3.legend()

    plt.tight_layout()

    return fig



if __name__ == '__main__':
    from ada.geometry.airfoils.kulfan import Kulfan
    from ada.analysis.apis.xfoil.runSingleCase import runSingleCase

    afl = Kulfan()
    afl.naca4_like(2,4,24)

    results = []
    for alpha in np.linspace(-10,25,15):
        for Re in 10**np.linspace(6,8,3):
            for M in [0]:
                try:
                    res = runSingleCase('alpha',afl,alpha, Re = Re, M=M, N_panels=160, N_crit=9.0, xtr_u=1.0, xtr_l=1.0)
                    results.append(res)
                except:
                    # should have enough data, an occasional failure is ok
                    pass

    polarPlot(results)







