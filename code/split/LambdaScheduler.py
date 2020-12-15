import pandas as pd
import numpy as np
import scipy.stats as stats
from math import floor, isnan
import random
import heapq
from collections import defaultdict
from LambdaData import *
from Container import *
from TraceGen import *
from time import sleep
import os

class LambdaScheduler:

    hist_num_cols = [i for i in range(4*60)]

    def __init__(self, policy:str="GD", mem_capacity:int=32000, num_funcs:int=10, run:str="a", log_dir=""):
        # log_dir = "/data2/alfuerst/azure/functions/trace_pckl/middle/logs/"
        fname = "{}-{}-{}-{}-".format(policy, num_funcs, mem_capacity, run)

        self.mem_capacity = mem_capacity
        self.mem_used = 0
        self.eviction_policy = policy
        self.Clock = 0
        self.wall_time = 0
        self.finish_times = []
        self.running_c = dict()
        self.ContainerPool = []

        self.PerfLogFName = os.path.join(log_dir, fname+"performancelog.csv")
        self.PerformanceLog = open(self.PerfLogFName, "w")
        self.PerformanceLog.write("lambda,time,meta\n")

        self.MemUsageFname = os.path.join(log_dir, fname+"memusagehist.csv")
        self.MemUsageHist = open(self.MemUsageFname, "w")
        self.MemUsageHist.write("time,reason,mem_used,mem_size,extra\n")

        self.PureCacheFname = os.path.join(log_dir, fname+"purecachehist.csv")
        self.PureCacheHist = open(self.PureCacheFname, "w")
        self.PureCacheHist.write("time,used_mem,running_mem,pure_cache\n")

        self.evdict = defaultdict(int)
        self.capacity_misses = defaultdict(int)
        self.TTL = 10 * 60 * 1000  # 10 minutes in ms
        self.Long_TTL = 2 * 60 * 60 * 1000  # 2 hours in ms

        self.IT_histogram = dict()
        self.last_seen = dict() # func-name : last seen time
        self.wellford = dict() # func-name : aggregate
        self.histTTL = dict() # func-name : time to live
        self.histPrewarm = dict() # func-name : prewarm time
        self.rep = dict() # func-name : LambdaData; used to prewarm containers

        heapq.heapify(self.ContainerPool)

    ##############################################################

    def WriteMemLog(self, reason, wall_time, mem_used, mem_size, extra="N/A"):
        msg = "{},{},{},{},{}\n".format(wall_time, reason, mem_used, mem_size, str(extra))
        self.MemUsageHist.write(msg)

    ##############################################################

    def WritePerfLog(self, d:LambdaData, time, meta):
        msg = "{},{},{}\n".format(d.kind, time, meta)
        self.PerformanceLog.write(msg)

    ##############################################################

    def WritePureCacheHist(self, time):
        # time, used_mem, running_mem, pure_cache
        running_mem = sum([k.metadata.mem_size for k in self.running_c.keys()])
        pure_cache = self.mem_used - running_mem
        if pure_cache < 0:
          raise Exception("Impossible pure_cache allocation: {}".format(pure_cache))
        msg = "{},{},{},{}\n".format(time, self.mem_used, running_mem, pure_cache)
        self.PureCacheHist.write(msg)


    ##############################################################

    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
    # For a new value newValue, compute the new count, new mean, the new M2.
    # mean accumulates the mean of the entire dataset
    # M2 aggregates the squared distance from the mean
    # count aggregates the number of samples seen so far
    def well_update(self, existingAggregate, newValue):
        (count, mean, M2) = existingAggregate
        count += 1
        delta = newValue - mean
        mean += delta / count
        delta2 = newValue - mean
        M2 += delta * delta2

        return (count, mean, M2)

    # Retrieve the mean, variance and sample variance from an aggregate
    def well_finalize(self, existingAggregate):
        (count, mean, M2) = existingAggregate
        if count < 2:
            return float('nan'), float('nan'), float('nan')
        else:
            (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
        return (mean, variance, sampleVariance)

    ##############################################################

    def _find_precentile(self, cdf, percent, head=False):
        """ Returns the last whole bucket (minute) before the percentile """
        for i, value in enumerate(cdf):
            if percent < value:
                if head:
                    return max(0, i-1)
                else:
                    return min(i+1, len(cdf))
        return len(cdf)

    def track_activation(self, d: LambdaData):
        if self.eviction_policy != "HIST":
            return

        four_hours_in_mins = 4*60
        t = self.wall_time
        if d.kind in self.last_seen:
            IAT = self.wall_time - self.last_seen[d.kind]
        self.last_seen[d.kind] = t

        if not d.kind in self.IT_histogram:
            # never lambda seen before
            self.rep[d.kind] = d

            self.IT_histogram[d.kind] = np.zeros(four_hours_in_mins)
            self.wellford[d.kind] = (0,0,0)
            # default TTL is 2 hours in miliseconds
            self.histTTL[d.kind] = 2 * 60 * 60 * 1000
            self.histPrewarm[d.kind] = 0
            return

        minute = floor(IAT / (60*1000))
        if minute >= four_hours_in_mins:
            # don't track IAT over 4 hours
            return

        self.wellford[d.kind] = self.well_update(self.wellford[d.kind], minute)
        self.IT_histogram[d.kind][minute] += 1
        mean, variance, sampleVariance = self.well_finalize(self.wellford[d.kind])
        if not isnan(mean):
            data = self.IT_histogram[d.kind]
            cdf = np.cumsum(data / data.sum())
            head = self._find_precentile(cdf, 0.05, head=True)
            tail = self._find_precentile(cdf, 0.99)


            if mean == 0 or variance / mean <= 2:
                self.histTTL[d.kind] = tail * 60 * 1000     * 1.1 # 10% increase margin
                self.histPrewarm[d.kind] = head * 60 * 1000 * 0.9 # 10% decrease margin
            else:
                # default TTL is 2 hours in miliseconds
                self.histTTL[d.kind] = 2 * 60 * 60 * 1000
                self.histPrewarm[d.kind] = 0 # default to not unload
        else:
            # default TTL is 2 hours in miliseconds
            self.histTTL[d.kind] = 2 * 60 * 60 * 1000
            self.histPrewarm[d.kind] = 0 # default to not unload

    ##############################################################

    def PurgeOldHist(self, container_list):
        """ Return list of still usable containers after purging those older than TTL """
        kill_list = [c for c in container_list
                     if c.last_access_t + self.histTTL[c.metadata.kind] < self.wall_time]

        for k in kill_list:
            self.RemoveFromPool(k, "HIST-TTL-purge")
            kind = k.metadata.kind
            self.evdict[kind] += 1

        #This is just the inverse of kill_list. Crummy way to do this, but YOLO
        valid_containers = [c for c in container_list
                     if c.last_access_t + self.histTTL[c.metadata.kind] >= self.wall_time]

        return valid_containers

    ##############################################################

    def PreWarmContainers(self):
        """Warm containers before incoming activation to mimic it happening at the actual time """
        if self.eviction_policy != "HIST":
            return
        to_warm = [kind for kind, prewarm in self.histPrewarm.items() if prewarm != 0 and prewarm + self.last_seen[kind] >= self.wall_time]
        for kind in to_warm:
            c = Container(self.rep[kind])
            at = self.histPrewarm[kind] + self.last_seen[kind]
            at = min(at, self.wall_time)
            self.AddToPool(c=c, prewarm=True, at_time=at)

    ##############################################################

    def find_container(self, d: LambdaData):
        """ search through the containerpool for matching container """
        if len(self.ContainerPool) == 0 :
            return None
        containers_for_the_lambda = [x for x in self.ContainerPool if (x.metadata == d and
                                                     x not in self.running_c)]
        #for const-ttl, filter here, and remove.
        if self.eviction_policy == "TTL" and containers_for_the_lambda != []:
            #All the old containers, get rid of them
            fresh_containers = self.PurgeOldTTL(containers_for_the_lambda) # This also deletes the containers from containerpool
            containers_for_the_lambda = fresh_containers

        if self.eviction_policy == "LONG-TTL" and containers_for_the_lambda != []:
            #All the old containers, get rid of them
            fresh_containers = self.PurgeOldLongTTL(containers_for_the_lambda) # This also deletes the containers from containerpool
            containers_for_the_lambda = fresh_containers

        if self.eviction_policy == "HIST" and containers_for_the_lambda != []:
            fresh_containers = self.PurgeOldHist(containers_for_the_lambda) # This also deletes the containers from containerpool
            containers_for_the_lambda = fresh_containers

        if containers_for_the_lambda == []:
            return None
        else:
            return containers_for_the_lambda[0]
        #Just return the first element.
        #Later on, maybe sort by something? Priority? TTL ?

    ##############################################################

    def pool_stats(self):
        pool = self.ContainerPool #Is a heap
        sdict = defaultdict(int)
        for c in pool:
            k = c.metadata.kind
            sdict[k] += 1

        return sdict

    ##############################################################

    def container_clones(self, c):
        return [x for x in self.ContainerPool if x.metadata == c.metadata]

    ##############################################################

    def calc_priority(self, c, update=False):
        """ GD prio calculation as per eq 1 .
        If update==True, then dont replace the clock value. 
        Modifies insert_clock container state. 
        """

        #It makes sense to have per-container clock instead of per-function.
        #The "oldest" container of the function will be evicted first

        if not update:
            clock = self.Clock
        else:
            clock = c.insert_clock

        prio = c.last_access_t

        if self.eviction_policy == "GD":
            freq = sum([x.frequency for x in self.container_clones(c)])
            #freq shoud be of all containers for this lambda actiion, not just this one...
            cost = float(c.metadata.run_time - c.metadata.warm_time)  # run_time - warm_time, or just warm_time , or warm/run_time
            size = c.metadata.mem_size
            prio = clock + freq*(cost/size)

        elif self.eviction_policy == "LND":
            # For now, assume this is called only on accesses.
            cost = c.metadata.warm_time # can also be R - W  time
            prio = cost

        elif self.eviction_policy == "FREQ":
            freq = sum([x.frequency for x in self.container_clones(c)])
            cost = float(c.metadata.run_time - c.metadata.warm_time)  # run_time - warm_time, or just warm_time , or warm/run_time
            prio = clock + freq*cost
        elif self.eviction_policy == "SIZE":
            freq = sum([x.frequency for x in self.container_clones(c)])
            size = c.metadata.mem_size
            prio = clock + freq/size
        elif self.eviction_policy == "RAND":
            prio = np.random.randint(10)
        elif self.eviction_policy == "LRU":
            prio = c.last_access_t
        elif self.eviction_policy == "TTL":
            prio = c.last_access_t
        elif self.eviction_policy == "LONG-TTL":
            prio = c.last_access_t
        elif self.eviction_policy == "HIST":
            prio = c.last_access_t

        return prio

    ##############################################################

    def checkfree(self, c):
        mem_size = c.metadata.mem_size
        return mem_size + self.mem_used <= self.mem_capacity

    ##############################################################

    def AddToPool(self, c: Container, prewarm:bool=False, at_time=None):
        if not prewarm and at_time is not None:
            raise Exception("Can only add container at self.wall_time when not prewarming")

        mem_size = c.metadata.mem_size
        if mem_size + self.mem_used <= self.mem_capacity:
            #Have free space
            self.mem_used = self.mem_used + mem_size
            self.WriteMemLog("Add", self.wall_time, self.mem_used, mem_size)

            if prewarm and at_time is not None:
                c.last_access_t = at_time
                c.keep_alive_start_t = at_time
            else:
                c.last_access_t = self.wall_time
                c.keep_alive_start_t = self.wall_time
            c.Priority = self.calc_priority(c)
            c.insert_clock = self.Clock #Need this when recomputing priority
            heapq.heappush(self.ContainerPool, c)
            return True
        else:
            # print ("Not enough space for memsize, used, capacity.", mem_size, self.mem_used, self.mem_capacity)
            return False

    ##############################################################

    def RemoveFromPool(self, c: Container, reason: str):
        if c in self.running_c:
            raise Exception("Cannot remove a running container")
        self.ContainerPool.remove(c)
        self.mem_used -= c.metadata.mem_size

        self.WriteMemLog(reason, self.wall_time, self.mem_used, c.metadata.mem_size)
        heapq.heapify(self.ContainerPool)

    ##############################################################

    def PurgeOldLongTTL(self, container_list):
        """ Return list of still usable containers after purging those older than TTL """

        kill_list = [c for c in container_list
                     if c.last_access_t + self.Long_TTL < self.wall_time]

        #Aargh this is duplicated from Eviction. Hard to merge though.
        for k in kill_list:
            self.RemoveFromPool(k, "TTL-purge")
            kind = k.metadata.kind
            self.evdict[kind] += 1

        #This is just the inverse of kill_list. Crummy way to do this, but YOLO
        valid_containers = [c for c in container_list
                     if c.last_access_t + self.Long_TTL >= self.wall_time]

        heapq.heapify(self.ContainerPool)
        return valid_containers

    ##############################################################

    def PurgeOldTTL(self, container_list):
        """ Return list of still usable containers after purging those older than TTL """

        kill_list = [c for c in container_list
                     if c.last_access_t + self.TTL < self.wall_time]

        #Aargh this is duplicated from Eviction. Hard to merge though.
        for k in kill_list:
            self.RemoveFromPool(k, "TTL-purge")
            kind = k.metadata.kind
            self.evdict[kind] += 1

        #This is just the inverse of kill_list. Crummy way to do this, but YOLO
        valid_containers = [c for c in container_list
                     if c.last_access_t + self.TTL >= self.wall_time]

        heapq.heapify(self.ContainerPool)
        return valid_containers

    ##############################################################


    def Landlord_Charge_Rent(self):
        """ Return a list of containers to be evicted """
        #Go over all containers, charging rent
        #Then evict lowest credit containers...
        deltas = [float(c.Priority)/c.metadata.mem_size for c in self.ContainerPool]
        delta = min(deltas)
        for c in self.ContainerPool:
            c.Priority = c.Priority - (delta*c.metadata.mem_size)

        heapq.heapify(self.ContainerPool)

    ############################################################

    def Eviction_Priority_Based(self, to_free, eviction_target):
        """ Return save and victim lists for Priority based methods """
        save = []
        eviction_list = []

        if self.eviction_policy == "LND" :
            self.Landlord_Charge_Rent()

        while to_free > eviction_target and len(self.ContainerPool) > 0:
            # XXX Can't evict running containers right?
            # Even with infinite concurrency, container will still exist in running_c
            # cleanup_finished
            victim = heapq.heappop(self.ContainerPool)
            if victim in self.running_c:
                save.append(victim)
            else:
                eviction_list.append(victim)
                to_free -= victim.metadata.mem_size

        return save, eviction_list

    #############################################################

    def Eviction(self, d: LambdaData):
        """ Return a list of containers to be evicted """
        to_free = d.mem_size

        if self.eviction_policy != "ALL":
            eviction_target = 0
        else:
            eviction_target = np.infty

        self.WriteMemLog("Pre-eviction", self.wall_time, self.mem_used, to_free)

        if len(self.running_c) == len(self.ContainerPool):
            # all containers busy
            self.WriteMemLog("Post-eviction", self.wall_time, self.mem_used, to_free)
            return []

        save, eviction_list = self.Eviction_Priority_Based(to_free, eviction_target)

        for v in eviction_list:
            self.mem_used -= v.metadata.mem_size
            k = v.metadata.kind
            self.evdict[k] += 1

        for c in save:
            heapq.heappush(self.ContainerPool, c)

        #Supposed to set clock = max(eviction_list)
        #Since these are sorted, just use the last element?
        if len(eviction_list) > 0 :
            max_clock = eviction_list[-1].Priority
            #also try max(eviction_list.Priority) ?
            self.Clock = max_clock

        ev_postmortem = [str(v) for v in eviction_list]

        self.WriteMemLog("Post-eviction", self.wall_time, self.mem_used, to_free, ev_postmortem)

        return eviction_list

    ##############################################################

    def cache_miss(self, d:LambdaData):
        c = Container(d)
        if not self.checkfree(c) : #due to space constraints
            #print("Eviction needed ", d.mem_size, self.mem_used)
            evicted = self.Eviction(d) #Is a list. also terminates the containers?

        added = self.AddToPool(c)
        if not added:
            # print("Could not add even after evicting. FATAL ERROR")
            # print("actual in-use memory", sum([k.metadata.mem_size for k in self.ContainerPool]))
            # print("pool size", len(self.ContainerPool))
            return None

        heapq.heapify(self.ContainerPool)
        return c

    ##############################################################

    def cleanup_finished(self):
        """ Go through running containers, remove those that have finished """
        t = self.wall_time
        finished = []
        for c in self.running_c:
            (start_t, fin_t) = self.running_c[c]
            if t >= fin_t:
                finished.append(c)

        for c in finished:
            del self.running_c[c]
            if c.metadata.kind in self.histPrewarm and self.histPrewarm[c.metadata.kind] != 0:
                self.RemoveFromPool(c, "HIST-prewarm")

        heapq.heapify(self.ContainerPool)
        # We'd also like to set the container state to WARM (or atleast Not running.)
        # But hard to keep track of the container object references?
        return len(finished)

    ##############################################################

    def runActivation(self, d: LambdaData, t = 0):

        #First thing we want to do is queuing delays?
        #Also some notion of concurrency level. No reason that more cannot be launched with some runtime penalty...
        #Let's assume infinite CPUs and so we ALWAYS run at time t
        self.wall_time = t
        self.cleanup_finished()

        self.PreWarmContainers()
        self.track_activation(d)

        # Concurrency check can happen here. If len(running_c) > CPUs, put in the queue.
        # Could add fake 'check' entries corresponding to finishing times to check and drain the queue...

        c = self.find_container(d)
        if c is None:
            #Launch a new container since we didnt find one for the metadata ...
            c = self.cache_miss(d)
            if c is None:
                # insufficient memory
                self.capacity_misses[d.kind] += 1
                return
            c.run()
            #Need to update priority here?
            processing_time = d.run_time
            self.running_c[c] = (t, t+processing_time)
            self.WritePerfLog(d, t, "miss")

        else:
            # Strong assumption. If we can find the container, it is warm.
            c.run()
            processing_time = d.warm_time # d.run_time - d.warm_time
            self.running_c[c] = (t, t+processing_time)
            self.WritePerfLog(d, t, "hit")

        #update the priority here!!
        c.last_access_t = self.wall_time
        new_prio = self.calc_priority(c) #, update=True)
        c.Priority = new_prio
        #Since frequency is cumulative, this will bump up priority of this specific container
        # rest of its clones will be still low prio. We should recompute all clones priority
        for x in self.container_clones(c):
            x.Priority = new_prio

        #Now rebalance the heap and update container access time
        self.WritePureCacheHist(t)
        heapq.heapify(self.ContainerPool)

    ##############################################################

    def miss_stats(self):
        """ Go through the performance log."""
        rdict = dict() #For each activation
        with open(self.PerfLogFName, "r") as f:
            line = f.readline() # throw away header
            for line in f:
                line = line.rstrip()
                d, ptime, evtype = line.split(",")
                k = d
                if k not in rdict:
                    mdict = dict()
                    mdict['misses'] = 0
                    mdict['hits'] = 0
                    rdict[k] = mdict

                if evtype == "miss":
                    rdict[k]['misses'] = rdict[k]['misses'] + 1
                elif evtype == "hit":
                    rdict[k]['hits'] = rdict[k]['hits'] + 1
                else:
                    pass
        #Also some kind of response time data?
        return rdict

    ##############################################################
    ##############################################################
    ##############################################################

if __name__ == "__main__":
    from pprint import pprint
    from TestTraces import *
    ls = LambdaScheduler(policy="TTL", mem_capacity=1024, num_funcs=10, run="b")
    # lt = LowWellTrace()
    # lambdas, input_trace = lt.gen_full_trace(1, sample_seed=1)

    pth = "/extra/alfuerst/azure/functions/trace_pckl/bottom_qt/10-b.pckl"
    with open(pth, "r+b") as f:
        lambdas, input_trace = pickle.load(f)
    print(len(input_trace))

    # for d, t in input_trace:
    #     print(d, t/1000)

    for d, t in input_trace:
        ls.runActivation(d, t)

    print("\n\nDONE\n")

    pprint(ls.evdict)
    pprint(ls.miss_stats())
    print("cap", ls.capacity_misses)

    # print(ls.IT_histogram)
    # print(ls.wellford, "\n")
    # print("hist-ttl",ls.histTTL)
    # print("last seen", ls.last_seen)
    # print("prewarm", ls.histPrewarm)


    # for key, value in ls.wellford.items():
    #     mean, variance, sampleVariance = ls.well_finalize(value)
    #     if isnan(mean):
    #         continue
    #     if variance != 0:
    #         if mean < 0:
    #             print(ls.IT_histogram[key])
    #         print(key, mean, variance, sampleVariance, mean/variance)
    #     else:
    #         print(mean, variance, sampleVariance)
