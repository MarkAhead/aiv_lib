from .db_initialize import db
import time

collection_name = "standalone"
instagram_profiles_doc = "instagram_profiles"
youtube_profiles_doc = "youtube_profiles"
def fetch_instagram_profile():
    """Fetch the Instagram profile session data from Firestore."""
    print(f"Fetching Instagram profile data for key: {instagram_profiles_doc}")
    instgram_profile = db.collection(collection_name).document(instagram_profiles_doc)
    profiles_data = instgram_profile.get().to_dict()
    print(f"Data fetched for key: {instagram_profiles_doc}")
    return profiles_data if profiles_data is not None else {}

def save_instagram_profile(instagram_profiles_data):
    doc_ref = db.collection(collection_name).document(instagram_profiles_doc)
    doc_ref.set(instagram_profiles_data)
    print(f"Data pushed for key: {instagram_profiles_doc}")
    return instagram_profiles_doc

def fetch_youtube_profile(account_key):
    doc_ref = db.collection(collection_name).document(youtube_profiles_doc).collection("data").document(account_key)
    profiles_data = doc_ref.get().to_dict()
    print(f"Data fetched for key: {youtube_profiles_doc}")
    return profiles_data if profiles_data is not None else {}

def save_youtube_profile(account_key, youtube_profiles_data):
    doc_ref = db.collection(collection_name).document(youtube_profiles_doc).collection("data").document(account_key)
    doc_ref.set(youtube_profiles_data)
    print(f"Data pushed for key: {youtube_profiles_doc}")
    return youtube_profiles_doc

def fetch_youtube_account_list_keys():
    doc_ref = db.collection(collection_name).document(youtube_profiles_doc).collection("data")
    account_keys = [doc.id for doc in doc_ref.stream()]
    print(f"Data fetched for key: {youtube_profiles_doc}")
    return account_keys


def delete_youtube_profile(account_key):
    doc_ref = db.collection(collection_name).document(youtube_profiles_doc).collection("data").document(account_key)
    doc_ref.delete()
    print(f"Data deleted from youtube profile for key: {account_key}")

def delete_instagram_profile(account_key):
    doc_ref = db.collection(collection_name).document(instagram_profiles_doc).collection("data").document(account_key)
    doc_ref.delete()
    print(f"Data deleted from instagram profile for key: {account_key}")
