# from ada.analysis.apis.xfoil.forcePlot import computeNormals
# from ada.analysis.apis import xfoil

# def stressPlot(data):

# from ada.analysis.apis.xfoil.forcePlot import computeNormals, forcePlot
# from ada.analysis.apis.xfoil.standardPlot import standardPlot
# from ada.analysis.apis import xfoil

# import numpy as np 

# import matplotlib.pyplot as plt
# %matplotlib inline

# def stressPlot(data):

#     fig = plt.figure(figsize=(10,8), dpi=300)

#     xdata = data['bl_data']['x']
#     ydata = data['bl_data']['y']

#     wake_index = next(x[0] for x in enumerate(xdata) if x[1] > 1.0)
#     stagnation_index = data['cp_data']['cp'].index(max(data['cp_data']['cp']))
#     xmin_index = data['bl_data']['x'].index(min(data['bl_data']['x']))

#     xdata = xdata[0:wake_index]
#     ydata = ydata[0:wake_index]
    
#     afl = Kulfan()
#     afl.fit2coordinates(np.array(xdata), np.array(ydata), fit_order=8, atol = 1e-6)
#     hts = afl.getNormalizedHeight()

#     # normals = computeNormals(data)
#     upperNormals = afl.upperNormals
#     lowerNormals = afl.lowerNormals
    
#     cp_top = list(reversed(data['cp_data']['cp'][0:xmin_index+1]))
#     cp_bot = data['cp_data']['cp'][xmin_index:]
#     psis = afl.psi
#     zetaUpper = afl.zetaUpper
#     zetaLower = afl.zetaLower

#     # hasBlue = False
#     # hasRed = False
#     # shear_mat = np.zeros([len(normals),3])
#     # for i,nm in enumerate(normals[0:xmin_index]):
#     fy_arr = [0.0]
#     Vy_arr = [0.0]
#     M_arr  = [0.0]
#     for i,psi in enumerate(psis):
#         if i > 0:
#             x = psi
#             local_cp_top = -1.0*np.interp(x, list(reversed(xdata[0:xmin_index+1])), cp_top)
#             local_cp_bot = -1.0*np.interp(x, xdata[xmin_index:], cp_bot)
#             dx = x-psis[i-1]
            
#             fy = local_cp_top*dx - local_cp_bot*dx
#             fy_arr.append(fy)

#     fy_arr = np.array(fy_arr)
#     # fy_net = sum(fy_arr)
            
#     for i,psi in enumerate(psis):
#         if i > 0:
#             x = psi
#             dx = x-psis[i-1]
#             if x>= 0.25:
#                 shft = -1.0*sum(fy_arr)
#             else:
#                 shft = 0.0
#             Vy_arr.append(sum(fy_arr[0:i])+shft)
        
#     Vy_arr = np.array(Vy_arr)
    
#     for i,psi in enumerate(psis):
#         if i > 0:
#             x = psi
#             dx = x-psis[i-1]
#             if x>= 0.25:
#                 shft = -1.0*sum(Vy_arr)
#             else:
#                 shft = 0.0
#             M_arr.append(sum(Vy_arr[0:i])+shft)
        
#     M_arr = np.array(M_arr)
    
#     # if 0.25 in psis:
#     #     fy_arr[psis.index(0.25)] -= fy_net
#     # else:
#     #     ix = next(x[0] for x in enumerate(psis) if x[1] > 0.25)
#     #     psis   = np.append(psis[0:ix], np.append(0.25 , psis[ix:] ))
#     #     fy_arr = np.append(fy_arr[0:ix], np.append(-1.0*fy_net , fy_arr[ix:] ))
#     # print(psis)
        
    
            
#     # plt.plot(psis, fy_arr)
#     # plt.plot(psis, Vy_arr)
#     # plt.plot(psis, M_arr)
#     plt.plot(psis, M_arr/hts**2)
#     plt.grid(1)
        
# #         # dx = 
# #         # Vy = -1.0*nm[1]*sc *1/2 rho V**2 *dA_surf
        
# #         fy = -1.0*nm[1]*sc 
# #         Vy = fy*x   #*1/2 rho V**2 *span   /   (span*height)   (so this is per unit span)
# #         M  = Vy*x   # same, is per unit span

# #         shear_mat[i,0] = x
# #         shear_mat[i,1] = Vy
# #         shear_mat[i,2] = M
        
# #     shear_mat_sorted_idx = np.argsort(shear_mat[:,0])
# #     shear_mat_sorted = shear_mat[shear_mat_sorted_idx]
# #     shear_mat_sorted = np.append(shear_mat_sorted, [[0.25, -1*sum(shear_mat_sorted[:,1]), -1*sum(shear_mat_sorted[:,2])]],axis=0)
# #     shear_mat_sorted_idx = np.argsort(shear_mat_sorted[:,0])
# #     shear_mat_sorted = shear_mat_sorted[shear_mat_sorted_idx]
    
# #     running_shear = 0.0
# #     running_moment = 0.0
# #     rs_arr = [0.0]
# #     rm_arr = [0.0]
# #     for i in range(0,len(shear_mat_sorted)):
# #         running_shear += shear_mat_sorted[i,1]
# #         rs_arr.append(running_shear)
        
# #         running_moment += shear_mat_sorted[i,2] 
# #         rm_arr.append(running_moment)
        
        
# #     # afl = Kulfan()
# #     # afl.fit2coordinates(np.array(xdata), np.array(ydata), fit_order=8, atol = 1e-6)
# #     # hts = afl.getNormalizedHeight(shear_mat_sorted[:,0])

# #     plt.plot(np.append(0,shear_mat_sorted[:,0]),rs_arr)
# #     plt.plot(np.append(0,shear_mat_sorted[:,0]),rm_arr) 
# #     plt.plot(shear_mat_sorted[:,0],rm_arr[1:]/hts**2 /20)

# #     plt.grid(1)


# if __name__ == "__main__":
#     from ada.geometry.airfoils.kulfan import Kulfan

#     afl = Kulfan()
#     afl.naca4_like(4,7,8)
#     # afl.naca4_like(2,4,12)
#     # afl.constants.TE_gap = 0.01
#     # plt.plot(afl.xcoordinates, afl.ycoordinates)
#     # plt.axis('equal')

#     data = xfoil.runSingleCase('alpha', 
#           afl,
#           val = 0.0, 
#           Re = 1e7,
#           M = 0.0,
#           xtr_u=1.0,
#           xtr_l=1.0,
#           N_crit=9.0,
#           N_panels = 290)

#     stressPlot(data)
#     standardPlot(data)


# if __name__ == "__main__":
#     from ada.geometry.airfoils.kulfan import Kulfan

#     afl = Kulfan()
#     afl.naca4_like(2,4,12)


#     data = xfoil.runSingleCase('alpha', 
#           afl,
#           val = 0.0, 
#           Re = 1e7,
#           M = 0.0,
#           xtr_u=1.0,
#           xtr_l=1.0,
#           N_crit=9.0)

#     stressPlot(data)


