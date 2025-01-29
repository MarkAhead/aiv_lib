from datetime import datetime
import hashlib


def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key

def get_current_time():
    c = datetime.now()
    current_time = c.strftime("%Y-%m-%d %H:%M:%S")
    return current_time