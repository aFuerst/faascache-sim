from collections import defaultdict
from LambdaData import *
from Container import *
from TraceGen import *
import os
import pickle

# lt = AzureTrace()
# lambdas, input_trace = lt.gen_full_trace(50, sample_seed=None)
# running = dict() 


storage = "./traces"
for file in os.listdir(storage):
    in_use_mem = 0
    max_mem = 0
    running = dict() 

    pth = os.path.join(storage, file)
    with open(pth, "r+b") as f:
        input_trace = pickle.load(f)

    lambdas, input_trace = input_trace

    for d, t in input_trace:
        remove = []
        for uuid, data in running.items():
            start, finish, mem = data
            if finish <= t:
                in_use_mem -= mem
                remove.append(uuid)

        for uuid in remove:
            del running[uuid]

        uuid = str(d) + str(t)
        running[uuid] = (t, t + d.warm_time, d.mem_size)
        in_use_mem += d.mem_size
        if in_use_mem > max_mem:
            max_mem = in_use_mem

    print(file, "max memory usage {}".format(max_mem), "number of invocations {}".format(len(input_trace)))