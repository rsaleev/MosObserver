import json
import os


CONFIG = {}
file = f"{os.getcwd()}/config.json"
with open(file, mode="r") as f:
    CONFIG = json.load(f)
