import hashlib
from .util_ConfigManager import get_firestore_client
# Get a Firestore client
db = get_firestore_client()

def fetch_all_video_posts_data():
    prompt_ref = db.collection("social_prompt_store")
    docs = prompt_ref.stream()
    video_post_data = []
    for doc in docs:
        video_post_data.append((doc.id, doc.to_dict()))
    return video_post_data


def fetch_specific_video_post_data(key):
    prompt_ref = db.collection("social_prompt_store").document(key)
    video_post_data = prompt_ref.get().to_dict()
    return video_post_data


def push_video_posts_data_to_firestore(video_post_data):
    # Generate the key if it is not present
    if video_post_data.get("key") is None:
        key = get_hash_key(video_post_data["doc_input"]["prompt_text"])
        video_post_data["key"] = key
    
    key = video_post_data["key"]
    doc_ref = db.collection("social_prompt_store").document(key)

    # Push the combined_data to Firestore
    doc_ref.set(video_post_data)
    print(f"Data pushed for key: {key}")
    return key

def fetch_all_caption_post_data():
    prompt_ref = db.collection("caption_post_store")
    docs = prompt_ref.stream()
    video_post_data = []
    for doc in docs:
        video_post_data.append((doc.id, doc.to_dict()))
    return video_post_data


def fetch_specific_caption_post_data(key):
    prompt_ref = db.collection("caption_post_store").document(key)
    video_post_data = prompt_ref.get().to_dict()
    return video_post_data


import time

def push_caption_post_to_firestore(video_post_data, max_retries=3):
    # Generate the key if it is not present
    if video_post_data.get("key") is None:
        key = get_hash_key(video_post_data["prompt"]["title"])
        video_post_data["key"] = key
    
    key = video_post_data["key"]
    doc_ref = db.collection("caption_post_store").document(key)
    time.sleep(3)
    # Initialize the retry count
    retry_count = 0

    while retry_count < max_retries:
        try:
            doc_ref.set(video_post_data)
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
# push_caption_post_to_firestore(video_post_data)



# fun String.sha256(): String {
#    return MessageDigest.getInstance("SHA-256")
#        .digest(this.toByteArray(Charsets.UTF_8))
#        .joinToString("") { "%02x".format(it) } }
#
def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key
