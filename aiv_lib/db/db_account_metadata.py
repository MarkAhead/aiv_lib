from .db_initialize import db
import time
import random
from .model import AccountType
from .common import get_current_time, parse_datetime
from datetime import timedelta
collection_name = "account_metadata"

def create_account_document(account_key, username, account_type: AccountType):
    print(f"Creating account metadata document for key: {account_key}")
    if not account_key:
        raise Exception("Account key is required")
    if not username:
        raise Exception("Username is required")
    if not account_type:
        raise Exception("Account type is required")
    
    doc_ref = db.collection(collection_name).document(account_key)
    if doc_ref.get().exists:
        print(f"Account document already exists for key: {account_key}")
        return
    
    account_metadata = {
        "key": account_key,
        "username": username,
        "isActive": True,
        "account_type": account_type.value,
        "last_posted": 0,
        "next_post_time": 0,
        "created_at": get_current_time(),
        "last_post_type": "",
        "categories": [],
    }
    doc_ref.set(account_metadata)
    print(f"Created account metadata document for key: {account_key}")
    
        
def fetch_documents_from_collection():
    try:
        collection_ref = db.collection(collection_name)
        documents = collection_ref.stream()
        document_list = []
        for doc in documents:
            document_data = doc.to_dict()
            document_data['id'] = doc.id  # Include document ID
            document_list.append(document_data)
        return document_list
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []


def fetch_all_accounts_keys():
    # filter out accounts that are not active
    collection_ref = db.collection(collection_name).where("isActive", "==", True)
    documents = collection_ref.stream()
    return [doc.id for doc in documents]


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


def get_pending_posts_for_account(account_key):
    """
    Fetches the list of pending post keys for a given account.
    If the document or subcollection doesn't exist, returns an empty list.
    """
    account_ref = db.collection(collection_name).document(account_key)
    pending_posts_ref = account_ref.collection("pending_posts").document("pending_posts")

    doc = pending_posts_ref.get()
    if doc.exists:
        return doc.to_dict().get("post_keys", [])
    return []  # Return empty list if document doesn't exist


def add_post_key_to_account(account_key, artifact_key):
    """
    Adds a post key to the pending_posts subcollection for an account.
    Uses get_pending_posts() to avoid unnecessary Firestore writes.
    """
    pending_posts = get_pending_posts_for_account(account_key)

    if artifact_key in pending_posts:
        print(f"Post key {artifact_key} already exists for account {account_key}")
        return  # Exit early to avoid unnecessary writes

    # Append new post key and update Firestore
    pending_posts.append(artifact_key)
    
    account_ref = db.collection(collection_name).document(account_key)
    pending_posts_ref = account_ref.collection("pending_posts").document("pending_posts")

    pending_posts_ref.set({"artifact_keys": pending_posts}, merge=True)
    print(f"Added post key {artifact_key} to account {account_key} under pending_posts.")


def delete_account_metadata(account_key):
    doc_ref = db.collection(collection_name).document(account_key)
    if doc_ref.get().exists:
        doc_ref.delete()
        print(f"Data deleted from account metadata for key: {account_key}")
    else:
        print(f"Account metadata not found for key: {account_key}")


from datetime import datetime, timedelta

date_format = "%Y-%m-%d %H:%M:%S"

def get_current_time():
    return datetime.now().strftime(date_format)

def parse_datetime(timestamp_str):
    """Convert string timestamp to datetime object."""
    return datetime.strptime(timestamp_str, date_format)

def fetch_all_account_created_in_last_n_days(n_days):
    collection_ref = db.collection(collection_name)
    documents = collection_ref.stream()
    
    current_time = parse_datetime(get_current_time())
    time_threshold = current_time - timedelta(days=n_days)

    valid_accounts = []
    
    for doc in documents:
        doc_dict = doc.to_dict()
        
        # Debugging step: Print the document to see its structure
        if 'created_at' not in doc_dict:
            print(f"Skipping document {doc.id} (missing 'created_at')")
            continue
        
        created_at_str = doc_dict.get('created_at')
        
        try:
            created_at = parse_datetime(created_at_str)
        except ValueError as e:
            print(f"Error parsing 'created_at' for document {doc.id}: {e}")
            continue  # Skip if parsing fails
        
        if created_at > time_threshold:
            valid_accounts.append(doc.id)

    return valid_accounts
