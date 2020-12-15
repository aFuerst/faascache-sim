import os
import pandas as pd
import sys
sys.path.insert(1, '/home/alfuerst/repos/faas-keepalive-20/code/split/')
import numpy as np
import pickle
from math import ceil

save_dir = "/extra/alfuerst/azure/functions/trace_pckl/rare_large/"
store = "/extra/alfuerst/azure/functions/trace_pckl/"
buckets = [str(i) for i in range(1, 1441)]

datapath = "/extra/alfuerst/azure/functions/"
durations = "function_durations_percentiles.anon.d01.csv"
invocations = "invocations_per_function_md.anon.d01.csv"
mem_fnames = "app_memory_percentiles.anon.d01.csv"

quantiles = [0.0, 0.25, 0.5, 0.75, 1.0]

def gen_trace(rare_df, mem_df, num_funcs, run):
    lambdas = {}
    trace = []
    save_pth = "{}-{}.pckl".format(num_funcs, run)
    save_pth = os.path.join(save_dir, save_pth)

    per = num_funcs//2

    if not os.path.exists(save_pth):
        for df in [rare_df, mem_df]:
            samp = df.sample(per)
            for index, row in samp.iterrows():
                pckl = "{}.pckl".format(index)
                path = os.path.join(store, pckl)
                with open(path, "r+b") as f:
                    data = pickle.load(f)
                    one_lambda, one_trace = data
                    lambdas = {**lambdas, **one_lambda}
                    trace += one_trace
                    
        out_trace = sorted(trace, key=lambda x:x[1]) #(lamdata, t)
        print(num_funcs, len(out_trace))
        with open(save_pth, "w+b") as f:
            # format: (lambdas, trace) => 
            # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
            # trace = [LambdaData(func_name, mem, cold_time, warm_time), start_time]
            data = (lambdas, out_trace)
            pickle.dump(data, f)

    print("done", save_pth)

def gen_traces():
    global durations
    global invocations
    global memory

    def divive_by_func_num(row):
        return ceil(row["AverageAllocatedMb"] / group_by_app[row["HashApp"]])

    file = os.path.join(datapath, durations)
    durations = pd.read_csv(file)
    durations.index = durations["HashFunction"]
    durations = durations.drop_duplicates("HashFunction")

    group_by_app = durations.groupby("HashApp").size()

    file = os.path.join(datapath, invocations)
    invocations = pd.read_csv(file)
    invocations = invocations.dropna()
    invocations.index = invocations["HashFunction"]
    sums = invocations.sum(axis=1)

    invocations = invocations[sums > 1] # action must be invoked at least twice
    invocations = invocations.drop_duplicates("HashFunction")
    # sums = invocations.sum(axis=1)
    # print(sums.quantile(quantiles))

    joined = invocations.join(durations, how="inner", lsuffix='', rsuffix='_durs')

    file = os.path.join(datapath, mem_fnames.format(1))
    memory = pd.read_csv(file)
    memory = memory.drop_duplicates("HashApp")
    memory.index = memory["HashApp"]

    new_mem = memory.apply(divive_by_func_num, axis=1, raw=False, result_type='expand')
    memory["divvied"] = new_mem

    joined = joined.join(memory, how="inner", on="HashApp", lsuffix='', rsuffix='_mems')

    sums = joined.sum(axis=1)
    sums_qts = sums.quantile(quantiles)

    bottom_qt = joined[sums < sums_qts.iloc[1]]

    mem_qts = joined["divvied"].quantile(quantiles)
    mem_df = joined[sums >= mem_qts.iloc[3]]

    # print(bottom_qt.describe())
    # print(mem_df.describe())
    # exit()
    for size in range(200, 500, 50):
        for run in ["a"]:
            gen_trace(joined, bottom_qt, size, run)

gen_traces()