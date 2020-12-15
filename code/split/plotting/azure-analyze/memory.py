import pandas as pd
import os
from math import ceil

memory = "/data2/alfuerst/azure/functions/app_memory_percentiles.anon.d01.csv"
durations = "/data2/alfuerst/azure/functions/function_durations_percentiles.anon.d01.csv"
durations = pd.read_csv(durations)
group_by_app = durations.groupby("HashApp").size()

# print(group_by_app)

def divive_by_func_num(row):
    print(row["AverageAllocatedMb"], group_by_app[row["HashApp"]], row["AverageAllocatedMb"] / group_by_app[row["HashApp"]])
    return ceil(row["AverageAllocatedMb"] / group_by_app[row["HashApp"]])

memory = pd.read_csv(memory)
memory.index = memory["HashApp"]
new_mem = memory.apply(divive_by_func_num, axis=1, raw=False, result_type='expand')

# print(new_mem)
