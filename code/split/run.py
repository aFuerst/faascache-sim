#!/usr/bin/python3
from collections import defaultdict
import multiprocessing as mp
from TraceGen import *
from LambdaScheduler import LambdaScheduler
import pickle

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

def analyze_timings(policy, lambdas, L):
    """ Effective access time, etc. """
    msd = L.miss_stats()
    total_cold = []
    avg_latencies = [] 
    pct_increases  = []
    out_dict = dict()  #BAD: We'll insert some global and some per-key stats
    out_dict["global"] = dict()
    out_dict["global"]["server_cold"] = 0 
    total_accesses = 0 #for computing weighted averages 
    
    for k in sorted(msd.keys()):
        out_dict[k] = dict() 
        misses = msd[k]['misses']
        hits = msd[k]['hits']
        
        out_dict[k]["misses"] = misses 
        out_dict[k]["hits"] = hits 
        out_dict[k]["accesses"] = misses+hits 
        total_accesses += out_dict[k]["accesses"]
        
        twarm = lambdas[k][3]
        trun = lambdas[k][2]
        
        out_dict[k]["total_cold"] = twarm*misses 
        
        out_dict["global"]["server_cold"] += out_dict[k]["total_cold"]        
        #Effective acccess time 
        out_dict[k]["eat"] = ((misses*trun) + (hits*(trun-twarm)))/(misses+hits)
        
        if trun-twarm == 0:
            pct_incr = 0
        else:
            pct_incr = twarm*misses/((misses+hits)*(trun-twarm))
        out_dict[k]["pct_incr_vs_all_hits"] = pct_incr
    #
    out_dict["global"]["server_cold"] = out_dict["global"]["server_cold"]/total_accesses 
    
    out_dict["global"]["wted_eat"] = sum([out_dict[k]["eat"]*out_dict[k]["accesses"]/total_accesses 
                                for k in msd.keys()])
     
    out_dict["global"]["wted_increase"] = sum([out_dict[k]["pct_incr_vs_all_hits"]*out_dict[k]["accesses"]/total_accesses 
                                for k in msd.keys()])
      
    return out_dict


def average_dicts(dlist):
    n = len(dlist)
    outdict = dict()
    #Assume that the keys are the same for all the dictionaries. 
    #Simple dicts only, not nested or anything
    keys = dlist[0].keys()
    #print("keys:" + keys)
    for k in keys:
        vals = np.mean([adict[k] for adict in dlist])
        outdict[k] = vals 
        
    return outdict

def compare_pols(policy, trace, lambdas, mem_capacity=32000):
    result_dict = dict() 
    evdicts = dict()
    misses = dict()

    L = LambdaScheduler(policy, mem_capacity)
    for d, t in trace:
        L.runActivation(d, t)

    # run_misses = sum([val for val in L.capacity_misses])
    # misses[policy] = L.capacity_misses
    #achtung. Losing out on per-key information here... 
    #End multiple trials for the given policy. 
    # result_dict[policy] = analyze_timings(policy, lambdas, L)
    # evdicts[policy] = L.evdict

    return policy, L.evdict, analyze_timings(policy, lambdas, L), list(lambdas.keys())

def run_multiple_expts(n, LT, trace_size, mem_capacity):
    averaged_result_dict = dict()
    results_per_policy = defaultdict(list) # p -> [global-dicts]
    misses_per_policy = defaultdict(list) # p -> [global-dicts]
    policies = ["GD", "TTL" , "LRU", "FREQ", "SIZE", "HIST"]
    results = []
    functions = []
    with mp.Pool() as pool:
        for _ in range(n):
            lambdas, input_trace = LT.gen_full_trace(trace_size)
            for policy in policies:
                result = pool.apply_async(compare_pols, [policy, input_trace, lambdas, mem_capacity])
                results.append(result)
        [result.wait() for result in results]

    for result in results:
        policy, evdict, result_dict, function_keys = result.get()
        functions.append(function_keys)
        # policies = result_dict.keys()
        #Ignore evdicts for now. result_dict[k]["global"] is to be averaged 
        # for p in policies:
        results_per_policy[policy].append(result_dict["global"])

    for p in policies: 
        averaged_result_dict[p]  = average_dicts(results_per_policy[p])

    save_name = "./figs/sim-{}-{}.png".format(mem_capacity//1024, trace_size)
    print("saving to", save_name)
    plot_results(averaged_result_dict, save_name)
    pckl_name = "/data2/alfuerst/azure/functions/trace_pckl/runs/sim-{}-{}.pckl".format(mem_capacity//1024, trace_size)
    with open(pckl_name, "w+b") as f:
        pickle.dump(functions, f)

    return averaged_result_dict

def plot_results(result_dict, save_path=None):
    contenders = list(result_dict.keys())
    contenders.remove("GD")
    contenders.insert(0, "GD")

    wted_increases = [result_dict[k]["wted_increase"]*100
                      for k in contenders]
        
    wted_eat = [result_dict[k]["wted_eat"]
                      for k in contenders]

    server_cold = [result_dict[k]["server_cold"]
                      for k in contenders]
    
    ### Now the plotting begins... 
    
    if save_path is not None:
        fig, ax = plt.subplots()
        plt.tight_layout()
        fig.set_size_inches(5,3)
        ax.bar(contenders, wted_increases, width=0.5)
        ax.set_ylabel("% increase in execution time")
        plt.savefig(save_path, bbox_inches="tight")
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    fig.set_size_inches(15,3)
    ax = ax1 
    ax.bar(contenders, wted_increases)
    ax.set_ylabel("% increase in execution time")
    ax.set_title("% increase in execution time")
    
    ax = ax2 
    ax.bar(contenders, wted_eat)
    ax.set_ylabel("Effective response time (ms)")
    ax.set_title("Effective response time")
    
    ax = ax3
    ax.bar(contenders, server_cold)
    ax.set_ylabel("Server cold time per access (ms)")
    ax.set_title("Server cold time per access")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run Lambda simulator')
    parser.add_argument('-m', "--mem", type=int, action="store", default=1)
    parser.add_argument('-f', "--functions", type=int, action='store', default=1)
    parser.add_argument('-n', "--num-runs", type=int, action='store', default=5)
    parser.add_argument('-a', "--all", action='store_true')

    args = parser.parse_args()
    gb_mem = args.mem
    num_functions = args.functions
    n = args.num_runs
    try:
        if args.all:
            mems = [1, 2, 4, 8, 10, 20, 40, 50, 60, 80]
            num_funcs = [10, 20, 50, 100, 200, 500, 1000, 10000]   #, 20000, None]
            for mem in mems:
                for num_func in num_funcs:
                    print("running mem:{}, func:{}".format(mem, num_func))
                    run_multiple_expts(n, AzureTrace(), num_func, mem*1024)
        else:
            result_dict = run_multiple_expts(n, AzureTrace(), num_functions, gb_mem*1024)
    except Exception as e:
        import sys
        err_type, value, traceback = sys.exc_info()
        err_file = "./figs/sim-{}-{}.err".format(gb_mem, num_functions)
        with open(err_file, "w") as f:
            f.writelines([str(err_type), "\n"])
            f.writelines([str(value), "\n"])
            f.writelines([str(traceback), "\n"])
