import numpy as np
import pandas as pd
from random import shuffle

from wsk_interact import *

ids = ["216527e7d6aade91cd782570ba7bd97ffae5a65a514c0f10ee60c43f065160f4", "7f666388a99f37d762a617e1ad0ff34052832f98f16ac608422a37443f0c55dc", "710aae40a6f4f4e115517ff638792b8de0e50edd4ae8142be7f3ec7875e96200", "daf566a6e6a5a946d5310511f9910e2709991a56f01fbc3746d4689a98900e52", "eba44b7e5832d7ade1322f468d29c229e75fff94039fcbdeb1ef77bafbf3436b", "19c81049ad684057f5742dbd62b7f079b9315da24fc7bca6ffbb2cb10006518d", "2f720baf4f6fe0d87af030eec1c9d418aae2d79a9b7c0baf04779a9fd49ed8cb", "9c8658fdac33b1870843717be6a24ecfadd743bac562bc9eb4348b6125ecacae", "f1658eb4f7752c0ebfb0858c239c22406f88a0673bdf1f496d05dc1bdb1859df", "f0691eff17c0ce93beba17c78e3b2670b5d8c65a9724ce03aab5c7b27fcdd565", "1c002389c5b2896975a8d9e42b0ea4f3d799cb8e05fc67075611fe04a61ba6fc", "f84f4a00b22df32d5850fad776e7da0400d0cd3c8e0ddd24c31bbab3a2b73df8"]
# reqs_per_sec = shuffle(reqs_per_sec)
shuffle(actions)
# ids = shuffle(ids)

file = "/data2/alfuerst/azure/functions/invocations_per_function_md.anon.d01.csv"
buckets = [str(i) for i in range(1, 1441)]
section = [i for i in range(600, 661)]
columns = ["HashOwner","HashApp","HashFunction","Trigger"]
columns += buckets
df = pd.read_csv(file)
# df.index = df["HashFunction"]

milisec = 1000

matching = df[df["HashFunction"].isin(ids)]
# print(matching)
all_activations = []

for i, row in enumerate(matching.iterrows()):
    activate = []

    index, row = row
    sec = row[section]
    # print(sec.sum())
    action = actions[i]
    # print(action)
    for minute, count in enumerate(sec):
        count = int(count)
        if count <= 0:
            continue
        start = minute#*milisec
        if count == 1:
            activate.append(start)
            continue
        every = milisec / count
        activate += [start + i*every for i in range(count)]
    # print(len(activate), activate)
    activations = [(time, action) for time in activate]
    # print(activations)
    all_activations += activations

df = pd.DataFrame.from_records(all_activations, columns=["time", "action"])
df.sort_values(by="time", inplace=True)

df.to_csv("./load_trace.csv", index=False)