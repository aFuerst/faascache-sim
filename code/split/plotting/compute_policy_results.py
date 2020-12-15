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

def analyze_timings(policy, lambdas, msd):
    """ Effective access time, etc. """
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

data_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/"
save_path = "/data2/alfuerst/azure/functions/trace_runs_rep_392/analyzed/"

def get_info_from_file(filename):
    policy, num_funcs, mem, run = filename[:-5].split("-")
    return policy, int(num_funcs), int(float(mem)), run

def load_data(path):
    with open(path, "r+b") as f:
        return pickle.load(f)

def compute_timings(file):
    pth = os.path.join(data_path, file)
    policy, num_funcs, mem, run = get_info_from_file(file)
    policy, evdict, miss_stats, lambdas, capacity_misses, len_trace = load_data(pth)
    anal = analyze_timings(policy, lambdas, miss_stats)

    name = "{}-{}-{}-{}.pckl".format(policy, num_funcs, mem, run)
    save_pth = os.path.join(save_path, name)
    # capacity_misses: dict[func_name] = invocations_not_handled
    # len_trace: long
    data = (policy, anal, capacity_misses, len_trace)
    with open(save_pth, "w+b") as f:
        pickle.dump(data, f)
    print("done", name)
        
def compute_all():
    with mp.Pool() as pool:
        files = [file for file in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, file))]
        print("computing {} files".format(len(files)))
        pool.map(compute_timings, files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='analyze FaasCache Simulation')
    parser.add_argument("--pckldir", type=str, default="/data2/alfuerst/verify-test/", required=False)
    parser.add_argument("--savedir", type=str, default="/data2/alfuerst/verify-test/analyzed/", required=False)
    args = parser.parse_args()
    data_path = args.pckldir
    save_path = args.savedir
    compute_all()
    # compute_timings("GD-200-768-e.pckl")