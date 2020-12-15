import os,sys
import pickle
import math
import numpy as np
import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF 
# This needs scipy==1.2.0 

# pckls will have edcf for the given trace
ecdf_path = "/extra/alfuerst/azure/functions/trace_pckl/rare_large/ecdfs/"
two_hour_ecdf_path = "/extra/alfuerst/azure/functions/trace_pckl/represent_two_hour/ecdfs/"

def get_info_from_file(path):
    num_funcs, run, *_ = path.split("/")[-1][:-5].split("-")
    return int(num_funcs), run

def plot_cdf(path):
    with open(path, "r+b") as f:
        ecdf = pickle.load(f)

    num_funcs, run = get_info_from_file(path)
    fig, ax1 = plt.subplots()

    ax1.plot(ecdf.x, ecdf.y)
    ax1.set_xlabel("Cache Size (MB)")
    ax1.set_ylabel("Hit Ratio")
    ax1.set_xscale('log')
    if "two_hour" in path:
        save_path = "../figs/ecdfs/{}-{}-two_hour.pdf".format(num_funcs, run)
    else:
        save_path = "../figs/ecdfs/qt-{}-{}.pdf".format(num_funcs, run)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

def plot_all():
    import multiprocessing as mp
    with mp.Pool() as pool:
        paths = [os.path.join(ecdf_path, file) for file in os.listdir(ecdf_path) if os.path.isfile(os.path.join(ecdf_path, file))]
        print("computing {} files".format(len(paths)))
        pool.map(plot_cdf, paths)

        # paths = [os.path.join(two_hour_ecdf_path, file) for file in os.listdir(two_hour_ecdf_path) if os.path.isfile(os.path.join(two_hour_ecdf_path, file))]
        # print("computing {} files".format(len(paths)))
        # pool.map(plot_cdf, paths)

if __name__ == "__main__":
    plot_all()
    # print(plot_cdf("/extra/alfuerst/azure/functions/trace_pckl/represent/ecdfs/392-b-ecdf.pckl"))