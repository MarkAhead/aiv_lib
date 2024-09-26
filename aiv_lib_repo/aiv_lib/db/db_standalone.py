from .db_initialize import db
import time

collection_name = "standalone"
instagram_profiles_doc = "instagram_profiles"

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