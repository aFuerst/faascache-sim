#!/usr/bin/python3
from collections import defaultdict
import numpy as np
import multiprocessing as mp
import pickle
from collections import defaultdict
import os
from pprint import pprint
from math import floor
from datetime import datetime
from numpy.lib.function_base import kaiser
import pandas as pd

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

log_dir = "/data2/alfuerst/azure/functions/trace_runs_middle_200/logs/"


def get_info_from_file(filename):
    policy, num_funcs, mem, run, _ = filename[:-5].split("-")
    return policy.split("/")[-1], int(num_funcs), int(mem), run

def compute_mem_per_min(file):
    policy, num_funcs, mem_cap, run = get_info_from_file(file)
    try:
        # cols => time, used_mem, running_mem, pure_cache
        df = pd.read_csv(file, error_bad_lines=False, warn_bad_lines=False)
    except:
        print(file)
        raise

    sort = df.sort_values(by=["time"])
    dedup = sort.drop_duplicates(subset=["time"], keep="last")
    dedup.index = (dedup["time"] / 1000).apply(datetime.fromtimestamp)
    # upsample to second detail since there may be gaps
    # then downsample to minute buckets for
    dedup = dedup.resample("S").mean().interpolate().resample("1Min").interpolate()

    # print(dedup["used_mem"].mean())
    # print(dedup["pure_cache"].mean())
    # print(dedup["pure_cache"].mean() / dedup["used_mem"].mean())
    return mem_cap, dedup["pure_cache"].mean() / dedup["used_mem"].mean()


def compute_all():
    data = {"GD": []}  # , "TTL":[], "HIST":[]
    for file in os.listdir(log_dir):
        file = os.path.join(log_dir, file)
        policy, num_funcs, mem_cap, run = get_info_from_file(file)
        if os.path.isfile(file) and "b-purecachehist" in file and mem_cap < 6000:
            if "GD-200" in file:
                mem_cap, pure = compute_mem_per_min(file)
                data["GD"].append((mem_cap, pure))
            # elif "HIST-200" in file:
            #     mem_cap, pure = compute_mem_per_min(file)
            #     data["HIST"].append((mem_cap, pure))
            # elif "TTL-200" in file:
            #     mem_cap, pure = compute_mem_per_min(file)
            #     data["TTL"].append((mem_cap, pure))
            else:
                pass

    fig, ax = plt.subplots()
    plt.tight_layout()
    fig.set_size_inches(5,3)
    ax.set_ylabel("Pure Cache %")
    ax.set_xlabel("Memory (MB)")
    ax.set_title("200-b trace")
    for k, v in data.items():
        v = sorted(v, key= lambda x: x[0])
        ax.plot([x for x,y in v], [y*100 for x,y in v], label=k)
    # ax.plot([x for x,y in data["TTL"]], [y for x,y in data["TTL"]], label="TTL")
    # ax.plot([x for x, y in data["HIST"]], [y for x, y in data["HIST"]], label="HIST")

    fig.legend()
    save_path = "../figs/pure_cache/pure-cache-{}-b.png".format(200)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

def compute_one():
    for file in os.listdir(log_dir):
        if file == "GD-200-200-a-purecachehist.csv":
            pth = os.path.join(log_dir, file)
            compute_mem_per_min(pth)

if __name__ == "__main__":
    compute_all()