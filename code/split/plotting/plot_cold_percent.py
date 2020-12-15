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
    contenders = list(result_dict.keys())
    contenders = sorted(contenders)
    contenders.remove("GD")
    contenders.insert(0, "GD")

    miss_percent = [result_dict[k]*100 for k in contenders]

    fig, ax1 = plt.subplots()

    plt.tight_layout()
    fig.set_size_inches(5,3)
    ax1.bar(contenders, miss_percent, width=0.5)
    ax1.set_ylabel("% Cold Starts")

    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

data_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/analyzed/"

def get_info_from_file(filename):
    policy, num_funcs, mem, run = filename[:-5].split("-")
    return policy, int(num_funcs), int(mem), run

def load_data(path):
    with open(path, "r+b") as f:
        return pickle.load(f)

def plot_run(results_dict, mem_alloc, num_funcs):
    accesses_per_policy = defaultdict(int) # p -> [global-dicts]
    misses_per_policy = defaultdict(int) # p -> [global-dicts]
    averaged_result_dict = dict()

    for run in results_dict.keys():
        for tup in results_dict[run]:
            policy, anal, capacity_misses, len_trace = tup
            # pprint(anal)
            for func in anal.keys():
                if func != "global":
                    accesses_per_policy[policy] += anal[func]["accesses"]
                    misses_per_policy[policy] += anal[func]["misses"]

    for policy in accesses_per_policy.keys():
        averaged_result_dict[policy] = misses_per_policy[policy] / accesses_per_policy[policy]

    save_path = "../figs/cold_precent/cold_percent-{}-{}.pdf".format(mem_alloc, num_funcs)
    plot_results(averaged_result_dict, save_path)

def plot_all():
    data = dict()

    num = 392
    filt = "-{}-".format(num)
    for file in os.listdir(data_path):
        pth = os.path.join(data_path, file)
        if os.path.isfile(pth) and filt in file and "b" in file: 
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
        plot_run(data[mem_alloc], mem_alloc, num)

if __name__ == "__main__":
    plot_all()