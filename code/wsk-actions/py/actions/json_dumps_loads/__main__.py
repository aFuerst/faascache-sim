import json
from urllib.request import urlopen
from time import time
import random
import traceback

# https://github.com/jdorfman/awesome-json-datasets
urls = ["https://www.govtrack.us/api/v2/role?current=true&role_type=senator",
"https://www.govtrack.us/api/v2/role?current=true&role_type=representative&limit=438",
"https://api.github.com/emojis",
"https://www.justice.gov/api/v1/blog_entries.json?amp%3Bpagesize=2",
"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"]

cold = True

def main(args):
    # return {"body":"testing\n\n"}
    global cold
    was_cold = cold
    cold = False
    try:
        link = random.choice(urls)

        start = time()
        f = urlopen(link)
        data = f.read().decode("utf-8")
        network = time() - start

        start = time()
        json_data = json.loads(data)
        str_json = json.dumps(json_data, indent=4)
        latency = time() - start

        # print(str_json)
        return {"body": {"network": network, "serialization": latency, "cold":was_cold}}

    except Exception as e:
        return {"body": { "cust_error":traceback.format_exc(), "cold":was_cold, "link":link }}