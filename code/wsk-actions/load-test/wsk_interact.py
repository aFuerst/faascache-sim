import os
import subprocess
from time import time
import json
import requests

zips = ["chameleon.zip",  "cnn_image_classification.zip",  "dd.zip",  "float_operation.zip",  "gzip_compression.zip",  "hello.zip",  "image_processing.zip",  "lin_pack.zip",  "model_training.zip",  "pyaes.zip",  "video_processing.zip", "json_dumps_loads.zip"]
actions = ["cham", "cnn", "dd", "float", "gzip", "hello", "image", "lin_pack", "train", "aes", "video", "json"]
containers = ["python:3", "python:ai", "python:3", "python:ai", "python:3", "python:3", "python:ai", "python:ai", "python:ai", "python:3", "python:ai-vid", "python:3"]
# mem = [512, 1024, 256, 128, 128, 256, 640, 640, 512, 1024, 894, 128]
mem = [128, 256, 128, 256, 128, 128, 256, 256, 256, 128, 256, 128]

def set_properties(host=None, auth=None):
    if host == None:
      host = 'http://172.17.0.1:3233'
    if auth == None:
        auth = 'babecafe-cafe-babe-cafe-babecafebabe:007zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
    wsk = subprocess.run(args=["wsk", "property", "set", "--apihost", host, "--auth", auth], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if wsk.returncode != 0:
        print(wsk.stderr)
        wsk.check_returncode()
    wsk = subprocess.run(args=["wsk", "package", "create", "py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def add_action(name:str, path:str, container:str="python:3", memory:int=256):
    args = ["wsk", "action", "update", name, "--memory", str(memory), "--kind", container, path]
    wsk = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if wsk.returncode != 0:
        print(wsk.stderr)
        wsk.check_returncode()
    wsk.check_returncode()

def add_web_action(name:str, path:str, container:str="python:3", memory:int=256):
    url = "/alftest/py/{}".format(name)
    args = ["wsk", "action", "update", url, path, "--web", "true", "--memory", str(memory), "--kind", container]
    wsk = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wsk.check_returncode()
    print("http://172.17.0.1:3233/api/v1/web{}".format(url))
    return "http://172.17.0.1:3233/api/v1/web{}".format(url)

def invoke_action(name:str, act_args:dict, return_code:bool=False):
    popen_args = ["wsk", "action", "invoke", "--result", name]
    for key, value in act_args.items():
        popen_args += ["--param", str(key), str(value)]
    start = time()
    wsk = subprocess.run(args=popen_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    latency = time() - start
    if wsk.returncode != 0:
        if return_code:
            return wsk.stderr, latency, wsk.returncode
        return wsk.stderr, latency
    if return_code:
        return json.loads(wsk.stdout.decode()), latency, 0
    return json.loads(wsk.stdout.decode()), latency

def invoke_web_action(url):
    requests.get(url)

def invoke_action_async(name:str, act_args:dict):
    """
    Returns a tuple of running Popen object and the timestamp of when it was started
    """
    popen_args = ["wsk", "action", "invoke", "--result", name]
    for key, value in act_args.items():
        popen_args += ["--param", str(key), str(value)]
    start = time()
    wsk = subprocess.Popen(args=popen_args)
    # print(wsk)
    return wsk, start
    # latency = time() - start
    # if wsk.returncode != 0:
    #     return wsk.stderr, latency
    # return json.loads(wsk.stdout.decode()), latency

def wait_all_popen(procs):
    """
    wait for a list or Popen objects to finish
    """
    for proc, start in procs:
        proc.wait()
        # print(proc.stdout.read())

if __name__ == "__main__":
    set_properties()
    for zip_file, action_name, container, memory in zip(zips, actions, containers, mem):
        path = os.path.join("../py", zip_file)
        add_action(action_name, path, container, memory=memory)
        ret_json, latency = invoke_action(action_name, {})
        print(ret_json, latency)

    add_action("js_act_1", "../js/hello.js", container="nodejs:10")
    p = invoke_action_async("js_act_1", {"name":"ben"})
    wait_all_popen([p])
    print("async", p)
    print(invoke_action("js_act_1", {"name":"ben"}))