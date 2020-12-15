from Container import *
from LambdaData import *
import pandas as pd
import numpy as np
from random import choice
import  os
from math import ceil
import random, pickle

class LambdaTrace:
    kinds = ['a','b','c','d']
    mem_sizes = [10, 50, 100, 1000] #MB 
    run_times = [10, 500, 500, 3000] #ms
    warm_times = [5, 100, 400, 2000] #ms 

    workload_mix = [1, 1, 1, 1] #MUST BE integers 
    iat = [50, 50, 50, 50] #ms 
    # iat = list(np.array(warm_times)*10) # IAT is 1-2 orders of magnitude higher than execution time

    def __init__(self):
        self.most_recent_invocation = dict() #time of most recent invocation for each lambda
        self.proportional_lambdas = []
        self.lam_datas = []
        self.lambdas = dict() #terrible name, but older convention ugh
        for i,k in enumerate(self.kinds):
            self.lambdas[k] = (self.mem_sizes[i], 
                                             self.run_times[i], self.warm_times[i])
            self.lam_datas.append(LambdaData(k, self.mem_sizes[i], 
                                             self.run_times[i], self.warm_times[i]))
        self.frac_iat = self.get_frac_iat()
    
    def get_frac_iat(self):
        iats = np.array(self.iat)
        s = sum(self.iat)
        frac_iat = iats/s 
        reciprocal_iat = 1.0/frac_iat 
        recipsum = sum(reciprocal_iat)
        return reciprocal_iat/recipsum
    
    def gen_full_trace(self, n, sample_seed=0):
        #n: number of entries to generate
        trace = []
        self.curr_time = 0 
        
        for i,d in enumerate(self.lam_datas):
            t = 0 
            for _ in range(int(self.frac_iat[i]*n)):
                next_iat_ms = int(np.random.exponential(self.iat[i]))
                t = t + next_iat_ms
                trace.append((d, t))
        
        out_trace = sorted(trace, key=lambda x:x[1]) #(lamdata, t)
        return self.lambdas, out_trace 

class AzureTrace (LambdaTrace):
    store = "/data2/alfuerst/azure/functions/trace_pckl/"

    # datapath = "/data2/alfuerst/azure/functions/"
    # durations = "function_durations_percentiles.anon.d{0:02d}.csv"
    # duration_columns = ["HashOwner","HashApp","HashFunction","Average", "Count", "Minimum", "Maximum", "percentile_Average_0", "percentile_Average_1", "percentile_Average_25", "percentile_Average_50", "percentile_Average_75", "percentile_Average_99", "percentile_Average_100"]

    # invocations = "invocations_per_function_md.anon.d{0:02d}.csv"
    # buckets = [str(i) for i in range(1, 1441)]
    # invocation_columns = ["HashOwner","HashApp","HashFunction","Trigger"] + [str(i) for i in range(1, 1441)]
    # function_metadata = ["py:3", "py:ai", "py:vid"]

    # mem_columns = ["HashOwner", "HashApp", "SampleCount", "AverageAllocatedMb", "AverageAllocatedMb_pct1", "AverageAllocatedMb_pct5", "AverageAllocatedMb_pct25", "AverageAllocatedMb_pct50", "AverageAllocatedMb_pct75", "AverageAllocatedMb_pct95", "AverageAllocatedMb_pct99", "AverageAllocatedMb_pct100"]
    # mem_fnames = "app_memory_percentiles.anon.d{0:02d}.csv"

    # kinds = ['a','b','c','d']

    def _divive_by_func_num(self, row):
        return ceil(row["AverageAllocatedMb"] / self.group_by_app[row["HashApp"]])

    def __init__(self):
        # files are traces themselves. Just need to combine them together
        # format: (lambdas, trace) => 
        # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
        # trace = [LambdaData(func_name, mem, cold_time, warm_time), start_time]
        self.pckls = os.listdir(self.store)
        self.pckls = [file for file in self.pckls if os.path.isfile(os.path.join(self.store, file))]

    def gen_full_trace(self, n=30, sample_seed=None):
        secs_p_min = 60
        milis_p_sec = 1000
        trace = []
        lambdas = {}

        if n is None or n >= len(self.pckls):
            for pckl in self.pckls:
                path = os.path.join(self.store, pckl)
                with open(path, "r+b") as f:
                    data = pickle.load(f)
                    one_lambda, one_trace = data
                    lambdas = {**lambdas, **one_lambda}
                    trace += one_trace
        else:
            while n > 0:
                pckl = random.choice(self.pckls)
                path = os.path.join(self.store, pckl)
                with open(path, "r+b") as f:
                    data = pickle.load(f)
                    one_lambda, one_trace = data
                    lambdas = {**lambdas, **one_lambda}
                    trace += one_trace
                n -= 1

        out_trace = sorted(trace, key=lambda x:x[1]) #(lamdata, t)
        return lambdas, out_trace

class PlannedTrace (LambdaTrace):
    kinds = ['smol','lorge']
    mem_sizes = [200, 2000] #MB 
    run_times = [400, 990] #ms
    warm_times = [300, 600] #ms 

    workload_mix = [1, 1] #MUST BE integers 
    iat = list(np.array(warm_times)*1000)

    def __init__(self):
        self.most_recent_invocation = dict() #time of most recent invocation for each lambda
        self.proportional_lambdas = []
        self.lam_datas = []
        self.lambdas = dict() #terrible name, but older convention ugh
        for i,k in enumerate(self.kinds):
            self.lambdas[k] = (self.mem_sizes[i], 
                                             self.run_times[i], self.warm_times[i])
            self.lam_datas.append(LambdaData(k, self.mem_sizes[i], 
                                             self.run_times[i], self.warm_times[i]))
        self.frac_iat = self.get_frac_iat()
        
        return 
    
    def get_frac_iat(self):
        iats = np.array(self.iat)
        s = sum(self.iat)
        frac_iat = iats/s 
        reciprocal_iat = 1.0/frac_iat 
        recipsum = sum(reciprocal_iat)
        return reciprocal_iat/recipsum
    
    def gen_trace_entry(self):
        pass
    
    def gen_full_trace(self, n, sample_seed=0) :
        #n: number of entries to generate
        trace = []
        self.curr_time = 0 
        
        for i,d in enumerate(self.lam_datas):
            t = 0 
            for _ in range(int(self.frac_iat[i]*n)):
                next_iat_ms = int(np.random.exponential(self.iat[i]))
                t = t + next_iat_ms
                trace.append((d, t))
        out_trace = sorted(trace, key=lambda x:x[1]) #(lamdata, t)
        return self.lambdas, out_trace 

if __name__ == "__main__":
    import pickle
    save_pth = "/data2/alfuerst/azure/functions/trace_pckl/precombined"
    trace = AzureTrace()
    num_funcs = [10, 20, 50, 100, 200, 500, 1000, 10000] #, 20000, None]
    for size in num_funcs:
        for letter in ["a", "b", "c", "d", "e"]:
            pth = os.path.join(save_pth, str(size)+"-"+letter+".pckl")
            if not os.path.exists(pth):
                t = trace.gen_full_trace(size, sample_seed=None)  
                with open(pth, "w+b") as f:
                    # format: (lambdas, trace) => 
                    # lambdas:    dict[func_name] = (mem_size, cold_time, warm_time)
                    # trace = [LambdaData(func_name, mem, cold_time, warm_time), start_time]
                    pickle.dump(t, f)