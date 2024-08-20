import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
import math


def handleZeroDivide(num,dem):
    if dem == 0:
        return np.inf
    else:
        return num/dem
    
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def get_colors(N, selectedMap, lower = 0.15, upper = 0.75):
    cmap = plt.get_cmap(selectedMap)
    cmap = truncate_colormap(cmap,lower, upper)
    norm = plt.Normalize(0, N - 1)
    colors = cmap(norm(np.arange(N)))
    return colors

def get_fractional_color(frac, selectedMap, lower=0.15, upper=0.75):
    colors = get_colors(101, selectedMap, lower, upper)
    return(colors[int(math.floor(frac*100.0))])

def computeNormals(xdata, ydata):
    xmin_index = xdata.index(min(xdata))
    normals = []
    for i, x in enumerate(xdata):
        y = ydata[i]

        if i == 0:
            x_p1 = xdata[i+1]
            x_m1 = x
            y_p1 = ydata[i+1]
            y_m1 = y

            dxdy = handleZeroDivide(y_p1-y, x_p1-x)

        elif i == len(xdata)-1:
            x_p1 = x
            x_m1 = xdata[i-1]
            y_p1 = y
            y_m1 = ydata[i-1]

            dxdy = handleZeroDivide(y-y_m1, x-x_m1)

        else:
            x_p1 = xdata[i+1]
            x_m1 = xdata[i-1]
            y_p1 = ydata[i+1]
            y_m1 = ydata[i-1]

            dxdy_p1 = handleZeroDivide(y_p1-y, x_p1-x)
            dxdy_m1 = handleZeroDivide(y-y_m1, x-x_m1)

            if dxdy_p1!=dxdy_m1 and max([dxdy_p1,dxdy_m1])==np.inf:
                dxdy = min([dxdy_p1,dxdy_m1])
            else:
                dxdy = handleZeroDivide(y_p1-y_m1, x_p1-x_m1)

        if dxdy == 0.0:
            normal = [0,1]
        elif dxdy == np.inf:
            normal = [1,0]
        else:
            normal =  [ 1/(1+1/dxdy**2)**0.5, -1/dxdy/(1+1/dxdy**2)**0.5 ]

        if i<=xmin_index:
            # in upper
            if normal[1] < 0:
                normal = [-1*normal[0], -1*normal[1]]
        else:
            if x>1:
                #in wake
                if normal[1] < 0:
                    normal = [-1*normal[0], -1*normal[1]]
            else:
                #in lower
                if normal[1] > 0:
                    normal = [-1*normal[0], -1*normal[1]]

        if i < xmin_index+3 and i > xmin_index-3:
            # leading edge points need to point to left, but sometimes there are issues
            if normal[0] > 0:
                normal = [-1*normal[0], -1*normal[1]]

        normals.append(normal)

    return normals