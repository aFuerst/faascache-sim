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
import argparse

data_path = "/data2/alfuerst/azure/functions/trace_runs_rep/analyzed/"
plot_dir = "../figs/increase_with_mem/"

def plot_results(result_dict, save_path):
    fig, ax = plt.subplots()
    plt.tight_layout()
    fig.set_size_inches(5,3)
    pols = ["GD", "TTL", "LRU", "HIST", "SIZE", "LND", "FREQ"]
    colors = ["black", "tab:green", "tab:red", "tab:orange", "tab:purple", "tab:brown", "c"]
    markers = ["o", "^", "1", "p", "*", "+", "x", "D", "h"]
    style = ["-", "--", ":"]
    for i, policy in enumerate(pols):
        pts = sorted(result_dict[policy], key=lambda x: x[0])
        xs = [x/1024 for x,y in pts]
        ys = [y*100 for x,y in pts]
        print(policy, colors[i])
        ax.plot(xs, ys, label=policy, linestyle=style[i%3], color=colors[i]) #, marker=markers[i]
    ax.set_ylabel("% Increase in Execution Time")
    ax.set_xlabel("Memory (GB)")

    ax.legend(bbox_to_anchor=(1.32,.5), loc="right", columnspacing=1)
    print(save_path)
    ax.set_ylim(0,None)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def average_dicts(dlist):
    n = len(dlist)
    outdict = dict()
    #Assume that the keys are the same for all the dictionaries. 
    #Simple dicts only, not nested or anything
    keys = dlist[0].keys()
    for k in keys:
        vals = np.mean([adict[k] for adict in dlist])
        outdict[k] = vals 
        
    return outdict

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

def plot_run(results_dict, num_funcs):
    results_per_policy = defaultdict(list) # p -> [global-dicts]

    for mem in results_dict.keys():
        # if mem <= 50000:
            for policy in results_dict[mem].keys():
                analysis = results_dict[mem][policy]
                results_per_policy[policy].append((mem , analysis["global"]["wted_increase"]))

    pth = os.path.join(plot_dir, "exec_inc_mem-{}.pdf".format(num_funcs))
    plot_results(results_per_policy, pth)

def plot_all(args):
    data = dict()
    funcs = args.numfuncs
    filt = "-{}-".format(funcs)
    for file in os.listdir(data_path):
        if filt in file and "b" in file and "LONG-TTL" not in file:
            policy, num_funcs, mem, run = get_info_from_file(file)
            if 10000 <= mem <= 80000:
                # policy: string
                # analysis: output from analyze_timings
                # capacity_misses: dict[func_name] = invocations_not_handled
                # len_trace: long
                # print(file)
                tup = load_data(os.path.join(data_path, file))
                # print(tup)
                if len(tup) == 3:
                    policy, analysis, capacity_misses = tup
                else:
                    policy, analysis, capacity_misses, len_trace = tup
                if mem not in data:
                    data[mem] = dict()

                data[mem][policy] = analysis

    plot_run(data, funcs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='plot FaasCache Simulation')
    parser.add_argument("--analyzeddir", type=str, default="/data2/alfuerst/verify-test/analyzed", required=False)
    parser.add_argument("--plotdir", type=str, default="../figs/increase_with_mem/", required=False)
    parser.add_argument("--numfuncs", type=int, default=392, required=False)
    args = parser.parse_args()
    data_path = args.analyzeddir
    plot_dir = args.plotdir
    plot_all(args)
