#!/usr/bin/python3
from collections import defaultdict
import multiprocessing as mp
from TraceGen import *
from LambdaScheduler import LambdaScheduler
import pickle
import argparse
import os

def load_trace(num_functions, char, trace_path):
    fname = "{}-{}.pckl".format(num_functions, char)
    with open(os.path.join(trace_path, fname), "r+b") as f:
        return pickle.load(f)

def compare_pols(policy, num_functions, char, mem_capacity=32000, args=None):
    # save_pth = "/data2/alfuerst/verify-test/"
    # log_dir = "/data2/alfuerst/verify-test/logs/"
    save_pth = args.savedir
    log_dir = args.logdir
    name = "{}-{}-{}-{}.pckl".format(policy, num_functions, mem_capacity, char)
    save_pth = os.path.join(save_pth, name)

    if not os.path.exists(save_pth):
        result_dict = dict()
        evdicts = dict()
        misses = dict()

        L = LambdaScheduler(policy, mem_capacity, num_functions, char, log_dir)
        lambdas, trace = load_trace(num_functions, char, args.tracedir)
        i = 0
        for d, t in trace:
            i += 1
            L.runActivation(d, t)

        L.MemUsageHist.flush()
        L.PerformanceLog.flush()
        L.PureCacheHist.flush()

        L.MemUsageHist.close()
        L.PerformanceLog.close()
        L.PureCacheHist.close()

        # policy = string
        # L.evdict:    dict[func_name] = eviction_count
        # L.miss_stats: dict of function names whos entries are  {"misses":count, "hits":count}
        # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
        # capacity_misses: dict[func_name] = invocations_not_handled
        # len_trace: long
        data = (policy, L.evdict, L.miss_stats(), lambdas, L.capacity_misses, len(trace))
        with open(save_pth, "w+b") as f:
            pickle.dump(data, f)

    print("done", name)

def run_multiple_expts(args):
    policies = ["GD", "TTL", "LRU", "LND", "HIST", "FREQ", "SIZE"]
    mems = [i for i in range(1000, 80000, args.memstep)]
    mems = set(mems)
    results = []
    print(len(policies) * len(mems))
    with mp.Pool() as pool:
        for policy in policies:
            for mem in mems:
                for num_func in [args.numfuncs]:
                    for char in ["b"]:
                        result = pool.apply_async(compare_pols, [policy, num_func, char, mem, args])
                        results.append(result)
        [result.wait() for result in results]
        for result in results:
            r = result.get()
            if r is not None:
                print(r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run FaasCache Simulation')
    parser.add_argument("--tracedir", type=str, default="/data2/alfuerst/azure/functions/trace_pckl/represent/", required=False)
    parser.add_argument("--numfuncs", type=int, default=392, required=False)
    parser.add_argument("--savedir", type=str, default="/data2/alfuerst/verify-test/", required=False)
    parser.add_argument("--logdir", type=str, default="/data2/alfuerst/verify-test/logs/", required=False)
    parser.add_argument("--memstep", type=int, default=3000, required=False)
    args = parser.parse_args()
    if not os.path.exists(args.savedir):
        os.makedirs(args.savedir)
    if not os.path.exists(args.logdir):
        os.makedirs(args.logdir)

    print(args)
    run_multiple_expts(args)
