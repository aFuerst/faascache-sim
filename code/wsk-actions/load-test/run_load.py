import numpy as np
import pandas as pd
import os
import json
from time import time

from wsk_interact import *

import pickle

set_properties()

pth = "/data2/alfuerst/azure/functions/trace_pckl/precombined/{}-{}.pckl".format(num_functions, char)
with open(pth, "r+b") as f:
    lambdas, trace = pickle.load(f)

for action, metadata in lambdas.items():
    memory, _, _ = metadata
    add_action(action,  "./lookbusy/__main__.py", container="python:lookbusy", memory=memory)

start = time()
for tup in trace:
    t = time()
    hash_app, invoc_time_ms, mem, warm, cold = tup
    invoc_time = invoc_time_ms / 1000 # convert ms to float s
    while t - start < invoc_time:
        t = time()
    invoke_action_async(hash_app, {"cold_run":cold, "warm_run":warm, "mem_mb":mem})