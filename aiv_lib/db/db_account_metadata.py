from .db_initialize import db
import time
import random

collection_name = "account_metadata"

def fetch_last_post_timestamp(key):
    account = db.collection(collection_name).document(key)
    account_data = account.get().to_dict()
    if account_data is None:
        print(f"Account not found for key: {key}")
        return None
    else:
        return account_data.get("last_posted")


def update_publish_timestamp(key, post_type):
    timestamp = int(time.time() * 1000)  # Get the current time in milliseconds
    account = db.collection(collection_name).document(key)
    account_data = account.get().to_dict()
    
    if account_data is None:
        print(f"Account not found for key: {key}")
        return None
    else:
        account_data["last_posted"] = timestamp  # Store the timestamp in milliseconds
        account_data["last_post_type"] = post_type
        account.set(account_data)
        return account_data.get("last_posted")


def fetch_specific_account_metadata(key):
    account = db.collection(collection_name).document(key)
    account_data = account.get().to_dict()
    if account_data is None:
        print(f"Account not found for key: {key}")
        return None
    else:
        return account_data


def update_next_post_time(key, post_type, min_delay_ms, max_delay_ms):
    current_time_ms = int(time.time() * 1000)
    next_post_time_ms = current_time_ms + random.randint(min_delay_ms, max_delay_ms)
    
    account = db.collection(collection_name).document(key)
    account_data = account.get().to_dict()
    
    if account_data is None:
        print(f"Account not found for key: {key}")
        return None
    else:
        account_data["last_posted"] = current_time_ms
        account_data["next_post_time"] = next_post_time_ms
        account_data["last_post_type"] = post_type
        account.set(account_data)
        return next_post_time_ms