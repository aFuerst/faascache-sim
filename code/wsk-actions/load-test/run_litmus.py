import numpy as np
import os
from time import time
import pickle

from wsk_interact import add_action, invoke_action_async, set_properties

set_properties()

# Traces are list of tuples
# of (action_name, invocation_time, memory_usage, cold_time, warm_time)

freq = "./traces/freq_litmus.pckl"
iat = "./traces/iat_litmus.pckl"
lru = "./traces/lru_litmus.pckl"
size = "./traces/size_litmus.pckl"

load = lru

with open(load, "r+b") as f:
    trace = pickle.load(f)

# print(trace)
names = set([i[0] for i in trace])
# print(names)

dedup = []
for item in names:
    for t in trace:
        if t[0] == item:
            dedup.append(t)
            break

# print(dedup)
for tup in dedup:
    hash_app, invoc_time_ms, mem, warm, cold = tup
    add_action(hash_app, "./lookbusy/__main__.py", container="python:lookbusy", memory=mem)
    print("added {}".format(hash_app))

start = time()
for tup in trace:
    t = time()
    hash_app, invoc_time_ms, mem, warm, cold = tup
    invoc_time = invoc_time_ms / 1000 # convert ms to float s
    while t - start < invoc_time:
        t = time()
    invoke_action_async(hash_app, {"cold_run":cold, "warm_run":warm, "mem_mb":mem})
