import numpy as np
import pandas as pd
from time import time

from wsk_interact import *
import os

avgs = [2.03, 5.85, 2.23, 1.67, 2.48, 1.8, 7.6, 1.73, 10.07, 2.29, 30.15, 2.09]

df = pd.read_csv("./load_trace.csv")
start = time()
allocated_mem = 0

for row in df.iterrows():
    print(row[1]["time"], row[1]["action"])
    