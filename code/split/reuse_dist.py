import os,sys
import pickle
import math
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF 
# This needs scipy==1.2.0 
from LambdaData import *

pckl_path = "/extra/alfuerst/azure/functions/trace_pckl/rare_large/"
two_hour_pckl_path = "/extra/alfuerst/azure/functions/trace_pckl/represent_two_hour/"
# pckls will have edcf for the given trace
ecdf_path = "/extra/alfuerst/azure/functions/trace_pckl/rare_large/ecdfs/"
two_hour_ecdf_path = "/extra/alfuerst/azure/functions/trace_pckl/represent_two_hour/ecdfs/"

def get_info_from_file(path):
    num_funcs, run = path[:-5].split("-")
    return int(num_funcs), run

# a, b, c, b, a
# <----------->
# reuse dist = size of unique accesses
# reuse dist = size(b) + size(c)
def compute_cdf(trace_path):
    num_funcs, run = get_info_from_file(trace_path)
    lambdas, input_trace = pickle.load(open(os.path.join(two_hour_pckl_path, trace_path), "rb"))
    N = len(input_trace)
    reuse_distances = []

    for i, (d_left, t_left) in enumerate(input_trace):
        left_kind = d_left.kind
        local_reuse_set = dict()
        
        for j in range(i+1, N):
            d, t = input_trace[j]
            
            if d.kind == left_kind or j == N :
                # We have found the back marker.
                current_rd = sum(local_reuse_set.values()) 
                # TODO: falling of the end
                reuse_distances.append(current_rd)
                break
            
            # if different from left_kind 
            local_reuse_set[d.kind] = d.mem_size

    e = ECDF(reuse_distances)
    save_path = two_hour_ecdf_path + "{}-{}-ecdf.pckl".format(num_funcs, run)
    with open(save_path, "w+b") as f:
        pickle.dump(e, f)
    # return e

def SHARDS_reusedist(trace_path, R=0.1):
    """ R is the sampling rate, like"""
    #hash(k) % P < T
    #R = T/P -> T=0.01P -> P > 100
    P  = 10000 
    T  = int(R*P)
    
    num_funcs, run = get_info_from_file(trace_path)
    lambdas, input_trace = pickle.load(open(os.path.join(pckl_path, trace_path), "rb"))

    last_access = dict()
    reuse_distances = []
    current_bytes = 0
    
    for i, (d, t) in enumerate(input_trace):
        k = d.kind 
        current_bytes += d.mem_size 
        if hash(k) % P < T: # chosen one 
            #Check if first access? 
            if k in last_access:
                rd = (current_bytes - last_access[k]) - 2.0*d.mem_size 
                # Account for left and right access 
                last_access[k] = current_bytes 
                reuse_distances.append(rd)
            else: # This is first access. 
                last_access[k] = current_bytes 
                #Ignore the reuse distance for the first access? 
    
    reuse_distances = np.array(reuse_distances)
    reuse_distances = reuse_distances*(1/R)
    # print(reuse_distances)
    e=ECDF(reuse_distances*R)
    save_path = ecdf_path + "{}-{}-ecdf.pckl".format(num_funcs, run)
    with open(save_path, "w+b") as f:
        pickle.dump(e, f)

    return reuse_distances

def find_nearest_idx(array,value):
    idx = np.searchsorted(array, value)
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return int(idx-1)
    else:
        return int(idx)

def hit_rate(e, cache_size):
    # e=ECDF(reuse_distances)
    hit_rate = e.y[find_nearest_idx(e.x,cache_size)]
    return hit_rate

def calc_all():
    import multiprocessing as mp
    with mp.Pool() as pool:
        files = [file for file in os.listdir(pckl_path) if os.path.isfile(os.path.join(pckl_path, file))]
        print("computing {} files".format(len(files)))
        pool.map(SHARDS_reusedist, files)

def calc_two_hours():
    import multiprocessing as mp
    with mp.Pool() as pool:
        files = [file for file in os.listdir(two_hour_pckl_path) if os.path.isfile(os.path.join(two_hour_pckl_path, file))]
        print("computing {} files".format(len(files)))
        pool.map(SHARDS_reusedist, files)


if __name__ == "__main__":
    calc_all()

    # trace_path = "10-c.pckl"
    # # input_trace : [(LambdaData, time)]
    # e = compute_cdf(trace_path)
    # chance = hit_rate(e, 100)
    # with open("test.pckl", "w+b") as f:
    #     pickle.dump(e, f)
    # print(chance, e)
    # plt.plot(e.x,e.y)
    # plt.xlabel("Cache Size")
    # plt.ylabel("Hit Ratio")
    # plt.savefig("test.png", bbox_inches="tight")