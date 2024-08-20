import subprocess
import struct
import copy
import os
import math
import shutil
import pathlib
import numpy as np
import pandas as pd
from ada.geometry.airfoils.kulfan import Kulfan

path_to_XFOIL = shutil.which('xfoil')
path_to_here = pathlib.Path(__file__).parent.resolve()


def readSensx(filename = 'sensx.afl'):
    f = open(filename,'rb')
    allData = f.read()
    f.close()

    checksumArray = []

    # allData = allData.replace(b'\n',b' ')
    # allData = allData.replace(b' ',b'')
    # buffer = bytes.fromhex(allData.decode('utf-8'))  # need if copy paste actual hex in sublime, otherwise no
    buffer = allData

    sizeof_int = 4
    sizeof_char = 1
    sizeof_double = 8

    pointer = 0

    def movePointer(buffer, pointer, moveBytes, typeKey, notrunc=False):
        dta = struct.unpack(typeKey,buffer[pointer:pointer+moveBytes])
        pointer += moveBytes
        if notrunc:
            return dta, pointer
        else:
            return dta[0], pointer
        
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    dta,           pointer = movePointer(buffer,pointer,32,'32s')           # MSES
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    dta,           pointer = movePointer(buffer,pointer,32,'32s')           # Airfoil
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    kalpha,        pointer = movePointer(buffer,pointer,sizeof_int,'i')
    kM,         pointer = movePointer(buffer,pointer,sizeof_int,'i')
    kreyn,         pointer = movePointer(buffer,pointer,sizeof_int,'i')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    ldepma,        pointer = movePointer(buffer,pointer,sizeof_int,'i')
    ldepre,        pointer = movePointer(buffer,pointer,sizeof_int,'i')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    alpha,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    M,          pointer = movePointer(buffer,pointer,sizeof_double,'d')
    reyn,          pointer = movePointer(buffer,pointer,sizeof_double,'d')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    dnrms,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    drrms,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    dvrms,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    dnmax,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    drmax,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    dvmax,         pointer = movePointer(buffer,pointer,sizeof_double,'d')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    ii,            pointer = movePointer(buffer,pointer,sizeof_int,'i')
    nbl,           pointer = movePointer(buffer,pointer,sizeof_int,'i')
    nmod,          pointer = movePointer(buffer,pointer,sizeof_int,'i')
    npos,          pointer = movePointer(buffer,pointer,sizeof_int,'i')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    ileb = []
    iteb = []
    for i in range(0,nbl):
        dta,           pointer = movePointer(buffer,pointer,sizeof_int,'i')
        ileb.append(dta)
        dta,           pointer = movePointer(buffer,pointer,sizeof_int,'i')
        iteb.append(dta)
    end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    xleb   = []
    yleb   = []
    xteb   = []
    yteb   = []
    sblegn = []
    for i in range(0,nbl):
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        xleb.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        yleb.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        xteb.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        yteb.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        sblegn.append(dta)
    end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
    checksumArray.append(beg == end)
    beg,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
    cl,            pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cm,            pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdw,           pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdv,           pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdf,           pointer = movePointer(buffer,pointer,sizeof_double,'d')
    al_alfa,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cl_alfa,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cm_alfa,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdw_alfa,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdv_alfa,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdf_alfa,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    al_M,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cl_M,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cm_M,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdw_M,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdv_M,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdf_M,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    al_reyn,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cl_reyn,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cm_reyn,       pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdw_reyn,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdv_reyn,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    cdf_reyn,      pointer = movePointer(buffer,pointer,sizeof_double,'d')
    end,           pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
        
    iend = [0]*len(ileb)
    for i in range(0,nbl):
        ioff = ileb[i]-1
        ileb[i] -= ioff
        iteb[i] -= ioff
        iend[i] = ii-ioff

    xbi = []
    ybi = []
    cp = []
    hk = []
    cp_alfa = []
    hk_alfa = []
    cp_M = []
    hk_M = []
    cp_reyn = []
    hk_reyn = []

    for i in range(0,nbl):
        j = iend[i] - ileb[i]
        for k in range(0,2):
            xbi.append(np.zeros(j))
            ybi.append(np.zeros(j))
            cp.append(np.zeros(j))
            hk.append(np.zeros(j))
            cp_alfa.append(np.zeros(j))
            hk_alfa.append(np.zeros(j))
            cp_M.append(np.zeros(j))
            hk_M.append(np.zeros(j))
            cp_reyn.append(np.zeros(j))
            hk_reyn.append(np.zeros(j))
            beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
            for m in range(0,j):
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                xbi[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                ybi[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                cp[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                hk[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                cp_alfa[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                hk_alfa[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                cp_M[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                hk_M[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                cp_reyn[2*i+k][m] = dta
                dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                hk_reyn[2*i+k][m] = dta
            end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
            checksumArray.append(beg == end)
            

    modn    = []
    al_mod  = []
    cl_mod  = []
    cm_mod  = []
    cdw_mod = []
    cdv_mod = []
    cdf_mod = []
    gn = [[None for jjj in range(0,2*(nbl-1)+2)] for i in range(0,nmod)]
    xbi_mod = [[None for jjj in range(0,2*(nbl-1)+2)] for i in range(0,nmod)]
    ybi_mod = [[None for jjj in range(0,2*(nbl-1)+2)] for i in range(0,nmod)]
    cp_mod = [[None for jjj in range(0,2*(nbl-1)+2)] for i in range(0,nmod)]
    hk_mod = [[None for jjj in range(0,2*(nbl-1)+2)] for i in range(0,nmod)]

    # for k in range(0,nmod):   
    for k in range(0,40):   
        beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        modn.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        al_mod.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        cl_mod.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        cm_mod.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        cdw_mod.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        cdv_mod.append(dta)
        dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
        cdf_mod.append(dta)
        end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
        checksumArray.append(beg == end)

        for ib in range(0,nbl):
            for ix in range(0,2):
                j = iteb[ib] - ileb[ib] + 1
                beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
                dta, pointer = movePointer(buffer,pointer,sizeof_double*j,'d'*j, notrunc=True)
                gn[k][2*ib+ix] = dta
                end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
                checksumArray.append(beg == end)
                
                j = iend[ib] - ileb[ib]
                beg, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &begMarker
                xbi_row = []
                ybi_row = []
                cp_row = []
                hk_row = []
                for m in range(0,j):
                    dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                    xbi_row.append(dta)
                    dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                    ybi_row.append(dta)
                    dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                    cp_row.append(dta)
                    dta, pointer = movePointer(buffer,pointer,sizeof_double,'d')
                    hk_row.append(dta)
                end, pointer = movePointer(buffer,pointer,sizeof_int,'i')     # &endMarker
                checksumArray.append(beg == end)
                
                xbi_mod[k][2*ib+ix] = xbi_row
                ybi_mod[k][2*ib+ix] = ybi_row
                cp_mod[k][2*ib+ix]  = cp_row
                hk_mod[k][2*ib+ix]  = hk_row

    if all(checksumArray):
        # print('Markers all match')
        pass
    else:
        raise ValueError('Import markers do not match')

    outDict = {}

    outDict['kalpha']    = kalpha
    outDict['kM']     = kM
    outDict['kreyn']     = kreyn
    outDict['ldepma']    = ldepma
    outDict['ldepre']    = ldepre
    outDict['alpha']     = alpha
    outDict['M']      = M
    outDict['reyn']      = reyn
    outDict['dnrms']     = dnrms
    outDict['drrms']     = drrms
    outDict['dvrms']     = dvrms
    outDict['dnmax']     = dnmax
    outDict['drmax']     = drmax
    outDict['dvmax']     = dvmax
    outDict['ii']        = ii
    outDict['nbl']       = nbl
    outDict['nmod']      = nmod
    outDict['npos']      = npos
    outDict['ileb']      = ileb
    outDict['iteb']      = iteb
    outDict['xleb']      = xleb
    outDict['yleb']      = yleb
    outDict['xteb']      = xteb
    outDict['yteb']      = yteb
    outDict['sblegn']    = sblegn
    outDict['cl']        = cl
    outDict['cm']        = cm
    outDict['cdw']       = cdw
    outDict['cdv']       = cdv
    outDict['cdf']       = cdf
    outDict['al_alfa']   = al_alfa
    outDict['cl_alfa']   = cl_alfa
    outDict['cm_alfa']   = cm_alfa
    outDict['cdw_alfa']  = cdw_alfa
    outDict['cdv_alfa']  = cdv_alfa
    outDict['cdf_alfa']  = cdf_alfa
    outDict['al_M']   = al_M
    outDict['cl_M']   = cl_M
    outDict['cm_M']   = cm_M
    outDict['cdw_M']  = cdw_M
    outDict['cdv_M']  = cdv_M
    outDict['cdf_M']  = cdf_M
    outDict['al_reyn']   = al_reyn
    outDict['cl_reyn']   = cl_reyn
    outDict['cm_reyn']   = cm_reyn
    outDict['cdw_reyn']  = cdw_reyn
    outDict['cdv_reyn']  = cdv_reyn
    outDict['cdf_reyn']  = cdf_reyn
    outDict['xbi']       = xbi
    outDict['ybi']       = ybi
    outDict['cp']        = cp
    outDict['hk']        = hk
    outDict['cp_alfa']   = cp_alfa
    outDict['hk_alfa']   = hk_alfa
    outDict['cp_M']   = cp_M
    outDict['hk_M']   = hk_M
    outDict['cp_reyn']   = cp_reyn
    outDict['hk_reyn']   = hk_reyn
    outDict['modn']      = modn
    outDict['al_mod']    = al_mod
    outDict['cl_mod']    = cl_mod
    outDict['cm_mod']    = cm_mod
    outDict['cdw_mod']   = cdw_mod
    outDict['cdv_mod']   = cdv_mod
    outDict['cdf_mod']   = cdf_mod
    outDict['gn']        = gn
    outDict['xbi_mod']   = xbi_mod
    outDict['ybi_mod']   = ybi_mod
    outDict['cp_mod']    = cp_mod
    outDict['hk_mod']    = hk_mod


    return outDict
            








def runSingleCase(mode, 
          airfoil,
          val = 0.0, 
          Re = 1e7,
          M = 0.0,
          xtr_u=1.0,
          xtr_l=1.0,
          N_crit=9.0,
          N_panels = 160,
          ext = 'afl',
          # flapLocation = None,
          # flapDeflection = 0.0,
          # polarfile='polars.txt',
          # cpDatafile='cp_x.txt',
          # blDatafile='bl.txt',
          # defaultDatfile = 'airfoil.dat',
          # saveDatfile = False,
          msesFile = None, 
          modesFile = None, 
          paramsFile = None,
          ISMOM_overwrite = None,
          removeData = True,
          domain = [-1.75,2.0,-2.0,2.5],
          iteration_sequence=[-20,100]):

    modeNumber = 20 # number of modes used by mses, probably should not change
    pVal = 0.0 # default polynomial perturbation coefficient, probably should not change


    mode = mode.lower()
    if mode == 'alpha':
        mode = 'alfa'

    if mode not in ['alfa','cl']:
        raise ValueError('Invalid input mode.  Must be one of: alfa, cl ')

    path_to_mses = shutil.which('mses')
    path_to_mset = shutil.which('mset')

    if isinstance(airfoil, str):        
        if ('blade.') in airfoil:
            if os.path.isfile(airfoil):
                shutil.copy(airfoil,'blade.' + ext)
            else:
                raise ValueError('Could not find airfoil to be read')
        else:
            if isinstance(airfoil, Kulfan):
                afl.utility.Npoints = int(math.ceil(N_panels/2.0))
                coords = afl.coordinates
            elif ('.dat' in airfoil) or ('.txt' in airfoil):
                if os.path.isfile(airfoil):
                    afl = Kulfan()
                    afl.fit2file(airfoil)
                    afl.utility.Npoints = int(math.ceil(N_panels/2.0))
                    coords = afl.coordinates
                else:
                    raise ValueError('Could not find airfoil to be read')
            else:
                ck1 = 'naca' == airfoil.lower()[0:4]
                ck2 = airfoil[-4:].isdigit()
                if ck1:
                    if ck2 and (len(airfoil)!=8):
                        afl = airfoil.split()
                        airfoil = ''.join(afl)
                    afl = Kulfan()
                    afl.naca4(airfoil[-4:])
                    afl.utility.Npoints = int(math.ceil(N_panels/2.0))
                    # else:
                    #     raise ValueError('Could not parse the NACA 4 digit airfoil')
                else:
                    raise ValueError('The provided airfoil name "%s" cannot be parsed'%(airfoil))
            coords = afl.coordinates
            pstr = ''
            pstr += 'Airfoil \n'
            pstr += '%f %f %f %f \n'%(domain[0], domain[1], domain[2], domain[3]) # xmin, xmax, ymin, ymax
            for rw in coords:
                pstr += '%f %f \n'%(rw[0],rw[1])
            f = open('blade.'+ext,'w')
            f.write(pstr)
            f.close()

            # else:
            #     raise ValueError('Could not parse airfoil')

    if msesFile is None:
        msesFile  = 'mses.'  + ext
        pstr = ''
        pstr += '3 4 5 7 10 15 20 \n'
        if mode == 'alfa':
            pstr += '3 4 5 7 15 17 20 \n'
            pstr += '%.4f %.4f %.4f | MACHIN  CLIFIN ALFAIN \n'%(M,0.0,val)
        else:
            pstr += '3 4 6 7 15 17 20 \n'
            pstr += '%.4f %.4f %.4f | MACHIN  CLIFIN ALFAIN \n'%(M,val,0.0)
        if ISMOM_overwrite is not None:
            if ISMOM_overwrite == 2:
                pstr += '2 2            | ISMOM   IFFBC\n'
            elif ISMOM_overwrite == 4:
                pstr += '4 2            | ISMOM   IFFBC\n'
            else:
                raise ValueError('ISMOM overwrite value must be either 2 (M~<0.2) or 4 (M~>0.2)')
        else:
            if M < 0.15:
                pstr += '2 2            | ISMOM   IFFBC\n'
            else:
                pstr += '4 2            | ISMOM   IFFBC\n'
        pstr += '%.2f %.4f     | REYNIN  ACRIT\n'%(Re, N_crit)
        pstr += '%.4f %.4f        | XTRS    XTRP\n'%(xtr_u, xtr_l)
        pstr += '0.98 1.0       | MCRIT   MUCON\n'
        pstr += '1 1            | ISMOVE  ISPRES\n'
        pstr += '40 0           | NMOD    NPOS\n'
        f = open(msesFile,'w')
        f.write(pstr)
        f.close()
    else:
        shutil.copy(msesFile,'mses.'+ext)

    if modesFile is None:
        modesFile = 'modes.' + ext
        pstr = ''
        for i in range(0,20):
            pstr += '%d   %d   1.0   0.0   1.0   1\n'%(i+1, 21+i) # Upper Surface Modes
        for i in range(0,20):
            pstr += '%d   %d   1.0   0.0   -1.0   1\n'%(21+i, 21+i) # Lower surface modes
        f = open(modesFile,'w')
        f.write(pstr)
        f.close()
    else:
        shutil.copy(modesFile,'modes.'+ext)

    if paramsFile is None:
        paramsFile = 'params.' + ext
        pstr = ''
        pstr += '40   0 \n'
        for i in range(0,40):
            if modeNumber-1 == i:
                pstr += '%e \n'%(pVal)
            else:
                pstr += '0.00 \n'
        if mode == 'alfa':
            pstr += '%.5f  %.5f  %.5f  %.5f'%(val, 0.0, M, Re)
        else:
            pstr += '%.5f  %.5f  %.5f  %.5f'%(0.0, val, M, Re)
        f = open(paramsFile,'w')
        f.write(pstr)
        f.close()
    else:
        shutil.copy(paramsFile,'params.'+ext)


    proc = subprocess.Popen([path_to_mset + ' ' + ext], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    estr = ''
    estr += '1\n'
    if mode == 'alfa':
        estr += '%f\n'%(val)
    else:
        estr += '%f\n'%(val/(2*np.pi) *180/(2*np.pi)) # approximates alpha using thin airfoil theory, CL=2*pi*alpha(radians)
    estr += '2\n'
    estr += '\n'
    estr += '3\n'
    estr += '4\n'
    estr += '0\n'
    f = open('msetRun.txt','w')
    f.write(estr)
    f.close()
    proc.stdin.write(estr.encode())
    stdout_val_mset = proc.communicate()[0]
    proc.stdin.close()

    proc = subprocess.Popen([path_to_mses + ' ' + ext], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    estr = ''
    for ir in iteration_sequence:
        estr += '%+d\n'%(ir)
    estr += '0\n'

    f = open('msesRun.txt','w')
    f.write(estr)
    f.close()
    proc.stdin.write(estr.encode())
    stdout_val_mses = proc.communicate()[0]
    proc.stdin.close()

    # dataDct = {}
    # dataDct['sensFileRead'] = readSensx('sensx.'+ext)
    
    msetOutputString = stdout_val_mset.decode()
    msesOutputString = stdout_val_mses.decode()

    if msesOutputString.count('Converged on tolerance') != len(iteration_sequence):
        raise RuntimeError('MSES failed to converge')

    sensFileRead = readSensx('sensx.'+ext)
    sensFileRead['msetOutput'] = msetOutputString
    sensFileRead['msesOutput'] = msesOutputString


    # transition locations not in file for some reason, need to get
    msesOutputString_lines = msesOutputString.split('\n')

    xtr_u = -1.0
    xtr_l = -1.0
    for i in range(0,len(msesOutputString_lines)):
        if xtr_u != -1 and xtr_l != -1:
            break

        ln = msesOutputString_lines[-i]
        if 'transition at  X (x/c) i' in ln:
            ents = ln.split()
            for j,vl in enumerate(ents):
                if vl == '=':
                    trLoc = ents[j+1]
                    break
            if xtr_l == -1:
                xtr_l = trLoc
            else:
                xtr_u = trLoc

    sensFileRead['xtr_top'] = xtr_u
    sensFileRead['xtr_bot'] = xtr_l
    sensFileRead['N_crit'] = N_crit
    sensFileRead['N_panels'] = N_panels


    if removeData:
        os.remove('msesRun.txt')
        os.remove('msetRun.txt')
        os.remove('blade.' + ext)
        os.remove('mses.' + ext)
        os.remove('mdat.' + ext)
        os.remove('modes.' + ext)
        os.remove('params.' + ext)
        os.remove('sensx.' + ext)

    return sensFileRead




# if __name__ == '__main__':
#     dta = runSingleCase('alpha', 
#       'NACA2412',
#       val = 3.0, 
#       Re = 1e7,
#       M = 0.1,
#       xtr_u=1.0,
#       xtr_l=1.0,
#       N_crit=9.0,
#       N_panels = 160,
#       ext = 'afl',
#       removeData = True,
#       domain = [-1.75,2.0,-2.0,2.5],
#       iteration_sequence=[-20,100])

#     print(dta['msesOutput'])
#     print(dta['xtr_u'])
#     print(dta['xtr_l'])
