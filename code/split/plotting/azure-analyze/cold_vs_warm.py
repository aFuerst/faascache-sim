import pandas as pd
import numpy as np
import os

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot
plot.rc('font', size=14)

figsize = (5.5,3.6) # (6.4, 4.8)
def save_plot(path):
    if os.path.isfile(path):
        os.remove(path)
    plot.savefig(path, bbox_inches="tight")

datapath = "/extra/alfuerst/azure/functions/"
fnames = "function_durations_percentiles.anon.d{0:02d}.csv"
columns = ["HashOwner","HashApp","HashFunction","Average", "Count", "Minimum", "Maximum", "percentile_Average_0", "percentile_Average_1", "percentile_Average_25", "percentile_Average_50", "percentile_Average_75", "percentile_Average_99", "percentile_Average_100"]

for i in range(1, 7):
    file = os.path.join(datapath, fnames.format(i))
    df = pd.read_csv(file, names=columns, skiprows=1)
    # df.index = df["HashFunction"]

    proportion = df["percentile_Average_50"] / df["Maximum"]
    proportion = proportion.dropna()

    avg = df["Average"] / df["Maximum"]
    avg = avg[avg > 0]
    avg = avg.dropna()

    minimum = df["Minimum"] / df["Maximum"]
    minimum = minimum.dropna()


    min_avg = df["Minimum"] / df["Average"]
    min_avg = min_avg.dropna()
    min_avg = min_avg[min_avg > 0]

    fig1, ax1 = plot.subplots(figsize=figsize)
    ax1.set_ylabel("% of maximum")
    # ax1.set_xlabel("Avg Execution Time (sec)")
    # ax1.plot(df["percentile_Average_50"], label="percentile_Average_50")
    # ax1.plot(df["Maximum"], label="Maximum")
    # boxes = []
    colors = ["tab:blue", "tab:red", "tab:olive", "tab:brown"]
    bp = ax1.boxplot([proportion, minimum, avg], labels=["percentile_Average_50", "Minimum", "Average"], positions=[0, 4, 8],  patch_artist=True, showfliers=False)
    for i, patch in enumerate(bp["boxes"]):
        patch.set(facecolor=colors[i])

    save_plot("../../figs/cold_vs_warm.pdf")
    plot.clf()

    #############################################################################

    minute = df[df["Average"] <= 30000]
    minute = minute[minute["Average"] > 0]
    minute = minute[minute["Maximum"] <= 30000]
    minute = minute[minute["Maximum"] > 0]
    fig1, ax1 = plot.subplots(figsize=figsize)
    ax1.set_ylabel("Average")
    ax1.set_xlabel("Maximum")
    ax1.scatter(y=minute["Average"], x=minute["Maximum"], label="Scatter")

    save_plot("../../figs/scatter_cold_vs_warm.pdf")
    plot.clf()

    #############################################################################
    minute = df[df["Average"] <= 30000]
    minute = minute[minute["Average"] > 0]
    minute = minute[minute["Maximum"] <= 30000]
    minute = minute[minute["Maximum"] > 0]

    fig1, ax1 = plot.subplots(figsize=figsize)
    # heatmap, xedges, yedges = np.histogram2d(minute["Maximum"], minute["Average"], bins=10)
    # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # ax1.imshow(heatmap.T, extent=extent, origin='lower')
    
    ax1.hexbin(minute["Maximum"], minute["Average"], mincnt=1, bins=50)

    # ax1.scatter(y=minute["Average"], x=minute["Maximum"], label="Scatter")
    ax1.set_ylabel("Average")
    ax1.set_xlabel("Maximum")
    save_plot("../../figs/heatmap_cold_vs_warm.pdf")

    #############################################################################

    minute = df[df["Average"] <= 500]
    minute = minute[minute["Average"] > 0]
    minute = minute[minute["Maximum"] <= 500]
    minute = minute[minute["Maximum"] > 0]

    fig1, ax1 = plot.subplots(figsize=figsize)
    # heatmap, xedges, yedges = np.histogram2d(minute["Maximum"], minute["Average"], bins=10)
    # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # ax1.imshow(heatmap.T, extent=extent, origin='lower')
    
    ax1.hexbin(minute["Maximum"], minute["Average"], mincnt=1, bins=50)

    # ax1.scatter(y=minute["Average"], x=minute["Maximum"], label="Scatter")
    ax1.set_ylabel("Average")
    ax1.set_xlabel("Maximum")
    save_plot("../../figs/heatmap_short_cold_vs_warm.pdf")
    break