#!/usr/bin/python3
import sys
sys.path.insert(1, '/home/alfuerst/repos/faas-keepalive-20/code/split/')
import numpy as np
import pickle
import os
from pprint import pprint
from math import floor
from collections import defaultdict
import multiprocessing as mp
import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

def get_info_from_file(filename):
    num_funcs, run = filename.split("/")[-1][:-5].split("-")
    return num_funcs, run

def plot_trace(pth):
    with open(pth, "r+b") as f:
        lambdas, trace = pickle.load(f)

    buckets = np.zeros(24*60)
    min_ms = 60*1000

    cnts = defaultdict(int)

    for d, t in trace:
        cnts[d.kind] += 1 
        buckets[floor(t / (min_ms))] += 1

    fig, ax1 = plt.subplots()
    fig.set_size_inches(5,3)
    ax1.plot(buckets)

    num_funcs, run = get_info_from_file(pth)
    if "two_hour" in pth:
        save = "../figs/trace_shape/{}-{}-two.pdf".format(num_funcs, run)
    else:
        save = "../figs/trace_shape/{}-{}.pdf".format(num_funcs, run)
    plt.savefig(save, bbox_inches="tight")


two = "/extra/alfuerst/azure/functions/trace_pckl/represent_two_hour/"
full = "/extra/alfuerst/azure/functions/trace_pckl/represent/"

plot_trace("/data2/alfuerst/azure/functions/trace_pckl/represent/{}-{}.pckl".format(392, "b"))

# two = [os.path.join(two, file) for file in os.listdir(two) if os.path.isfile(os.path.join(two, file))]
# full = [os.path.join(full, file) for file in os.listdir(full) if os.path.isfile(os.path.join(full, file))]

# with mp.Pool() as pool:
#     print("computing {} files".format(len(full)))
#     pool.map(plot_trace, full)

#     print("computing {} files".format(len(two)))
#     pool.map(plot_trace, two)
