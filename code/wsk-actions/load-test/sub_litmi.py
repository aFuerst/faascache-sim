from wsk_interact import *
import os
from time import time
import pickle
import threading

set_properties()

zips = ["chameleon.zip",  "cnn_image_classification.zip",  "dd.zip",  "float_operation.zip",  "gzip_compression.zip",  "hello.zip",  "image_processing.zip",  "lin_pack.zip",  "model_training.zip",  "pyaes.zip",  "video_processing.zip", "json_dumps_loads.zip"]
actions = ["cham", "cnn", "dd", "float", "gzip", "hello", "image", "lin_pack", "train", "aes", "video", "json"]
containers = ["python:3", "python:ai", "python:3", "python:ai", "python:3", "python:3", "python:ai", "python:ai", "python:ai", "python:3", "python:ai-vid", "python:3"]
mem = [128, 512, 256, 64, 256, 128, 256, 256, 542, 256, 512, 128]

urls = []

for zip_file, action_name, container, mem in zip(zips, actions, containers, mem):
    path = os.path.join("../py", zip_file)
    urls.append(add_web_action(action_name, path, container, mem))

trans = {"rare_1":0, "rare_2":1, "rare_3":2, "often":3}

freq = "./traces/freq_litmus_sub.pckl"
lru = "./traces/lru_litmus_sub.pckl"

load = freq

with open(load, "r+b") as f:
    trace = pickle.load(f)

print("trace_len", len(trace), "\n")

start = time()
for tup in trace:
    t = time()
    hash_app, invoc_time_ms, mem, warm, cold = tup
    url = urls[trans[hash_app]]
    invoc_time = invoc_time_ms / 1000 # convert ms to float s
    while t - start < invoc_time:
        t = time()
    threading.Thread(target=invoke_web_action, args=(url,)).start()