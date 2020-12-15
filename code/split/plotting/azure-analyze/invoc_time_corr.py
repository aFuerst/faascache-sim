import pandas as pd
import numpy as np
import os

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

datapath = "/data2/alfuerst/azure/functions"
dur_names = "function_durations_percentiles.anon.d{0:02d}.csv"

invoc_names = "invocations_per_function_md.anon.d{0:02d}.csv"
buckets = [str(i) for i in range(1, 1441)]
columns = ["HashOwner","HashApp","HashFunction","Trigger"] + buckets

mem_columns = ["owner", "HashApp", "count", "averagealloc", "averagealloc_pct1", "averagealloc_pct5", "averagealloc_pct25", "averagealloc_pct50", "averagealloc_pct75", "averagealloc_pct95", "averagealloc_pct99", "averagealloc_pct100"]
fnames = "app_memory_percentiles.anon.d{0:02d}.csv"

for i in range(1, 13):
    file = os.path.join(datapath, dur_names.format(i))
    dur_df = pd.read_csv(file, index_col="HashFunction")

    file = os.path.join(datapath, invoc_names.format(i))
    invoc_df = pd.read_csv(file, names=columns, skiprows=1, index_col="HashFunction")

    # dur_index = pd.Series(dur_df.index)
    # invoc_index = pd.Series(invoc_df.index)

    sampled = invoc_df[buckets]
    sums = sampled.sum(axis=1)

    dur = dur_df[["Average"]]

    combined = dur.assign(Invocations=sums)
    combined = combined.dropna()
    corr = combined.corr()
    print("invoc - dur\n", corr, corr.iloc[0,1], type(corr))

    fig1, ax1 = plot.subplots(figsize=figsize)
    ax1.set_ylabel("Invocations")
    ax1.set_xlabel("Avg Execution Time (sec)")
    ax1.scatter(y=combined["Invocations"], x=combined["Average"]/1000, label="Scatter")
    x_vals = np.array(ax1.get_xlim())
    y_vals = corr.iloc[0,1] * x_vals
    print(x_vals, y_vals)
    ax1.plot(x_vals, y_vals, 'r--', label="Correlation")
    # ax1.plot(corr, "r+", label="Correlation")
    ax1.legend()
    save_plot("test.png")

    # file = os.path.join(datapath, dur_names.format(i))
    # dur_df = pd.read_csv(file, index_col="HashApp")

    # file = os.path.join(datapath, invoc_names.format(i))
    # invoc_df = pd.read_csv(file, names=columns, skiprows=1, index_col="HashApp")

    # file = os.path.join(datapath, fnames.format(i))
    # mem_df = pd.read_csv(file, names=mem_columns, skiprows=1, index_col="HashApp")

    # # dur_index = pd.Series(dur_df.index)
    # # invoc_index = pd.Series(invoc_df.index)
    # # mem_index = pd.Series(mem_df.index)

    # sampled = invoc_df[buckets]
    # sums = sampled.sum(axis=1)
    # print(sums)
    # mem = mem_df[["averagealloc"]]

    # combined = mem.assign(Invocations=sums)
    # combined = combined.dropna()
    # print("invoc - mem", combined.corr())

    # dur = dur_df[["Average"]]

    # combined = dur.assign(Invocations=mem)
    # combined = combined.dropna()
    # print("mem - dur", combined.corr(), "\n")
    break