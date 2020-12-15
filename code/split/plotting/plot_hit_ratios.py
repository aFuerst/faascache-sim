import os,sys
import pickle
import math
from collections import defaultdict
import numpy as np
import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF 
# This needs scipy==1.2.0 

# pckls will have edcf for the given trace
ecdf_path = "/data2/alfuerst/azure/functions/trace_pckl/represent/ecdfs/"

def get_info_from_file(filename):
    policy, num_funcs, mem, run = filename[:-5].split("-")
    return policy, int(num_funcs), int(float(mem)), run


fig, ax1 = plt.subplots()

#########################################################################
# Plot ECDF

with open("/data2/alfuerst/azure/functions/trace_pckl/represent/ecdfs/392-b-ecdf.pckl", "r+b") as f:
    ecdf = pickle.load(f)
ax1.plot(ecdf.x/1024, ecdf.y, label="Reuse Dist.", color="tab:blue")

store = "/data2/alfuerst/azure/functions/trace_runs_rep/analyzed"

#########################################################################
# Plot GD

data = list()
dropped = list()
for file in os.listdir(store):
    if "GD-392" in file:
        policy, num_funcs, mem, run = get_info_from_file(file)
        with open(os.path.join(store, file), "r+b") as f:
            policy, analysis, capacity_misses, len_trace = pickle.load(f)

        miss_count = sum([cnt["misses"] for key, cnt in analysis.items() if key != "global"])
        dropped_count = sum([cnt for key, cnt in capacity_misses.items()])
        p = 1 - ((miss_count + dropped_count) / len_trace)
        data.append((mem, p))

        p = 1 - ((miss_count) / (len_trace-dropped_count))
        dropped.append((mem, p))

data = sorted(data, key=lambda x: x[0])
# ax1.plot([x/1024 for x,y in data], [y for x,y in data], label="GD Empirical", color="tab:orange")
dropped = sorted(dropped, key=lambda x: x[0])
ax1.plot([x/1024 for x,y in dropped], [y for x,y in dropped], label="GreedyDual", color="tab:red")
#########################################################################
# Plot LRU


data = list()
dropped = list()
for file in os.listdir(store):
    if "LRU-392" in file:
        policy, num_funcs, mem, run = get_info_from_file(file)
        with open(os.path.join(store, file), "r+b") as f:
            policy, analysis, capacity_misses, len_trace = pickle.load(f)

        miss_count = sum([cnt["misses"] for key, cnt in analysis.items() if key != "global"])
        dropped_count = sum([cnt for key, cnt in capacity_misses.items()])
        p = 1 - ((miss_count + dropped_count) / len_trace)
        data.append((mem, p))

        p = 1 - ((miss_count) / (len_trace-dropped_count))
        dropped.append((mem, p))


data = sorted(data, key=lambda x: x[0])
# ax1.plot([x for x,y in data], [y for x,y in data], label="LRU Empirical", color="tab:blue")

dropped = sorted(dropped, key=lambda x: x[0])
# ax1.plot([x for x,y in dropped], [y for x,y in dropped], label="LRU (No Dropped)", color="tab:green")


#########################################################################
# Plot TTL


data = list()
dropped = list()
for file in os.listdir(store):
    if "TTL-392" in file:
        policy, num_funcs, mem, run = get_info_from_file(file)
        with open(os.path.join(store, file), "r+b") as f:
            policy, analysis, capacity_misses, len_trace = pickle.load(f)

        miss_count = sum([cnt["misses"] for key, cnt in analysis.items() if key != "global"])
        dropped_count = sum([cnt for key, cnt in capacity_misses.items()])
        p = 1 - ((miss_count + dropped_count) / len_trace)
        data.append((mem, p))

        p = 1 - ((miss_count) / (len_trace-dropped_count))
        dropped.append((mem, p))


data = sorted(data, key=lambda x: x[0])
# ax1.plot([x for x,y in data], [y for x,y in data], label="TTL Empirical", color="tab:purple")

dropped = sorted(dropped, key=lambda x: x[0])
# ax1.plot([x for x,y in dropped], [y for x,y in dropped], label="TTL (No Dropped)", color="tab:pink")

save_path = "../figs/hit-ratio-{}-{}.pdf".format(num_funcs, run)
ax1.set_xlabel("Cache Size (GB)")
ax1.set_ylabel("Hit Ratio")

# inset axes....
axins = ax1.inset_axes([0.5, 0.2, 0.47, 0.47])
# axins.imshow(Z2, extent=extent, interpolation="nearest", origin="lower")
# sub region of the original image
# axins.plot([x/1024 for x,y in data], [y for x,y in data], label="GD Empirical", color="tab:orange")
axins.plot([x/1024 for x,y in dropped], [y for x,y in dropped], label="GreedyDual", color="tab:red")
axins.plot(ecdf.x/1024, ecdf.y, label="Reuse Dist.", color="tab:blue")
x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9
axins.set_xlim((-5, 200))
# axins.set_xscale('log')
axins.set_xticklabels('')
axins.set_yticklabels('')
axins.tick_params(axis=u'both', which=u'both',length=0)
axins.set_xlabel("Full Graph")

# ax1.set_xscale('log')
ax1.set_xlim((0, 20000/1024))
ax1.legend(bbox_to_anchor=(0,1.13), loc="upper left", ncol=2, columnspacing=1)
plt.savefig(save_path, bbox_inches="tight")
plt.close(fig)

