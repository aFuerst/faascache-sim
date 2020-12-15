#!/usr/bin/python3
from collections import defaultdict
import numpy as np
import multiprocessing as mp
import pickle
from collections import defaultdict
import os
from pprint import pprint

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

def plot_results(result_dict, save_path):
    fig, ax = plt.subplots()
    plt.tight_layout()
    fig.set_size_inches(5,3)

    for policy in result_dict.keys():
        pts = sorted(result_dict[policy], key=lambda x: x[0])
        xs = [x for x,y in pts]
        ys = [y*100 for x,y in pts]
        ax.plot(xs, ys, label=policy)

    ax.set_ylabel("% dropped invocations")
    ax.set_xlabel("Memory (MB)")
    ax.legend(loc="upper right")
    # print(save_path)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

data_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/analyzed"

def get_info_from_file(filename):
    if "LONG-TTL" in filename:
        num_funcs, mem, run = filename[:-5][9:].split("-")
        policy = "LONG-TTL"
    else:
        policy, num_funcs, mem, run = filename[:-5].split("-")
    return policy, int(num_funcs), int(mem), run

def load_data(path):
    with open(path, "r+b") as f:
        return pickle.load(f)

def plot_run(results_dict, num_funcs, fname):
    results_per_policy = defaultdict(list) # p -> [global-dicts]

    for mem in results_dict.keys():
        for policy in results_dict[mem].keys():
            tup = results_dict[mem][policy]
            capacity_misses, len_trace = tup

            count = sum([cnt for key, cnt in capacity_misses.items()])
            results_per_policy[policy].append((mem , count/len_trace))

    pth = "../figs/dropped_changes/droppped-{}-{}.pdf".format(fname, num_funcs)
    plot_results(results_per_policy, pth)

def plot_all():
    data = dict()

    for file in os.listdir(data_path):
        if "-392-" in file and "b" in file and "LONG-TTL" not in file:
            policy, num_funcs, mem, run = get_info_from_file(file)
            if mem <= 50000:
                # policy = string 
                # anal = results from analyze_timings
                # capacity_misses: dict[func_name] = invocations_not_handled
                # len_trace: long
                policy, analysis, capacity_misses, len_trace = load_data(os.path.join(data_path, file))
                if mem not in data:
                    data[mem] = dict()

                data[mem][policy] = (capacity_misses, len_trace)

    plot_run(data, 350, "drop-change")

if __name__ == "__main__":
    plot_all()