from wsk_interact import *
import os
from time import time

set_properties()

for zip_file, action_name, container, memory in zip(zips, actions, containers, mem):
    path = os.path.join("../py", zip_file)
    add_web_action(action_name, path, container, memory=memory)