from time import time
import gzip
import os
import traceback
import random
import string

cold = True

def main(args):
    global cold
    was_cold = cold
    cold = False
    try:
        file_size = args.get("file_size", 5)
        file_write_path = '/tmp/file'

        start = time()
        with open(file_write_path, 'wb') as f:
            f.write(os.urandom(file_size * 1024 * 1024))
        disk_latency = time() - start

        with open(file_write_path, "rb") as f:
            start = time()
            with gzip.open('/tmp/result.gz', 'wb') as gz:
                gz.writelines(f)
            compress_latency = time() - start

        print(compress_latency)

        return {"body": {'disk_write': disk_latency, "compress": compress_latency, "cold":was_cold}}
    except Exception as e:
        return {"body": { "cust_error":traceback.format_exc(), "cold":was_cold }}