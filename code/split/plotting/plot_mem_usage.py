#!/usr/bin/python3
from collections import defaultdict
import numpy as np
import multiprocessing as mp
import pickle
from collections import defaultdict
import os
from pprint import pprint
from math import floor
import sys

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

memory_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/memory"

def get_info_from_file(filename):
    policy, num_funcs, mem, run = filename[:-5].split("-")
    return policy, int(num_funcs), int(mem), run

def plot_run(data_dict, memory, num_funcs):
    colors = ["tab:blue", "tab:green", "tab:orange", "tab:purple", "tab:brown", "tab:pink", "tab:gray"]
    fig, ax = plt.subplots()
    plt.tight_layout()
    fig.set_size_inches(5,3)
    ax.set_ylabel("Memory usage")

    for i, policy in enumerate(sorted(data_dict.keys())):
        avg_mem = np.zeros(60*24, dtype=np.float64)
        for arr in data_dict[policy]:
            avg_mem += arr

        avg_mem = avg_mem / len(data_dict[policy])
        ax.plot([i for i in range(60*24)], avg_mem, label=policy, color=colors[i])

    ax.axhline(y=memory, color="red")
    fig.legend()
    save_path = "../figs/mem_usage/mem-usage-{}-{}.pdf".format(memory, num_funcs)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    # print(save_path)

def plot_all():
    data = dict()
    funcs = 392
    filt = "-{}-".format(funcs)
    for file in os.listdir(memory_path):
        if filt in file and "b" in file:
            policy, num_funcs, mem, run = get_info_from_file(file)
            # saved as numpy array in one minute buckets of average memory usage across the minute
            array = np.load(os.path.join(memory_path, file))
            if mem not in data:
                data[mem] = dict()

            if num_funcs not in data[mem]:
                data[mem][num_funcs] = dict()

            if policy not in data[mem][num_funcs]:
                data[mem][num_funcs][policy] = list()

            data[mem][num_funcs][policy].append(array)

    for mem_alloc in data.keys():
        for num_funcs in data[mem_alloc].keys():
                plot_run(data[mem_alloc][num_funcs], mem_alloc, num_funcs)

if __name__ == "__main__":
    plot_all()