import json
import os

STATS_FILE = "stats.json"

def load_lifetime_count():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            data = json.load(file)
            return data.get("lifetime_sent", 0)
    return 0

def save_lifetime_count(count):
    with open(STATS_FILE, "w") as file:
        json.dump({"lifetime_sent": count}, file)
