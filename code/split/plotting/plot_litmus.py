import numpy as np
import pandas as pd
import os

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
fig.set_size_inches(5,3)

file = "/home/alfuerst/repos/faas-keepalive-20/experiments/litmus_tests.csv"

cols = ["LitmusTest","vanilla_cold","vanilla_warm","cache_cold","cache_warm","vanilla_delayed","cache_delayed", "len"]
litmi = pd.read_csv(file, index_col="LitmusTest")

###########################################################
# Plot 1 GB runs
###########################################################


vanilla = []
cache = []

xs = np.array([1, 2, 3, 4])
tests = ["freq", "iat", "lru", "size"]
for test in tests:
    vanilla.append(litmi.loc[test,"vanilla_cold"] / (litmi.loc[test,"vanilla_cold"]+litmi.loc[test,"vanilla_warm"]))
    cache.append(litmi.loc[test,"cache_cold"] / (litmi.loc[test,"cache_cold"]+litmi.loc[test,"cache_warm"]))

ticks = ["Freq", "IAT", "Cyclic", "Size"]
ax.bar(xs-0.1, vanilla, width=0.2, color='tab:blue', align='center', label="OpenWhisk")
ax.bar(xs+0.1, cache, width=0.2, color='tab:red', align='center', label="FaasCache")
ax.set_xticklabels([""]+ticks)
ax.set_xlabel("Litmus Test")
ax.set_ylabel("% Cold Starts")
fig.legend()
plt.savefig("../figs/litmus/litmus.pdf", bbox_inches="tight")

###########################################################
# Plot 2 GB runs
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1, 2, 3, 4])
tests = ["freq_2", "iat_2", "lru_2", "size_2"]
for test in tests:
    vanilla.append(litmi.loc[test,"vanilla_cold"] / (litmi.loc[test,"vanilla_cold"]+litmi.loc[test,"vanilla_warm"]))
    cache.append(litmi.loc[test,"cache_cold"] / (litmi.loc[test,"cache_cold"]+litmi.loc[test,"cache_warm"]))

ax.bar(xs-0.1, vanilla, width=0.2, color='tab:blue', align='center', label="OpenWhisk")
ax.bar(xs+0.1, cache, width=0.2, color='tab:red', align='center', label="FaasCache")
ticks = ["Freq", "IAT", "Cyclic", "Size"]
ax.set_xticklabels([""]+ticks)
ax.set_xlabel("Litmus Test")
ax.set_ylabel("% Cold Starts")
fig.legend()
plt.savefig("../figs/litmus/litmus_2.pdf", bbox_inches="tight")


###########################################################
# Plot 2 GB runs
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1, 2, 3])
tests = ["freq_2", "lru_2", "size_2"]
for test in tests:
    d = litmi.loc[test,"len"] - (litmi.loc[test,"vanilla_cold"] + litmi.loc[test,"vanilla_warm"])
    print(litmi.loc[test,"vanilla_cold"], litmi.loc[test,"vanilla_warm"], d)
    vanilla.append((litmi.loc[test,"vanilla_cold"], litmi.loc[test,"vanilla_warm"], d))

    d = litmi.loc[test,"len"] - (litmi.loc[test,"cache_cold"] + litmi.loc[test,"cache_warm"])
    cache.append((litmi.loc[test,"cache_cold"], litmi.loc[test,"cache_warm"], d))

print(vanilla)
print(cache)

v_height = [c for c, w, d in vanilla]
v_bottom = [0]*len(vanilla)
v_cold = ax.bar(xs - 0.1, height=v_height, bottom=v_bottom, width=0.2, color='black', align='center', label="OW Cold")
v_height = [w for c, w, d in vanilla]
v_bottom = [c for c, w, d in vanilla]
v_warm = ax.bar(xs-0.1, height=v_height, bottom=v_bottom, width=0.2, color='red', align='center', label="OW Warm")

# v_height = [d for c, w, d in vanilla]
# v_bottom = [c+w for c, w, d in vanilla]
# v_dropped = ax.bar(xs-0.1, height=v_height, bottom=v_bottom, width=0.2, color='black', align='center', label="OW Dropped")


c_height = [c for c, w, d in cache]
c_bottom = [0]*len(cache)
c_cold = ax.bar(xs + 0.1, height=c_height, bottom=c_bottom, width=0.2, color='grey', align='center', label="FC Cold")
c_height = [w for c, w, d in cache]
c_bottom = [c for c, w, d in cache]
c_warm = ax.bar(xs+0.1, height=c_height, bottom=c_bottom, width=0.2, color='gold', align='center', label="FC Warm")

# c_height = [d for c, w, d in cache]
# c_bottom = [c+w for c, w, d in cache]
# c_dropped = ax.bar(xs+0.1, height=c_height, bottom=c_bottom, width=0.2, color='black', align='center', label="FC Dropped")

from matplotlib.legend_handler import HandlerLine2D, HandlerTuple

ticks = ["Skewed Freq", "Cyclic", "Skewed Size"]
ax.set_xticks(xs)
ax.set_xticklabels(ticks)
ax.set_xlabel("Workload Type")
ax.set_ylabel("# of Invocations")
# l = fig.legend([(v_cold, v_warm), (c_cold, c_warm)], ['OpenWhisk', "FaasCache"], numpoints=1,
#                handler_map={tuple: HandlerTuple(ndivide=None)})
ax.legend(bbox_to_anchor=(-.5,1.2), ncol=4, loc="upper left", columnspacing=1)
# fig.legend()
plt.savefig("../figs/litmus/litmus_2_stacked.pdf", bbox_inches="tight")

###########################################################
# Plot 2 GB served
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1, 2, 3, 4])
tests = ["freq_2", "iat_2", "lru_2", "size_2"]
for test in tests:
    vanilla.append(litmi.loc[test,"vanilla_cold"]+litmi.loc[test,"vanilla_warm"])
    cache.append(litmi.loc[test,"cache_cold"]+litmi.loc[test,"cache_warm"])

vanilla = np.array(vanilla)
cache = np.array(cache)

ax.bar(xs, cache/vanilla, width=0.2, color='tab:purple', align='center')
ax.set_xticks(xs)
ticks = ["Freq", "IAT", "Cyclic", "Size"]
ax.set_xticklabels(ticks)
ax.set_xlabel("Litmus Test")
ax.set_ylabel("% Growth in Served Requests")
plt.savefig("../figs/litmus/served_2.pdf", bbox_inches="tight")

###########################################################
# Plot 2 GB delayed
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1, 2, 3, 4])
tests = ["freq_2", "iat_2", "lru_2", "size_2"]
for test in tests:
    vanilla.append(litmi.loc[test,"vanilla_delayed"])
    cache.append(litmi.loc[test,"cache_delayed"])

vanilla = np.array(vanilla)
cache = np.array(cache)

ax.bar(xs, cache/vanilla, width=0.2, color='tab:purple', align='center')
ax.set_xticks(xs)
ticks = ["Freq", "IAT", "Cyclic", "Size"]
ax.set_xticklabels(ticks)
ax.set_xlabel("Litmus Test")
ax.set_ylabel("Cache/OW Delayed")
plt.savefig("../figs/litmus/delayed_2.pdf", bbox_inches="tight")