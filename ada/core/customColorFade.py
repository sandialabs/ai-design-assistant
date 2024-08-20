import matplotlib
import numpy as np

def hex_to_uvl(hexColor):
    sRGBTriad = matplotlib.colors.to_rgb(hexColor)
    return rgb_to_uvl(sRGBTriad)

def rgb_to_hex(sRGBTriad):
    for i, vl in enumerate(sRGBTriad):
        sRGBTriad[i] = min([1,sRGBTriad[i]])
        sRGBTriad[i] = max([0,sRGBTriad[i]])
    return matplotlib.colors.to_hex(sRGBTriad)

def uvl_to_XYZ(UVLTriad):
    u,v,lum = UVLTriad
    Y = ((lum+16)/116)**3
    X = -9*Y*u/((u-4)*v-u*v)
    Z = (9*Y-15*v*Y - v*X) / (3 * v)
    return [X,Y,Z]
    
def XYZ_to_rgb(XYZTriad):
    X = XYZTriad[0]
    Y = XYZTriad[1]
    Z = XYZTriad[2]
    xmat = np.array([ [ 3.2406, -1.5372, -0.4986],
                      [-0.9689,  1.8758,  0.0415],
                      [ 0.0557, -0.2040,  1.0570]
                    ])
    sRGBTriad = np.dot(xmat,XYZTriad)
    for i in range(0,len(sRGBTriad)):
        c = sRGBTriad[i]
        if c <= 0.0031308:
            c*=12.92
        else:
            c=1.055*c**(1/2.4)-0.055
        sRGBTriad[i] = c
    return sRGBTriad

def uvl_to_rgb(UVLTriad):
    XYZTriad = uvl_to_XYZ(UVLTriad)
    return XYZ_to_rgb(XYZTriad)

def rgb_to_uvl(sRGBTriad):
    sRGBTriad = np.array(sRGBTriad)
    if sRGBTriad[0]==0 and sRGBTriad[1]==0 and sRGBTriad[2]==0:
        xn = 0.312713
        yn = 0.329016
        un = 4.*xn / ( -2.*xn + 12.*yn + 3. )
        vn = 9.*yn / ( -2.*xn + 12.*yn + 3. )
        return [un,vn,0]
    else:
        XYZTriad = rgb_to_XYZ(sRGBTriad)
        
        X = XYZTriad[0]
        Y = XYZTriad[1]
        Z = XYZTriad[2]
        u = 4*X/(X + 15*Y + 3*Z)
        v = 9*Y/(X + 15*Y + 3*Z)
        if Y <= 216/24389:
            lum = 24389*Y/27
        else:
            lum = 116*Y**(1/3) - 16
        return [u,v,lum]
    
def rgb_to_XYZ(sRGBTriad):
    for i in range(0,len(sRGBTriad)):
        c = sRGBTriad[i]
        if c <= 0.04045:
            c/=12.92
        else:
            c=((c+0.055)/1.055)**2.4
        sRGBTriad[i] = c
        
    xmat = np.array([ [0.4124, 0.3576, 0.1805],
                      [0.2126, 0.7152, 0.0722],
                      [0.0193, 0.1192, 0.9505]
                    ])
    XYZTriad = np.dot(xmat,sRGBTriad)
    return XYZTriad

def customColorFade(baseColor, N_colors):
    
    u_origin,v_origin,tsh = hex_to_uvl('#ffffff')

    ulimit = 0.3
    vlimit = 0.25
    
    umode = np.array([min([ulimit,x]) for x in (1-np.linspace(0,1,101))**1.7])/ulimit
    vmode_1 = np.array([min([vlimit,x]) for x in (1-np.linspace(0,1,101))**1.4])/vlimit
    vmode_2 = np.array([x for x in (np.linspace(0,1,101)-1)**2])

    u_start, v_start, lum_start = hex_to_uvl(baseColor)

    lumArray = np.linspace(33,90,N_colors)
    
    u = (u_start-u_origin)*umode + u_origin
    uvals = np.interp(lumArray, np.linspace(0,100,101), u)
    
    if v_start > v_origin:
        v = (v_start-v_origin)*vmode_1 + v_origin
        vvals = np.interp(lumArray, np.linspace(0,100,101), v)
    else:
        v = (v_start-v_origin)*vmode_2 + v_origin
        vvals = np.interp(lumArray, np.linspace(33,90,101), v)
    
    colorMatrix = np.array([uvals, vvals, lumArray]).T
    colorVec = [rgb_to_hex( uvl_to_rgb(cmr) ) for cmr in colorMatrix]
    return colorVec