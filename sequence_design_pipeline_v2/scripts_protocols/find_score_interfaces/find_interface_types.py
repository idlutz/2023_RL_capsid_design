#!/usr/bin/env python

import sys
from math import cos,sin,tan,asin,acos,radians,sqrt,degrees,atan,atan2,copysign,pi,exp
from math import pi as mPI
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import os
import glob
import seaborn as sns
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
import itertools
import operator
from functools import reduce
import pickle
from sklearn.cluster import KMeans
import scipy
from scipy import signal as scipysignal
from sklearn.cluster import DBSCAN
from scipy.stats import norm
import random
import statistics
import time
import timeit
from mpl_toolkits.mplot3d import Axes3D
import math
import gzip
import npose_util as nu
import subprocess
import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# Dirs and paths
b_paths = glob.glob('../../test/cage_design/1st_DM/*/*pdb') #### change this dir
outdir = '../../test/cage_design/1st_DM_chA_all/interfaces/' #### change this dir for output
zero_ih = nu.npose_from_file('zero_ih.pdb')

chain_ops = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W', \
             'X','Y','Z','0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j', \
             'k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def find_neighs(subunits, ind):
    subunit_dists = {}
    chains = 60
    for i in range(chains):
        subunit_dists[i] = np.linalg.norm(np.mean(subunits[ind],0)[:3] - np.mean(subunits[i],0)[:3])
        
    n_neighs = [x[0] for x in sorted(subunit_dists.items(), key = lambda kv: kv[1])[1:6]]
    
    interfaces = []
    temp_done = []
    for ni in n_neighs:
        for n2i in n_neighs:
            if ni != n2i and ni < n2i:
                if abs(subunit_dists[ni] - subunit_dists[n2i]) < 0.001:
                    interfaces.append((ni,n2i))
                    temp_done.append(ni)
                    temp_done.append(n2i)
                    
    for ni in n_neighs:
        if ni not in temp_done:
            interfaces.append(ni)
            
    return interfaces

def find_interfaces(bd_path):
    
    npose = nu.npose_from_file(bd_path)
    bd = npose[:int(len(npose)/60)]
    
    chains = 60
    slice_len = len(npose)/chains
    
    subunit_dists = {}
    subunits = []
    
    for i in range(chains):
        ch = npose[int(i*slice_len):int((i+1)*slice_len)]
        subunits.append(ch)
        subunit_dists[i] = np.linalg.norm(np.mean(bd,0)[:3] - np.mean(ch,0)[:3])
        
    n_neighs = [x[0] for x in sorted(subunit_dists.items(), key = lambda kv: kv[1])[1:6]]
    
    interfaces = []
    temp_done = []
    for ni in n_neighs:
        for n2i in n_neighs:
            if ni != n2i and ni < n2i:
                if abs(subunit_dists[ni] - subunit_dists[n2i]) < 0.001:
                    interfaces.append((ni,n2i))
                    temp_done.append(ni)
                    temp_done.append(n2i)
                    
    for ni in n_neighs:
        if ni not in temp_done:
            interfaces.append(ni)
     
    # rough but probably fine, only accept designs where 5 closest have (pair, pair, single)
    # one edge case is when dimer is too far away, so solo is pentamer instead -- fix further down
    if len(interfaces) != 3:
        return 0,0,0
    
    dimer_set = []
    trimer_done = False
    pentamer_edge_case = False
    for i in interfaces:
        
        if type(i) is tuple:
            new_neighs = find_neighs(subunits,i[0])
            
            # for edge case -- dimer is shared in pentamer's trimer and trimer's pentamer
            dimer_set += [new_neighs[0][0],new_neighs[0][1],new_neighs[1][0],new_neighs[1][1]]

            # check one of two interfaces, get the other -- is a trimer (except for pentamer edge case)
            if i[1] in [new_neighs[0][0],new_neighs[0][1],new_neighs[1][0],new_neighs[1][1]]:
                # if this happens twice, it's all pentamer
                if not trimer_done:
                    trimer = i[0]
                    trimer_done = True
                else:
                    pentamer_edge_case = True
            # check one of two interfaces, don't find other -- is a pentamer (and avoid edge case above)
            else:
                pentamer = i[0]
    
    dimer = None
    check_set = []
    for s in dimer_set:
        if s != 0:
            if s not in check_set:
                check_set.append(s)
            else:
                dimer = s
    
    if not dimer:
        dimer = interfaces[-1]
        
    # another edge case -- no trimer contacts, so only pentamer
    if pentamer_edge_case:
        n_neighs = [x[0] for x in sorted(subunit_dists.items(), key = lambda kv: kv[1])[6:9]]
        pentamer = trimer
        trimer = n_neighs[0]
        dimer = interfaces[-1]
    
    return chain_ops[dimer], chain_ops[trimer], chain_ops[pentamer]
    

b_paths = glob.glob('../../test/cage_design/1st_DM/*/*pdb') #### change this dir

for ind,i in enumerate(b_paths):
    d,t,p = find_interfaces(i)
    chA = []
    chDimer = []
    chTrimer = []
    chPentamer = []

    with open(i,'r') as file:
        for lnd,line in enumerate(file):
            if len(line.split()) > 8:
                if line.split()[0] == 'ATOM':
                    if line.split()[4] == 'A':
                        chA.append(line)
                    if line.split()[4] == d:
                        chDimer.append(line)
                    if line.split()[4] == t:
                        chTrimer.append(line)
                    if line.split()[4] == p:
                        chPentamer.append(line)
    
    name = i.split('/')[-1][:-4]
    with open(outdir+name+'_dimer.pdb','w') as file:
        for line in chA:
            file.write(line)
        for line in chDimer:
            file.write(line)
    with open(outdir+name+'_trimer.pdb','w') as file:
        for line in chA:
            file.write(line)
        for line in chTrimer:
            file.write(line)
    with open(outdir+name+'_pentamer.pdb','w') as file:
        for line in chA:
            file.write(line)
        for line in chPentamer:
            file.write(line)

print(len(b_paths)*3)
print(len(glob.glob('../../test/cage_design/1st_DM_chA_all/interfaces/*.pdb')))


