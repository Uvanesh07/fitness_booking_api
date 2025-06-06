import json
import os

def read_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def write_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
