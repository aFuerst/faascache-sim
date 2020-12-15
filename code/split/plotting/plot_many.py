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

def plot_results(result_dict, averaged_misses_dict, save_path):
    contenders = list(result_dict.keys())
    contenders = sorted(contenders)
    contenders.remove("GD")
    contenders.insert(0, "GD")

    wted_increases = [result_dict[k]["wted_increase"]*100
                      for k in contenders]
        
    wted_eat = [result_dict[k]["wted_eat"]
                      for k in contenders]

    server_cold = [result_dict[k]["server_cold"]
                      for k in contenders]
    
    misses = [averaged_misses_dict[k] * 100
                      for k in contenders]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    plt.tight_layout()
    fig.set_size_inches(5,3)
    ax1.bar(contenders, wted_increases, width=0.5)
    ax1.set_ylabel("% Increase in Execution Time")

    ax2.set_ylabel("% Requests Dropped")
    ax2.plot(contenders, misses, "ro")
    ax2.set_ylim([0,None])

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

def plot_run(results_dict, mem_alloc, num_funcs):
    results_per_policy = defaultdict(list) # p -> [global-dicts]
    misses_per_policy = defaultdict(list) # p -> [global-dicts]
    averaged_result_dict = dict()
    averaged_misses_dict = dict()
    for run in results_dict.keys():
        for tup in results_dict[run]:
            policy, anal, capacity_misses, len_trace = tup
            results_per_policy[policy].append(anal["global"])
            cap_misses_sum = sum([cnt for key, cnt in capacity_misses.items()])
            misses_per_policy[policy].append(cap_misses_sum / len_trace) # the % of invocations that weren't fulfilled

    for policy in results_per_policy.keys():
        averaged_result_dict[policy] = average_dicts(results_per_policy[policy])
        averaged_misses_dict[policy] = sum(misses_per_policy[policy]) / len(misses_per_policy[policy])

    save_path = "../figs/exec_increase/exec_increase-{}-{}.pdf".format(mem_alloc, num_funcs)
    plot_results(averaged_result_dict, averaged_misses_dict, save_path)

def plot_all():
    data = dict()
    funcs = 392
    filt = "-{}-".format(funcs)
    for file in os.listdir(data_path):
        pth = os.path.join(data_path, file)
        if os.path.isfile(pth) and filt in file and "b" in file and "-200-" not in file and "LONG-TTL" not in file: 
            policy, num_funcs, mem, run = get_info_from_file(file)
            # if policy == "HIST":
            #     continue
            tup = load_data(pth)
            # policy: str
            # output from analyze_timings
            # capacity_misses: dict[func_name] = invocations_not_handled
            # len_trace: long
            if mem not in data:
                data[mem] = dict()

            if run not in data[mem]:
                data[mem][run] = list()

            data[mem][run].append(tup)

    for mem_alloc in data.keys():
        plot_run(data[mem_alloc], mem_alloc, funcs)

if __name__ == "__main__":
    plot_all()