from datetime import datetime
import hashlib
import json

date_format = "%Y-%m-%d %H:%M:%S"
def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key

def get_random_hash_key(data):
    data_str = json.dumps(data, sort_keys=True)  # Convert dict to string
    data_str = data_str + str(datetime.now())
    hash_result = hashlib.sha256(data_str.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key


def add_current_time_to_data(data):
    # if data is a dictionary and doesn't have a created_at key, add it
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if 'created_at' not in data:
        data['created_at'] = get_current_time()
    return data

def get_current_time():
    c = datetime.now()
    current_time = c.strftime(date_format)
    return current_time


def parse_datetime(timestamp_str):
    """Convert string timestamp to datetime object."""
    return datetime.strptime(timestamp_str, date_format)