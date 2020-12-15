import pandas as pd
import os

datapath = "/data2/alfuerst/azure/functions"
fnames = "invocations_per_function_md.anon.d01.csv"
trigger = "http"
timer = "timer"
buckets = [str(i) for i in range(1, 1441)]
buckets = [str(i) for i in range(600, 661)]
columns = ["HashOwner","HashApp","HashFunction","Trigger"]

columns += buckets

file = os.path.join(datapath, fnames)
df = pd.read_csv(file)
df.index = df["HashFunction"]
counts = df[buckets]
# print(counts.describe())
sums = counts.sum(axis=1)

counts = df[buckets]

sums = counts.sum(axis=1)
counts = counts[sums > 1] # action must be invoked at least twice
sums = counts.sum(axis=1)
# print("\n\n", counts.index, "\n\n")


sums.index = counts.index
# print(counts.describe())
# print(sums.describe())
# sums = sums / 60
sums = sums[sums >= 4.0]
samples = sums.sample(12)
# print(samples)

# print(sums.quantile([0.125, 0.25, 0.5, 0.75, 0.8, 0.9, 0.95]))

lims = sums.quantile([0, 0.25, 0.5, 0.75, 1.0])
print(lims, lims[0], lims[1])

bottom = sums[sums.between(lims[0], lims[.25], inclusive=True)]
print(bottom.sample(4))
bottom = sums[sums.between(lims[.25], lims[.5], inclusive=False)]
print(bottom.sample(4))
bottom = sums[sums.between(lims[.5], lims[.75], inclusive=False)]
print(bottom.sample(4))
bottom = sums[sums.between(lims[.75], lims[1], inclusive=False)]
print(bottom.sample(4))