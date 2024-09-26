

import hashlib


def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key

def get_bucket_name_and_path(path):
    split = path.split("/", 1)
    bucket_name = split[0]
    folder_path = split[1] if len(split) > 1 else ""
    return bucket_name, folder_path