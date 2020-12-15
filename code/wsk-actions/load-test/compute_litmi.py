import numpy as np
import pandas as pd
from random import shuffle
from math import ceil
from wsk_interact import *

num_to_pick = 100 #len(actions)
shuffle(actions)
sample_from = 5000

def get_frac_iat(iat):
    iats = np.array(iat)
    s = sum(iat)
    frac_iat = iats/s 
    reciprocal_iat = 1.0/frac_iat 
    recipsum = sum(reciprocal_iat)
    return reciprocal_iat/recipsum

def generate_trace(df, outfile):
    df = df.sample(num_to_pick)
    # print(df)
    bucket_only = df[buckets]
    milisec = 1000
    all_activations = []

    for hash_app, row in bucket_only.iterrows():
        mem = df.at[hash_app, "AverageAllocatedMb"]
        hot = df.at[hash_app, "percentile_Average_50"]
        cold = df.at[hash_app, "Maximum"]
        activate = []

        # index, row = row
        # sec = row[section]
        # action = actions[i]
        for minute, count in enumerate(row):
            count = int(count)
            if count <= 0:
                continue
            start = minute*60*milisec
            if count == 1:
                activate.append(start)
                continue
            every = milisec / count
            activate += [start + i*every for i in range(count)]
        activations = [(hash_app, time, mem, hot, cold) for time in activate]
        all_activations += activations

    df = pd.DataFrame.from_records(all_activations, columns=["action", "time", "mem", "hot_dur", "cold_dur"])
    df.sort_values(by="time", inplace=True)

    df.to_csv(outfile, index=False)

def divive_by_func_num(row):
    return ceil(row["AverageAllocatedMb"] / group_by_app[row["HashApp"]])

dur_fname = "/data2/azure/functions/function_durations_percentiles.anon.d01.csv"
mem_fname = "/data2/azure/functions/app_memory_percentiles.anon.d01.csv"
invoc_fname = "/data2/azure/functions/invocations_per_function_md.anon.d01.csv"
buckets = [str(i) for i in range(1, 1441)]


durations = pd.read_csv(dur_fname)
durations.index = durations["HashFunction"]
durations = durations.drop_duplicates("HashFunction")

group_by_app = durations.groupby("HashApp").size()

invocations = pd.read_csv(invoc_fname)
invocations = invocations.dropna()
invocations.index = invocations["HashFunction"]
invocations = invocations.drop_duplicates("HashFunction")
sums = invocations[buckets].sum(axis=1)
invocations = invocations[sums > 1] # action must be invoked at least twice

joined = invocations.join(durations, how="inner", lsuffix='', rsuffix='_durs')

memory = pd.read_csv(mem_fname)
memory = memory.drop_duplicates("HashApp")
memory.index = memory["HashApp"]

new_mem = memory.apply(divive_by_func_num, axis=1, raw=False, result_type='expand')
memory["divvied"] = new_mem

master = joined.join(memory, how="inner", on="HashApp", lsuffix='', rsuffix='_mems')

# # section = [i for i in range(600, 661)]
# columns = ["HashOwner","HashApp","HashFunction","Trigger"]
# columns += buckets
# master = pd.read_csv(invoc_fname)
# # master = master.drop_duplicates(subset=["HashApp"], keep="last")
# master.index = master["HashFunction"]

# mem_df = pd.read_csv(mem_fname, dtype={"HashApp": str})
# mem_df = mem_df.dropna()
# mem_df["HashApp"] = mem_df["HashApp"].astype(str)
# print(mem_df.dtypes)
# # mem_df.index = mem_df["HashFunction"]
# master = master.join(mem_df, on="HashApp", how='inner', lsuffix='', rsuffix='_mem')

# dur_df = pd.read_csv(dur_fname)
# dur_df.index = dur_df["HashFunction"]
# master = master.join(dur_df, how='inner', lsuffix='', rsuffix='_dur')

# sums = master[buckets].sum(axis=1)
# master = master[sums > 2]

#################################################################################################################
#                                       Overlap litmus                                                          #
#################################################################################################################

def gen_overlap():
    overlap = master.copy()#.sample(sample_from)

    def count_times(row):
        row = row[4:]
        window = np.array([i for i in range(11)]) # window is > 10 minutes long
        count = 0
        while window[-1] < 1440:
            if np.sum(row[window] >= 1) > 1:
                count += 1
            window += 1
        return count

    overlap2 = overlap.apply(count_times, axis=1, raw=True, result_type="expand")
    print("\n\noverlap done\n\n")
    return "overlap", overlap2

#################################################################################################################
#                                       Wellford litmus                                                         #
#################################################################################################################

# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
# For a new value newValue, compute the new count, new mean, the new M2.
# mean accumulates the mean of the entire dataset
# M2 aggregates the squared distance from the mean
# count aggregates the number of samples seen so far
def well_update(existingAggregate, newValue):
    (count, mean, M2) = existingAggregate
    count += 1
    delta = newValue - mean
    mean += delta / count
    delta2 = newValue - mean
    M2 += delta * delta2

    return (count, mean, M2)

# Retrieve the mean, variance and sample variance from an aggregate
def well_finalize(existingAggregate):
    (count, mean, M2) = existingAggregate
    if count < 2:
        return float('nan'), float('nan'), float('nan')
    else:
        (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
    return (mean, variance, sampleVariance)

def gen_well():
    well = master[buckets]
    wellford = dict() # func-name : aggregate

    milisec = 1000
    for (index, counts) in well.iterrows():
        wellford[index] = (0,0,0)

        for minute, count in enumerate(counts):
            count = int(count)
            if count <= 0:
                continue
            start = minute*60*milisec
            if count == 1:
                wellford[index] = well_update(wellford[index], start)
                continue
            every = milisec / count
            for i in range(count):
                wellford[index] = well_update(wellford[index], start + i*every)

    data = []
    idxs = []
    for key, value in wellford.items():
        mean, variance, sampleVariance = well_finalize(value)
        if variance != 0:
            data.append(mean / variance)
        else:
            data.append(0)
        idxs.append(key)    
            
    cv_df = pd.Series(data, idxs)
    print("\n\nwell done\n\n")
    return "CV", cv_df

#################################################################################################################
#                                       Sum litmus                                                          #
#################################################################################################################

def gen_sum():
    s = master[buckets]

    sums = s.sum(axis=1)
    print("\nsums done\n")
    return "sums", sums

#################################################################################################################
#                                       IAT litmus                                                          #
#################################################################################################################

def gen_iat():
    buks = master[buckets]
    milisec = 1000
    iats = dict()  # func-name : aggregate
    for (index, counts) in buks.iterrows():
        iats[index] = list()
        last = 0
        for minute, count in enumerate(counts):
            count = int(count)
            if count <= 0:
                continue
            start = minute * 60 * milisec
            if count == 1:
                now = start
                iats[index].append(now - last)
                last = now
                continue
            every = milisec / count
            for i in range(count):
                now = start + i * every
                iats[index].append(now - last)
                last = now
    
    data = []
    idxs = []
    for key, iat_list in iats.items():
        data.append(sum(iat_list) / len(iat_list))
        idxs.append(key)
        # avgs.append((key, sum(iat_list) / len(iat_list)))
    # print(avgs)
    iat_df = pd.Series(data, idxs)
    print("\n\niat done\n\n")
    return "iat", iat_df

#################################################################################################################
# Run #
#################################################################################################################
from multiprocessing import Pool

# t = gen_iat()
# print(t[1])

procs = [gen_sum, gen_overlap, gen_well, gen_iat]

results = []
with Pool(processes=len(procs)) as pool:
    for p in procs:
        result = pool.apply_async(p)
        results.append(result)
    results = results[::-1]
    [result.wait() for result in results]

for result in results:
    column, data = result.get()
    print(type(data))
    master[column] = data
    # master = master.join(data, how='inner', lsuffix='', rsuffix="_"+column)
    # master[column] = data

master.to_csv("./added_columns.csv", index=False)