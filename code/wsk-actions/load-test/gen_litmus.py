import numpy as np
import pandas as pd
import pickle

# Traces are list of tuples
# of (action_name, invocation_time, memory_usage, cold_time, warm_time)


def save_pckl(obj, file):
    with open(file, "w+b") as f:
        pickle.dump(obj, f)


def gen_trace(name: str, mem: int = 100, warm_ms: int = 100, cold_ms: int = 100, iat: int = 100, start: int = 0):
    activations = list()
    two_hrs_ms = 2 * 60 * 60 * 1000
    t = start
    while t < two_hrs_ms:
        activations.append((name, t, mem, warm_ms, cold_ms))
        t += iat
    return activations

def sort_trace(*traces):
    traces = [item for sublist in traces for item in sublist]
    return sorted(traces, key=lambda x: x[1])

#################################################################################################################
#                                       LRU bust litmus                                                         #
#################################################################################################################


def gen_lru():
    trace = []
    trace += gen_trace("a", 300, 100, 300, 500, 0)
    trace += gen_trace("b", 300, 100, 300, 500, 50)
    trace += gen_trace("c", 300, 100, 300, 500, 100)
    trace += gen_trace("d", 300, 100, 300, 500, 150)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/lru_litmus.pckl")
    print("lru done")

#################################################################################################################
#                                       IAT bust litmus                                                         #
#################################################################################################################


def gen_iat():
    mins_11 = 11 * 60 * 1000
    trace = []
    trace += gen_trace("a", 250, 100, 300, mins_11, 0)
    trace += gen_trace("b", 250, 100, 300, mins_11, 0)
    trace += gen_trace("c", 250, 100, 300, mins_11, 0)
    trace += gen_trace("d", 250, 100, 300, mins_11, 0)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/iat_litmus.pckl")
    print("iat done")

#################################################################################################################
#                                       Size Priority litmus                                                    #
#################################################################################################################


def gen_size_priority():
    trace = []
    trace += gen_trace("large", 600, 100, 300, 350, 0)
    trace += gen_trace("small", 300, 100, 300, 350, 0)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/size_litmus.pckl")
    print("size done")

#################################################################################################################
#                                    Frequency Priority litmus                                                  #
#################################################################################################################


def gen_freq_priority():
    trace = []
    trace += gen_trace("rare_1", 250, 100, 300, 1000, 0)
    trace += gen_trace("rare_2", 250, 100, 300, 1000, 0)
    trace += gen_trace("rare_3", 250, 100, 300, 1000, 0)
    trace += gen_trace("often", 250, 100, 300, 200, 0)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/freq_litmus.pckl")
    print("freq done")

#################################################################################################################
#                                    Frequency Priority Substitute litmus                                       #
#################################################################################################################


def gen_freq_priority_sub():
    trace = []
    trace += gen_trace("rare_1", 250, 100, 300, 1500, 0)
    trace += gen_trace("rare_2", 250, 100, 300, 1500, 300)
    trace += gen_trace("rare_3", 250, 100, 300, 1500, 600)
    trace += gen_trace("often", 250, 100, 300, 400, 50)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/freq_litmus_sub.pckl")
    print("freq done")

#################################################################################################################
#                                       LRU bust Substitute litmus                                              #
#################################################################################################################


def gen_lru_sub():
    trace = []
    trace += gen_trace("a", 300, 100, 300, 1000, 0)
    trace += gen_trace("b", 300, 100, 300, 1000, 200)
    trace += gen_trace("c", 300, 100, 300, 1000, 400)
    trace += gen_trace("d", 300, 100, 300, 1000, 600)
    trace = sort_trace(trace)
    save_pckl(trace, "./traces/lru_litmus_sub.pckl")
    print("lru done")

#################################################################################################################
# Run #
#################################################################################################################
gen_lru()
gen_iat()
gen_size_priority()
gen_freq_priority()
gen_lru_sub()
gen_freq_priority_sub()
