import pandas as pd
import os

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot
plot.rc('font', size=14)

figsize = (5.5,3.6) # (6.4, 4.8)

datapath = "/data2/alfuerst/azure/functions"
fnames = "invocations_per_function_md.anon.d{0:02d}.csv"
trigger = "http"
timer = "timer"
buckets = [str(i) for i in range(1, 1441)]
columns = ["HashOwner","HashApp","HashFunction","Trigger"]

columns += buckets

for i in range(1, 7):
    file = os.path.join(datapath, fnames.format(i))
    df = pd.read_csv(file, names=columns, skiprows=1)
    # http = df[df["Trigger"] != timer]
    # sampled = http.sample(12, random_state=0)
    # print(sampled.describe())
    # print(sampled.columns)
    counts = df[buckets]
    sums = counts.sum(axis=1)

    counts = df[buckets]
    sums = counts.sum(axis=0)

    fig1, ax1 = plot.subplots(figsize=figsize)
    ax1.set_ylabel("Invocations")
    ax1.set_xlabel("Time")
    ax1.plot([i for i in range(1, 1441)], sums, label="Invocations")
    # ax1.plot(corr, "r+", label="Correlation")
    ax1.legend()
    if os.path.isfile("invoc.png"):
        os.remove("invoc.png")
    plot.savefig("invoc.png", bbox_inches="tight")

    sums = counts.sum(axis=1)
    sums = sums / 1440
    sums = sums[sums >= (1/300)]
    samples = sums[sums > 0.1].sample(12)
    print(samples.values)
    # print(sampled.sum())
    # print(sums.describe())
    print(sums.quantile([0.25, 0.5, 0.75, 0.8, 0.9, 0.95]))
    print(sums.quantile([0.25, 0.5, 0.75, 0.8, 0.9, 0.95])/1440, "\n")
    # mamny = sums[(sums/1440) >= 1]
    # print(mamny)

    # print(sampled.describe())
    # for sample in sampled.itertuples(index=False):
    #     # print(sampled.columns)
    #     # print(sample, sum(sample))
    #     print(sum(sample), sum(sample)/1440)
    #     # break
    break