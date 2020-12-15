import numpy as np
import pandas as pd
import os

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
fig.set_size_inches(5,3)

file = "/home/alfuerst/repos/faas-keepalive-20/experiments/sub_lit_tests.csv"

cols = ["LitmusTest","vanilla_cold","vanilla_warm","cache_cold","cache_warm","vanilla_delayed","cache_delayed"]
litmi = pd.read_csv(file, index_col="LitmusTest")
trace_len = 32400
timings = {"CNN":(6.5, 2), "DD":(2.2, 0.4), "Float":(2, 0.3), "Web":(2.4, 0.4)} # func : (cold, warm)

def plot(vanilla, cache, gm_mem):
        fig, ax1 = plt.subplots()
        fig.set_size_inches(5,3)
        colors = ["firebrick", "goldenrod", "teal", "orchid", "black"]

        served_vanilla = sum([sum([i for i in v.values()]) for v in vanilla.values()])
        dropped_vanilla = trace_len - served_vanilla

        # print(gm_mem, " dropped_vanilla", dropped_vanilla, "served_vanilla", served_vanilla)
        served_cache = sum([sum([i for i in v.values()]) for v in cache.values()])
        dropped_cache = trace_len - served_cache

        # print(gm_mem, " dropped_cache", dropped_cache, "served_cache", served_cache)

        warm_vanilla = sum([v for v in vanilla["warm"].values()])
        warm_cache = sum([v for v in cache["warm"].values()])

        print(gm_mem, " dropped_cache", dropped_cache, dropped_cache / trace_len, "dropped_vanilla", dropped_vanilla, dropped_vanilla/trace_len)
        print(gm_mem, " Warm %", " cache:", warm_cache / served_cache, "vanil: ", warm_vanilla / served_vanilla, "diff")

        print("warm inc:", (warm_cache / served_cache) / (warm_vanilla / served_vanilla), "w", warm_cache/warm_vanilla)


        vanilla_increase = []
        cache_increase = []
        for func, (trun, twarm) in timings.items():
                misses = vanilla["cold"][func]
                hits = vanilla["warm"][func]
                pct_incr = twarm*misses/((misses+hits)*(trun-twarm))
                vanilla_increase.append(pct_incr * (hits + misses) / served_vanilla)

        for func, (trun, twarm) in timings.items():
                misses = cache["cold"][func]
                hits = cache["warm"][func]
                pct_incr = twarm*misses/((misses+hits)*(trun-twarm))
                cache_increase.append(pct_incr * (hits + misses) / served_cache)

        vanilla_increase = sum(vanilla_increase) * 100
        cache_increase = sum(cache_increase) * 100
        print("wted_increase", "vanilla", vanilla_increase, "cache", cache_increase)

        for func in vanilla["warm"].keys():
                cache_hit_p = cache["warm"][func] / (cache["cold"][func] + cache["warm"][func])
                vanil_hit_p = vanilla["warm"][func] / (vanilla["cold"][func] + vanilla["warm"][func])
                print(func, " hit %", " cache:", cache_hit_p, " vanil:", vanil_hit_p, "  warm change:", cache["warm"][func] / vanilla["warm"][func])

        print()
        if dropped_cache >= 0:
                cache_cold = np.array([v for k,v in sorted(list(cache["cold"].items()), key= lambda t: t[0])] + [dropped_cache])
        else:
                cache_cold = np.array([v for k,v in sorted(list(cache["cold"].items()), key= lambda t: t[0])])
        cache_warm = np.array([v for k,v in sorted(list(cache["warm"].items()), key= lambda t: t[0])])
        if dropped_vanilla >= 0:
                vanilla_cold = np.array([v for k,v in sorted(list(vanilla["cold"].items()), key= lambda t: t[0])] + [dropped_vanilla])
        else:
                vanilla_cold = np.array([v for k,v in sorted(list(vanilla["cold"].items()), key= lambda t: t[0])])
        vanilla_warm = np.array([v for k,v in sorted(list(vanilla["warm"].items()), key= lambda t: t[0])])

        # cache_warm = np.array(list(cache["warm"].values()))
        # vanilla_cold = np.array(list(vanilla["cold"].values()))
        # vanilla_warm = np.array(list(vanilla["warm"].values()))

        ax1.barh(y=[1], left=np.cumsum(cache_cold) - cache_cold, width=cache_cold, height=[0.4], color=colors)
        bs = ax1.barh(y=[2], left=np.cumsum(vanilla_cold) - vanilla_cold, width=vanilla_cold, height=[0.4], color=colors)
        ax1.barh(y=[3], left=np.cumsum(cache_warm) - cache_warm, width=cache_warm, height=[0.4], color=colors)
        ax1.barh(y=[4], left=np.cumsum(vanilla_warm)-vanilla_warm, width=vanilla_warm, height=[0.4], color=colors)

        # fig.legend(bs, list(cache["cold"].keys()))
        ax1.set_yticks([])
        # ax1.set_yticks([1,2,3,4])
        # ax1.set_yticklabels(["FaasCache Cold", "OpenWhisk Cold", "FaasCache Warm", "OpenWhisk Warm"])
        # ax1.legend(bs, sorted(list(cache["cold"].keys())) + ["Dropped"], bbox_to_anchor=(-.5,1.3), ncol=len(cache["cold"].keys())+1, loc="upper left", columnspacing=1, fontsize='large')
        ax1.set_xlabel("Invocations")
        plt.savefig("../figs/litmus/faasbench_{}_cold_hot.pdf".format(gm_mem), bbox_inches="tight")

###########################################################
# Plot runs
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1])
test = "freq"
vanilla.append(litmi.loc[test,"vanilla_cold"] / (litmi.loc[test,"vanilla_cold"]+litmi.loc[test,"vanilla_warm"]))
cache.append(litmi.loc[test,"cache_cold"] / (litmi.loc[test,"cache_cold"]+litmi.loc[test,"cache_warm"]))

ax.bar(xs-0.1, vanilla, width=0.2, color='tab:blue', align='center', label="OpenWhisk")
ax.bar(xs+0.1, cache, width=0.2, color='tab:red', align='center', label="FaasCache")
ax.set_ylabel("% Cold Starts")
fig.legend()
plt.savefig("../figs/litmus/faasbench_freq.pdf", bbox_inches="tight")

###########################################################
# Plot Served
###########################################################
fig, ax = plt.subplots()
fig.set_size_inches(5,3)

vanilla = []
cache = []

xs = np.array([1, 2, 3])
ticks = ["freq"]
for test in ticks:
    vanilla.append(litmi.loc[test,"vanilla_cold"]+litmi.loc[test,"vanilla_warm"])
    cache.append(litmi.loc[test,"cache_cold"]+litmi.loc[test,"cache_warm"])

vanilla = np.array(vanilla)
cache = np.array(cache)

ax.bar(xs, cache/vanilla, width=0.2, color='tab:purple', align='center')
ax.set_xticks(xs)
ax.set_xticklabels([t[:-2] for t in ticks])
ax.set_xlabel("Litmus Test")
ax.set_ylabel("% Growth in Served Requests")
plt.savefig("../figs/litmus/faasbench_served.pdf", bbox_inches="tight")

###########################################################
# Plot Hot - Cold Per Function
###########################################################
fig, ax1 = plt.subplots()
fig.set_size_inches(5,3)

colors = ["firebrick", "goldenrod", "teal", "navy"]
vanilla = {
        "cold": {"DD": 1228, "Float": 1232, "CNN": 1395, "gzip":2529},
        "warm": {"DD": 178, "Float": 95, "CNN": 1395, "gzip":2529}
        }

cache = {
        "cold": {"DD": 1762, "Float": 1787, "CNN": 2048, "gzip":3585},
        "warm": {"DD": 290, "Float": 265, "CNN": 232, "gzip":4108}
        }

mx = max([sum([i for i in v.values()]) for v in vanilla.values()] + [sum([i for i in v.values()]) for v in cache.values()])
ax1.set_xlim(0, mx)

names = list(cache["cold"].keys())
cache_cold = np.array(list(cache["cold"].values()))
cache_warm = np.array(list(cache["warm"].values()))
vanilla_cold = np.array(list(vanilla["cold"].values()))
vanilla_warm = np.array(list(vanilla["warm"].values()))

bs = ax1.barh(y=["FaasCache Cold"], left=np.cumsum(cache_cold) - cache_cold, width=cache_cold, height=[0.4], color=colors)
xcenters = (np.cumsum(cache_cold)-cache_cold) + cache_cold / 2
for i, center in enumerate(xcenters):
    ax1.text(center, "FaasCache Cold", str(cache_cold[i]), ha='center', va='center', color="white")

ax1.barh(y=["FaasCache Warm"], left=np.cumsum(cache_warm) - cache_warm, width=cache_warm, height=[0.4], color=colors)
ax1.barh(y=["OpenWhisk Cold"], left=np.cumsum(vanilla_cold) - vanilla_cold, width=vanilla_cold, height=[0.4], color=colors)
ax1.barh(y=["OpenWhisk Warm"], left=np.cumsum(vanilla_warm)-vanilla_warm, width=vanilla_warm, height=[0.4], color=colors)

fig.legend(bs, names)
plt.savefig("../figs/litmus/faasbench_cold_hot.pdf", bbox_inches="tight")

###########################################################
# Plot Hot - Cold Per Function 4 GB
###########################################################

vanilla = {
        "cold": {"DD": 882, "Web": 938, "CNN": 993, "Float":1947},
        "warm": {"DD": 118, "Web": 63, "CNN": 173, "Float":1804}
        }

cache = {
        "cold": {"DD": 1413, "Web": 1464, "CNN": 1614, "Float":3049},
        "warm": {"DD": 206, "Web": 125, "CNN": 117, "Float":3021}
        }

plot(vanilla, cache, 4)

###########################################################
# Plot Execution Increase 4 GB
###########################################################
fig, ax1 = plt.subplots()
fig.set_size_inches(5,3)

colors = ["firebrick", "goldenrod", "teal", "navy"]

times = {"DD": (2.2806561470031737, 0.41934380531311033), "Web": (2.246276044845581, 0.281107234954834), "CNN": (6.193624019622803, 2.032859182357788), "Float":(1.9148462772369386, 0.2270068645477295)}

vanilla = {
        "cold": {"DD": 882, "Web": 938, "CNN": 993, "Float":1947},
        "warm": {"DD": 118, "Web": 63, "CNN": 173, "Float":1804}
        }

cache = {
        "cold": {"DD": 1413, "Web": 1464, "CNN": 1614, "Float":3049},
        "warm": {"DD": 206, "Web": 125, "CNN": 117, "Float":3021}
        }

out_dict = dict()  #BAD: We'll insert some global and some per-key stats
out_dict["global"] = dict()
total_accesses = 0 #for computing weighted averages 

for k in sorted(times.keys()):
        out_dict[k] = dict() 
        misses = vanilla["cold"][k]
        hits = vanilla["warm"][k]

        out_dict[k]["accesses"] = misses+hits 
        total_accesses += out_dict[k]["accesses"]

        trun = times[k][0]
        twarm = times[k][1]
        pct_incr = twarm*misses/((misses+hits)*(trun-twarm))
        out_dict[k]["pct_incr_vs_all_hits"] = pct_incr

increase = sum([out_dict[k]["pct_incr_vs_all_hits"]*out_dict[k]["accesses"]/total_accesses 
                        for k in sorted(times.keys())])

ax1.bar(x=0.3, height=increase, width=0.2, color='gold', align='center', label="OpenWhisk")

out_dict = dict()  #BAD: We'll insert some global and some per-key stats
out_dict["global"] = dict()
total_accesses = 0 #for computing weighted averages 

for k in sorted(times.keys()):
        out_dict[k] = dict() 
        misses = cache["cold"][k]
        hits = cache["warm"][k]

        out_dict[k]["accesses"] = misses+hits 
        total_accesses += out_dict[k]["accesses"]

        trun = times[k][0]
        twarm = times[k][1]
        pct_incr = twarm*misses/((misses+hits)*(trun-twarm))
        out_dict[k]["pct_incr_vs_all_hits"] = pct_incr

increase = sum([out_dict[k]["pct_incr_vs_all_hits"]*out_dict[k]["accesses"]/total_accesses 
                        for k in sorted(times.keys())])

ax1.bar(x=0, height=increase, width=0.2, color='Navy', align='center', label="FaasCache")
fig.legend()
plt.savefig("../figs/litmus/faasbench_4_exec_inc.pdf", bbox_inches="tight")

###########################################################
# Plot Hot - Cold Per Function 16 GB
###########################################################

vanilla = {
        "cold": {"DD": 671, "Web": 758, "CNN": 581, "Float":2008},
        "warm": {"DD": 250, "Web": 164, "CNN": 345, "Float":1447}
        }

cache = {
        "cold": {"DD": 325, "Web": 306, "CNN": 520, "Float":809},
        "warm": {"DD": 3460, "Web": 3479, "CNN": 3525, "Float":13384}
        }

plot(vanilla, cache, 16)

###########################################################
# Plot Hot - Cold Per Function 32 GB
###########################################################

vanilla = {
        "cold": {"DD": 1226, "Web": 1407, "CNN": 958, "Float":3588},
        "warm": {"DD": 766, "Web": 586, "CNN": 1067, "Float":3882}
        }

cache = {
        "cold": {"DD": 1386, "Web": 1417, "CNN": 1141, "Float":3447},
        "warm": {"DD": 806, "Web": 776, "CNN": 1057, "Float":4775}
        }

plot(vanilla, cache, 32)

###########################################################
# Plot Hot - Cold Per Function 48 GB
###########################################################

vanilla = {
        "cold": {"DD": 572, "Web": 624, "CNN": 608, "Float":1704},
        "warm": {"DD": 1384, "Web": 1333, "CNN": 1447, "Float":5632}
        }

cache = {
        "cold": {"DD": 9, "Web": 7, "CNN": 444, "Float":25},
        "warm": {"DD": 4791, "Web": 4793, "CNN": 4787, "Float":17975}
        }

plot(vanilla, cache, 48)

###########################################################
# Plot Hot - Cold Per Function 128 GB
###########################################################

vanilla = {
        "cold": {"DD": 23, "Web": 17, "CNN": 439, "Float":57},
        "warm": {"DD": 4777, "Web": 4783, "CNN": 4792, "Float":17943}
        }
cache = {
        "cold": {"DD": 3, "Web": 3, "CNN": 452, "Float":9},
        "warm": {"DD": 4797, "Web": 4797, "CNN": 4797, "Float":17991}
        }

# plot(vanilla, cache, 128)

###########################################################
# Plot Hot - Cold Per Function 64 GB
###########################################################

vanilla = {
        "cold": {"DD": 48, "Web": 33, "CNN": 448, "Float":85},
        "warm": {"DD": 4736, "Web": 4751, "CNN": 4758, "Float":17853}
        }
cache = {
        "cold": {"DD": 3, "Web": 3, "CNN": 461, "Float":11},
        "warm": {"DD": 4782, "Web": 4783, "CNN": 4774, "Float":17935}
        }

plot(vanilla, cache, 64)