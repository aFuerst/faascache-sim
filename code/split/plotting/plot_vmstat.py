import pandas as pd
from datetime import datetime, timedelta
import os
cols = ['r', 'b', 'swpd', 'free', 'buff', 'cache', 'si', 'so', 'bi', 'bo', 'in', 'cs', 'us', 'sy', 'id', 'wa', 'st', "day", "timestamp"]

files = ["cach_sub_128_gb_vmstat_log.txt", "vanil_sub_128_gb_vmstat_log.txt", "cach_sub_64_gb_vmstat_log.txt",
     "vanil_sub_64_gb_vmstat_log.txt", "cach_sub_32_gb_vmstat_log.txt", "vanil_sub_32_gb_vmstat_log.txt",
     "cach_sub_48_gb_vmstat_log.txt", "vanil_sub_48_gb_vmstat_log.txt"]

for file in files:
    pth = os.path.join("/home/alfuerst/vmstats/", file)

    df = pd.read_csv(pth, names=cols, skiprows=2, parse_dates=True, sep="\s+", skipinitialspace=True)

    fmt = "%Y-%m-%d %H:%M:%S"
    df["time"] = (df["day"] + " " + df["timestamp"]).apply(datetime.strptime, args=(fmt,))

    cut = df[df["time"] <= df.at[0, "time"] + timedelta(0, 0, 0, 0, 20, 2)]
    # print(len(df), len(cut))
    cpu = cut["us"] + cut["sy"] + cut["wa"]
    print(file, cpu.mean())
