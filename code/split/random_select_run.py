#!/usr/bin/python3
from collections import defaultdict
import multiprocessing as mp
from TraceGen import *
from LambdaScheduler import LambdaScheduler
import pickle
import numpy as np

def load_trace(num_functions, char):
    pth = "/data2/alfuerst/azure/functions/trace_pckl/precombined/{}-{}.pckl".format(num_functions, char)
    with open(pth, "r+b") as f:
        return pickle.load(f)

def compare_pols(policy, num_functions, char, mem_capacity=32000):
    result_dict = dict()
    evdicts = dict()
    misses = dict()

    L = LambdaScheduler(policy, mem_capacity)
    lambdas, trace = load_trace(num_functions, char)
    for d, t in trace:
        if np.random.randint(low=0, high=10) == 0:
            L.runActivation(d, t)

    # policy = string 
    # L.evdict:    dict[func_name] = eviction_count
    # L.miss_stats: dict of function names whos entries are  {"misses":count, "hits":count}
    # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
    # capacity_misses: dict[func_name] = invocations_not_handled
    # len_trace: long
    data = (policy, L.evdict, L.miss_stats(), lambdas, L.capacity_misses, len(trace))
    save_pth = "/data2/alfuerst/azure/functions/random_trace_runs"
    name = "{}-{}-{}-{}.pckl".format(policy, num_functions, mem_capacity, char)
    save_pth = os.path.join(save_pth, name)
    with open(save_pth, "w+b") as f:
        pickle.dump(data, f)
    print("done", name)

def run_multiple_expts():
    policies = ["GD", "TTL" , "LRU", "FREQ", "SIZE", "HIST"]
    results = []
    with mp.Pool() as pool:
        mems = [1, 2, 4, 8, 10]
        num_funcs = [10, 20, 50, 100, 200, 500, 1000]
        for mem in mems:
            for num_func in num_funcs:
                for char in ["a", "b", "c", "d", "e"]:
                    for policy in policies:
                        result = pool.apply_async(compare_pols, [policy, num_func, char, mem*1024])
                        results.append(result)
        [result.wait() for result in results]
        for result in results:
            print(result.get())

if __name__ == "__main__":
    run_multiple_expts()
