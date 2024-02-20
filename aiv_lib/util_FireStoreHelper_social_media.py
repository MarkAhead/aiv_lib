import hashlib
import json
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from .util_ConfigManager import get_google_cred_path


# Initialize the Firebase Admin SDK
cred = credentials.Certificate(get_google_cred_path())
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()


def fetch_all_prompt_data():
    prompt_ref = db.collection("social_prompt_store")
    docs = prompt_ref.stream()
    prompt_data = []
    for doc in docs:
        prompt_data.append((doc.id, doc.to_dict()))
    return prompt_data


def fetch_specific_prompt_data(key):
    prompt_ref = db.collection("social_prompt_store").document(key)
    prompt_data = prompt_ref.get().to_dict()
    return prompt_data


def push_prompt_data_to_firestore(prompt_data):
    # Generate the key if it is not present
    if prompt_data.get("key") is None:
        key = get_hash_key(prompt_data["promptStyle"]["prompt_text"])
        prompt_data["key"] = key
    
    key = prompt_data["key"]
    doc_ref = db.collection("social_prompt_store").document(key)

    # Push the combined_data to Firestore
    doc_ref.set(prompt_data)
    print(f"Data pushed for key: {key}")
    return key

def fetch_all_caption_post_data():
    prompt_ref = db.collection("caption_post_store")
    docs = prompt_ref.stream()
    prompt_data = []
    for doc in docs:
        prompt_data.append((doc.id, doc.to_dict()))
    return prompt_data


def fetch_specific_caption_post_data(key):
    prompt_ref = db.collection("caption_post_store").document(key)
    prompt_data = prompt_ref.get().to_dict()
    return prompt_data


import time

def push_caption_post_to_firestore(prompt_data, max_retries=3):
    # Generate the key if it is not present
    if prompt_data.get("key") is None:
        key = get_hash_key(prompt_data["prompt"]["title"])
        prompt_data["key"] = key
    
    key = prompt_data["key"]
    doc_ref = db.collection("caption_post_store").document(key)
    time.sleep(3)
    # Initialize the retry count
    retry_count = 0

    while retry_count < max_retries:
        try:
            doc_ref.set(prompt_data)
            print(f"Data pushed for key: {key}")
            return  # Exit the function if successful
        except Exception as e:
            print(f"Error while pushing data to Firestore: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 3 seconds (retry {retry_count}/{max_retries})")
                time.sleep(3)  # Wait for 3 seconds before retrying

    print(f"Max retries ({max_retries}) reached. Data push failed for key: {key}")

# Usage example:
# push_caption_post_to_firestore(prompt_data)



# fun String.sha256(): String {
#    return MessageDigest.getInstance("SHA-256")
#        .digest(this.toByteArray(Charsets.UTF_8))
#        .joinToString("") { "%02x".format(it) } }
#
def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key
