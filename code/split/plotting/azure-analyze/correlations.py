import pandas as pd
import numpy as np
import os
from math import ceil

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot
plot.rc('font', size=14)

figsize = (5.5,3.6) # (6.4, 4.8)
show_fliers=False

def save_plot(path):
    if os.path.isfile(path):
        os.remove(path)
    plot.savefig(path, bbox_inches="tight")

def divive_by_func_num(row):
    return ceil(row["AverageAllocatedMb"] / durs_group_by_app[row["HashApp"]])

dur_pth = "/extra/alfuerst/azure/functions/function_durations_percentiles.anon.d01.csv"

invoc_pth = "/extra/alfuerst/azure/functions/invocations_per_function_md.anon.d01.csv"
buckets = [str(i) for i in range(1, 1441)]
columns = ["HashOwner","HashApp","HashFunction","Trigger"] + buckets

mem_pth = "/extra/alfuerst/azure/functions/app_memory_percentiles.anon.d01.csv"

dur_df = pd.read_csv(dur_pth)
dur_df.index = dur_df["HashFunction"]
dur_df = dur_df.dropna()
durs_group_by_app = dur_df.groupby("HashApp").size()

invoc_df = pd.read_csv(invoc_pth)
invoc_df.index = invoc_df["HashFunction"]
invoc_df = invoc_df.dropna()

mem_df = pd.read_csv(mem_pth)
mem_df.index = mem_df["HashApp"]
new_mem = mem_df.apply(divive_by_func_num, axis=1, raw=False, result_type='expand')
mem_df["divvied"] = new_mem
# mem_df = mem_df.dropna()

invoc_df["sums"] = invoc_df[buckets].sum(axis=1)

joined = invoc_df.join(mem_df, on="HashApp", how="left", lsuffix='', rsuffix='_mems')
joined = joined.replace([np.inf, -np.inf], np.nan)
joined = joined.dropna()
joined = joined[joined["sums"] > 0]

fig1, ax1 = plot.subplots(figsize=figsize)
ax1.set_ylabel("Memory Usage (MB)")
ax1.set_xlabel("Invocations")

ax1.hist2d(x=joined["sums"], y=joined["divvied"], bins=100, normed=False, cmap='plasma')

ax1.set_xscale('log')
ax1.set_ylim((0,200))
ax1.set_xlim((1,10**6))
save_plot("../../figs/mem-conv-corr.png")

####################################################################################################

joined = dur_df.join(mem_df, on="HashApp", how="left", lsuffix='', rsuffix='_mems')
joined = joined[joined["Average"] > 0]

joined = joined.replace([np.inf, -np.inf], np.nan)
joined = joined.dropna()

fig1, ax1 = plot.subplots(figsize=figsize)
ax1.set_ylabel("Memory Usage (MB)")
ax1.set_xlabel("Average execution time (ms)")
# ax1.scatter(x=joined["Average"], y=joined["divvied"], label="Scatter")

ax1.hist2d(x=joined["Average"], y=joined["divvied"], bins=100, normed=False, cmap='plasma')
ax1.set_ylim((0,200))
ax1.set_xlim((0,60*1000))
# reg = np.polyfit(x=joined["Average"], y=joined["divvied"], deg=1)
# two = joined[["divvied", "Average"]]

# # print(two.corr())
# # print(reg)
# ax1.set_xlim(left=0)
# ticks = ax1.get_xticks()
# x = ticks[:-2]
# y = reg[0] * x + reg[1]
# # print(x, y)
# ax1.plot(x, y, color="red")

# ax1.legend()
save_plot("../../figs/mem-dur-corr.png")