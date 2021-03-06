import globals as gb
from app import App
from Visualize import Visualize
from SignalReader import SignalReader
from SignalReaderArtificial import SignalReaderArtificial
from Clustering import Clustering
#from ArtificialDataOriginal import ArtificialData
from ArtificialData import ArtificialData
import itertools
import os
import math
import random
import datetime
import time
import warnings
import numpy as np
import matplotlib.pyplot as plt2

# =================================================================
if __name__ == '__main__':
    warnings.simplefilter(action = "ignore", category = FutureWarning)
    random.seed(1234)
    viz = Visualize()

    # -----------------------------
    # agg = 0 # Always calm
    # agg = 1 # Always aggressive
    agg = None # Mix of calm periods and aggressive periods

    # Ks = [3, 6, 8, 10] # Clusters
    # Ds = [5, 10, 15, 30, 60, 90, 120] # Duration window
    Ks = [3] # Clusters
    Ds = [5]
    # Ds = [.5, 1, 5, 15, 60] # Duration window
    Ps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.] # Patterns similarity (difficulty)
    Ns = [3.] # Noise level
    MODE_NAMES = ["b","g", "r"]

    variable = "P"

    if variable=="P": combos, params, combo_name = list(itertools.product(Ks, Ds, Ns)), Ps, ("K", "D", "N")
    if variable=="D": combos, params, combo_name = list(itertools.product(Ks, Ps, Ns)), Ds, ("K", "P", "N")
    if variable=="N": combos, params, combo_name = list(itertools.product(Ks, Ds, Ps)), Ns, ("K", "D", "P")
    if variable=="K": combos, params, combo_name = list(itertools.product(Ds, Ps, Ns)), Ks, ("D", "P", "N")

    # -----------------------------
    for comb in combos:
        if variable=="P": (K, D, N) = comb
        if variable=="D": (K, P, N) = comb
        if variable=="N": (K, D, P) = comb
        if variable=="K": (D, P, N) = comb

        vals = []
        FSP_ari = []; SSP_ari = []; FSP_ami = []; SSP_ami = []; FSP_ho = []; SSP_ho = []; FSP_com = []; SSP_com = []; FSP_vm = []; SSP_vm = []

        for param in params:
            if variable=="P": P = param
            if variable=="D": D = param
            if variable=="N": N = param
            if variable=="K": K = param

            id_combin = "-".join([ str(vn)+str(v) for v,vn in list(zip(comb, combo_name)) ]) + "-Agg"+str(agg)
            vals.append(param)
            gb.K = K

            signalsValues, modes = ArtificialData(noise=N, ptrn=P).run()#parts=30) # VS, ES, APP, BPP, ECT
            sigReaders = [ SignalReaderArtificial(signame="Signal"+str(i), sigvalues=values, modes=modes) for i,values in enumerate(signalsValues) ]
            app = App(sigReaders)

            DATA, AXES_INFO = app.build_features_data()
            clust = Clustering(DATA, scale=True, features=None).gmm(k = 3)#k=gb.K) # kmeans, dpgmm, gmm
            app.init_clust_tracker(clust, AXES_INFO)

            PLOT_PATH = gb.PLOT_PATH + str(id_combin) + '/' + str(param) + '/'
            if not os.path.exists(PLOT_PATH): os.makedirs(PLOT_PATH)
            path = PLOT_PATH+str(id_combin)+'_'
            app.logInformations( id_combin=id_combin, clust=clust, path=path )

            #(ari_fps, ari_sps), (ami_fps, ami_sps), (ho_fps, ho_sps), (com_fps, com_sps), (vm_fps, vm_sps) = app.tracking(path=path)
            STATS, RESULTS = app.tracking(path=gb.PLOT_PATH, )
            times_fsp, axes_fsp,labels_fsp,times_ssp,axes_ssp,labels_ssp = RESULTS
            (ari_fps, ari_sps), (ami_fps, ami_sps), (ho_fps, ho_sps), (com_fps, com_sps), (vm_fps, vm_sps) = STATS
            FSP_ari.append(ari_fps); SSP_ari.append(ari_sps)
            FSP_ami.append(ami_fps); SSP_ami.append(ami_sps)
            FSP_ho.append(ho_fps); SSP_ho.append(ho_sps)
            FSP_com.append(com_fps); SSP_com.append(com_sps)
            FSP_vm.append(vm_fps); SSP_vm.append(vm_sps)

            #plotting
            plt2.clf()
            sss=5000
            TIME = range(len(signalsValues[0]))
            #umode = set(modes)
            cl=[MODE_NAMES[xx] for xx in modes]
            start_plt = sss
            end_plt = 3*sss
            plt2.scatter(TIME[start_plt:end_plt],signalsValues[0][start_plt:end_plt], color = cl[start_plt:end_plt])
            cl_fsp = [MODE_NAMES[xx] for xx in labels_fsp]
            plt2.scatter(TIME[start_plt:end_plt],[130]*len(TIME[start_plt:end_plt]),color=cl_fsp[start_plt:end_plt],marker="|",s=20)
            plt2.text(start_plt,120,"clustering")
            cl_ssp = [MODE_NAMES[xx] for xx in labels_ssp]
            plt2.scatter(TIME[start_plt:end_plt],[110]*len(TIME[start_plt:end_plt]),color=cl_ssp[start_plt:end_plt],marker="|",s=20)
            plt2.text(start_plt,100,"tracking")
            fname = "plots/rs"+ str(id_combin) + ".png"
            plt2.savefig(fname)
            plt2.close()

        viz.do_plot( [vals, FSP_ari], axs_labels=['Parameter '+variable, 'Adjusted Random Index'], marker="-", color="red", label="FSP_ari" )
        viz.do_plot( [vals, SSP_ari], axs_labels=['Parameter '+variable, 'Adjusted Random Index'], marker="-", color="blue", label="SSP_ari" )
        viz.end_plot( fig=gb.PLOT_PATH+"/ARI_"+str(id_combin)+"---"+str(time.time())+".png" )

        viz.do_plot( [vals, FSP_ami], axs_labels=['Parameter '+variable, 'Adjusted Mutual Information'], marker="-", color="red", label="FSP_ami" )
        viz.do_plot( [vals, SSP_ami], axs_labels=['Parameter '+variable, 'Adjusted Mutual Information'], marker="-", color="blue", label="SSP_ami" )
        viz.end_plot( fig=gb.PLOT_PATH+"/AMI_"+str(id_combin)+"---"+str(time.time())+".png" )

        viz.do_plot( [vals, FSP_ho], axs_labels=['Parameter '+variable, 'Homogeneity'], marker="-", color="red", label="FSP_ho" )
        viz.do_plot( [vals, SSP_ho], axs_labels=['Parameter '+variable, 'Homogeneity'], marker="-", color="blue", label="SSP_ho" )
        viz.end_plot( fig=gb.PLOT_PATH+"/HO_"+str(id_combin)+"---"+str(time.time())+".png" )

        viz.do_plot( [vals, FSP_com], axs_labels=['Parameter '+variable, 'Completeness'], marker="-", color="red", label="FSP_com" )
        viz.do_plot( [vals, SSP_com], axs_labels=['Parameter '+variable, 'Completeness'], marker="-", color="blue", label="SSP_com" )
        viz.end_plot( fig=gb.PLOT_PATH+"/COM_"+str(id_combin)+"---"+str(time.time())+".png" )

        viz.do_plot( [vals, FSP_vm], axs_labels=['Parameter '+variable, 'V_measure'], marker="-", color="red", label="FSP_vm" )
        viz.do_plot( [vals, SSP_vm], axs_labels=['Parameter '+variable, 'V_measure'], marker="-", color="blue", label="SSP_vm" )
        viz.end_plot( fig=gb.PLOT_PATH+"/VM_"+str(id_combin)+"---"+str(time.time())+".png" )

    # -----------------------------
    map(lambda sr: sr.closeDB(), sigReaders)
    print("FINISH.")
    input()

