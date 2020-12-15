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
import pandas as pd

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse

# data_path = "/data2/alfuerst/azure/functions/trace_runs_updated"
memory_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/memory"
log_dir = "/data2/alfuerst/azure/functions/trace_runs_rep_392/logs/"

def get_info_from_file(filename):
    policy, num_funcs, mem, run, _ = filename[:-5].split("-")
    return policy, int(num_funcs), int(mem), run

def load_data(path):
    with open(path, "r+b") as f:
        return pickle.load(f)

def compute_mem_per_min(file, ret=False):
    pth = os.path.join(log_dir, file)
    policy, num_funcs, mem_cap, run = get_info_from_file(file)
    fname = "{}-{}-{}-{}-".format(policy, num_funcs, mem_cap, run)
    memUsageFname = os.path.join(log_dir, file)

    try:
        df = pd.read_csv(memUsageFname, error_bad_lines=False, warn_bad_lines=False)
    except:
        print(file)
        raise
    start = {"time":0, "reason":"fix","mem_used":df.at[0, "mem_used"], "mem_size":0, "extra":"N/A"}
    end = {"time": 24 * 59 * 60 * 1000, "reason": "fix", "mem_used": df.at[len(df)-1, "mem_used"], "mem_size": 0, "extra": "N/A"}
    # print(start)
    # print(end)
    df2 = pd.DataFrame([start, end], columns=df.columns)
    df = df.append(df2)

    sort = df.sort_values(by=["time", "mem_used"])
    dedup = sort.drop_duplicates(subset=["time"], keep="last")
    dedup.index = (dedup["time"] / 1000).apply(datetime.fromtimestamp)
    # upsample to second detail since there may be gaps
    # then downsample to minute buckets for 
    dedup = dedup.resample("S").mean().interpolate().resample("1Min").interpolate()

    save_path = "{}-{}-{}-{}.npy".format(policy, num_funcs, mem_cap, run)
    save_path = os.path.join(memory_path, save_path)
    d = dedup["mem_used"].to_numpy(copy=True)
    if len(d) != 1440:
        d.resize(1440)
    # saved as numpy array in one minute buckets of average memory usage across the minute
    np.save(save_path, d)

def compute_all():
    with mp.Pool() as pool:
        files = [file for file in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, file)) and "memusagehist" in file]
        print("computing {} files".format(len(files)))
        pool.map(compute_mem_per_min, files)


def compute_one():
    data = np.zeros(60*24)
    events = 0
    cnt = 0
    for file in os.listdir(log_dir):
        if "TTL-1000-4096-" in file:
            cnt += 1
            pth = os.path.join(log_dir, file)
            data += compute_mem_per_min(pth, ret=True)

    data = data / cnt
    print(cnt)
    print(data)
    print(data.mean())

if __name__ == "__main__":
    # pth = "TTL-392-16000-b-memusagehist.csv"
    # compute_mem_per_min(pth)
    # compute average memory usage per-minute of each run

    parser = argparse.ArgumentParser(description='analyze FaasCache Simulation')
    parser.add_argument("--savedir", type=str, default="/data2/alfuerst/verify-test/memory/", required=False)
    parser.add_argument("--logdir", type=str, default="/data2/alfuerst/verify-test/logs/", required=False)
    args = parser.parse_args()
    log_dir= args.logdir
    memory_path = args.logdir
    compute_all()