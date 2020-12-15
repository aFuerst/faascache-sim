from LambdaData import *
from TraceGen import LambdaTrace 
from random import choice
import numpy as np

class LowWellTrace (LambdaTrace):
    kind = 'a'
    mem_size = 100 #MB 
    run_time = 100 #ms
    warm_time = 50 #ms
    
    def __init__(self):
        self.lam_datas = []
        self.lambdas = dict() #terrible name, but older convention ugh
        self.lambdas[self.kind] = (self.mem_size, self.run_time, self.warm_time)
        self.d = LambdaData(self.kind, self.mem_size, self.run_time, self.warm_time)
    
    def gen_full_trace(self, n=0, sample_seed=0) :
        trace = []
        next_iat_ms = 0
        t = 0 
        for _ in range(1000):
            t = t + next_iat_ms
            trace.append((self.d, t))
            next_iat_ms += 1000*60
        return self.lambdas, trace 

class PrewarmableTrace (LambdaTrace):
    kind = 'a'
    mem_size = 100 #MB 
    run_time = 100 #ms
    warm_time = 50 #ms
    
    def __init__(self):
        self.lam_datas = []
        self.lambdas = dict() #terrible name, but older convention ugh
        self.lambdas[self.kind] = (self.mem_size, self.run_time, self.warm_time)
        self.d = LambdaData(self.kind, self.mem_size, self.run_time, self.warm_time)
    
    def gen_full_trace(self, n=0, sample_seed=0) :
        trace = []
        next_iat_ms = 60*1000*5
        t = 0 
        for _ in range(100):
            t = t + next_iat_ms + choice([60*1000, 0, 0, -60*1000])
            trace.append((self.d, t))
        return self.lambdas, trace 

class LongTTLTrace (LambdaTrace):
    kind = 'a'
    mem_size = 100 #MB 
    run_time = 100 #ms
    warm_time = 50 #ms
    p=[9.60000e-05, 2.46200e-03, 2.85950e-02, 1.46717e-01, 3.28005e-01, 3.23315e-01, 1.41154e-01, 2.73140e-02, 2.24800e-03, 9.40000e-05]
    
    def __init__(self):
        self.lam_datas = []
        self.lambdas = dict() #terrible name, but older convention ugh
        self.lambdas[self.kind] = (self.mem_size, self.run_time, self.warm_time)
        self.d = LambdaData(self.kind, self.mem_size, self.run_time, self.warm_time)
        self.iats = np.array([i for i in range(10)]) * 60*1000

    def gen_full_trace(self, n=0, sample_seed=0) :
        trace = []
        t = 0 
        for _ in range(1000):
            t = t + np.random.choice(self.iats, p=self.p)
            trace.append((self.d, t))
        return self.lambdas, trace 