from wsk_interact import *
import os
from time import time

set_properties()

zips = ["chameleon.zip",  "cnn_image_classification.zip",  "dd.zip",  "float_operation.zip",  "gzip_compression.zip",  "hello.zip",  "image_processing.zip",  "lin_pack.zip",  "model_training.zip",  "pyaes.zip",  "video_processing.zip", "json_dumps_loads.zip"]
actions = ["cham", "cnn", "dd", "float", "gzip", "hello", "image", "lin_pack", "train", "aes", "video", "json"]
containers = ["python:3", "python:ai", "python:3", "python:ai", "python:3", "python:3", "python:ai", "python:ai", "python:ai", "python:3", "python:ai-vid", "python:3"]
mem = [512, 1024, 512, 512, 512, 400, 512, 512, 1024, 512, 1024, 256]

for zip_file, action_name, container in zip(zips, actions, containers):
    path = os.path.join("../py", zip_file)
    # print(path)
    add_web_action(action_name, path, container)

# for zip_file, action_name in zip(zips, actions):
#     path = os.path.join("../py", zip_file)
#     # print(path)
#     add_action(action_name, path)

# start = time()
# for i in range(3):
#     lst = []
#     for action in actions:
#         lst.append(invoke_action_async(action, {}))
#     wait_all_popen(lst)

# print((time() - start)/3)