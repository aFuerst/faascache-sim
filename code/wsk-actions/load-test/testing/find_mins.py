from wsk_interact import *
import os
from time import time, sleep

set_properties()

start_mem = 1024

for zip_file, action_name, container in zip(zips, actions, containers):
    print(action_name)
    mem = start_mem
    warm_times = []
    cold_times = []
    while mem >= 128:
        print(mem)
        iterations = 10
        c_i = 0
        w_i = 0
        cold_lat = []
        warm_lat = []
        for i in range(iterations):
            new_action_name = action_name + '-' + str(mem) + "-" + str(i)
            path = os.path.join("../py", zip_file)
            add_action(new_action_name, path, container, memory=mem)
            json_c, cold_latency, ret = invoke_action(new_action_name, {}, return_code=True)
            if ret == 0:
                # print(json_c)
                cold_lat.append(cold_latency)
                c_i += 1
            sleep(1)
            json_w, warm_latency, ret = invoke_action(new_action_name, {}, return_code=True)
            if ret == 0:
                # print(json_w)
                warm_lat.append(warm_latency)
                w_i += 1
        if c_i != 0 and w_i != 0:
            cold_times.append((mem, sum(cold_lat)/c_i, cold_times))
            warm_times.append((mem, sum(warm_lat)/w_i, warm_lat))
        # print(cold_lat/iterations, warm_lat/iterations)
        mem -= 128
    cold_sort = sorted(cold_times, key= lambda x: x[1])
    warm_sort = sorted(warm_times, key= lambda x: x[1])
    print("Cold: Mem: {0}, {1}".format(cold_sort[0][0], cold_sort[0][1]), "\n", cold_sort)
    print("Warm: Mem: {0}, {1}".format(warm_sort[0][0], warm_sort[0][1]), "\n", warm_sort)

    print("\n")
