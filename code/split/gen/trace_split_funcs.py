import os
import pandas as pd
from multiprocessing import Pool
from LambdaData import *
import pickle
from math import ceil

store = "/data2/alfuerst/azure/functions/trace_pckl/"
buckets = [str(i) for i in range(1, 1441)]

datapath = "/data2/alfuerst/azure/functions/"
durations = "function_durations_percentiles.anon.d01.csv"
invocations = "invocations_per_function_md.anon.d01.csv"
mem_fnames = "app_memory_percentiles.anon.d01.csv"

def trace_row(data):
    index, row = data
    secs_p_min = 60
    milis_p_sec = 1000
    trace = list()
    lambdas = dict()
    cold_dur = int(row["Maximum"])
    warm_dur = int(row["Average"])
    mem = int(row["divvied"])
    k = index
    d = LambdaData(k, mem, cold_dur, warm_dur)
    lambdas[k] = (k, mem, cold_dur, warm_dur)
    for minute, invocs in enumerate(row[buckets]):
        start = minute * secs_p_min * milis_p_sec
        if invocs == 0:
            continue
        elif invocs == 1:
            trace.append((d, start))
        else:
            every = (secs_p_min*milis_p_sec) / invocs
            trace += [(d, start + i*every) for i in range(invocs)]
    # print(trace)
    out_trace = sorted(trace, key=lambda x:x[1]) #(lamdata, t)

    out_pth = os.path.join(store, index+".pckl")
    # files are traces themselves. Just need to combine them together
    # format: (lambdas, trace) => 
    # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
    # trace = [LambdaData(func_name, mem, cold_time, warm_time), start_time]
    with open(out_pth, "w+b") as f:
        pickle.dump((lambdas, out_trace), f)
    # return lambdas, out_trace

def divive_by_func_num(row):
    return ceil(row["AverageAllocatedMb"] / group_by_app[row["HashApp"]])

file = os.path.join(datapath, durations.format(1))
durations = pd.read_csv(file)
durations.index = durations["HashFunction"]
durations = durations.drop_duplicates("HashFunction")

group_by_app = durations.groupby("HashApp").size()

file = os.path.join(datapath, invocations.format(1))
invocations = pd.read_csv(file)
invocations = invocations.dropna()
invocations.index = invocations["HashFunction"]
sums = invocations.sum(axis=1)
invocations = invocations[sums > 1] # action must be invoked at least twice
invocations = invocations.drop_duplicates("HashFunction")

joined = invocations.join(durations, how="inner", lsuffix='', rsuffix='_durs')

file = os.path.join(datapath, mem_fnames.format(1))
memory = pd.read_csv(file)
memory = memory.drop_duplicates("HashApp")
memory.index = memory["HashApp"]

new_mem = memory.apply(divive_by_func_num, axis=1, raw=False, result_type='expand')
memory["divvied"] = new_mem

joined = joined.join(memory, how="inner", on="HashApp", lsuffix='', rsuffix='_mems')

with Pool() as p:
    p.map(trace_row, joined.iterrows())