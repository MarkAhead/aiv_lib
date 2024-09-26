
import json
import os
from .util_ConfigManager import get_config_value

filename = get_config_value("key_value_store_path")
def store_key_value(key, value):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[key] = value

    with open(filename, "w") as f:
        json.dump(data, f)

def get_value(key):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            return data.get(key, None)  # Return None if the key is not found
    except (FileNotFoundError, json.JSONDecodeError):
        return None  # Return None if the file is not found or empty
