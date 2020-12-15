from wsk_interact import *
import os
from time import time, sleep

set_properties()

# for zip_file, action_name in zip(zips, actions):
#     path = os.path.join("../py", zip_file)
#     add_action(action_name, path)

lst = []

invocations = 100
for zip_file, action_name in zip(zips, actions):
    path = os.path.join("../py", zip_file)
    cold_total = 0.0
    warm_total = 0.0
    for i in range(invocations):
        name = action_name+str(i)
        add_action(name, path)
        json, cold_latency = invoke_action(name, {})
        sleep(1)
        json, warm_latency = invoke_action(name, {})
        cold_total += cold_latency
        warm_total += warm_latency
    lst.append((action_name, cold_total/invocations, warm_total/invocations))

cold = sorted(lst, key=lambda x: x[1])
warm = sorted(lst, key=lambda x: x[2])

for action, cold, _ in cold:
    print("{0} : {1} sec".format(action, cold))

print("\n")

for action, _, warm in warm:
    print("{0} : {1} sec".format(action, warm))