# #!/usr/bin/env python

from mpi4py import MPI 
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import os
import sys
inputFolder = int(sys.argv[1])

import natsort
combined = os.listdir(inputFolder)
files   = natsort.natsorted([f for f in combined if os.path.isfile(self.workingDirectory + os.sep + f)], alg=natsort.ns.IGNORECASE)
folders = natsort.natsorted([f for f in combined if not os.path.isfile(self.workingDirectory + os.sep + f)], alg=natsort.ns.IGNORECASE)

sortedFiles = []
for fl in files:
    if fl != '.DS_Store':
        sortedFiles.append(fl)

import json

for i, fl in enumerate(sortedFiles):
    if i % size == rank:
        # do something
        pass





if rank==0:
    # collect things
    pass




# import multiprocessing
# pool = multiprocessing.Pool()  
# result = pool.map(soFitnessFunction, ipList)
# pool.close()