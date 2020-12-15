import numpy as np
import pandas as pd
import os

import matplotlib as mpl
mpl.rcParams.update({'font.size': 14})
mpl.use('Agg')
import matplotlib.pyplot as plt

buckets = [str(i) for i in range(1, 1441)]
datapath = "/extra/alfuerst/azure/functions/"
invocations = "invocations_per_function_md.anon.d01.csv"
file = os.path.join(datapath, invocations)

invocations = pd.read_csv(file)
invocations = invocations.dropna()
invocations.index = invocations["HashFunction"]
sums = invocations.sum(axis=1)
invocations = invocations[sums > 1] # action must be invoked at least twice
invocations = invocations.drop_duplicates("HashFunction")
sums = invocations[buckets].sum(axis=0)
# print(sums)
# print(sums.columns)

fig, ax1 = plt.subplots()
fig.set_size_inches(5,3)
ax1.plot(sums.to_numpy())
plt.savefig("../figs/whole_trace.pdf", bbox_inches="tight")
