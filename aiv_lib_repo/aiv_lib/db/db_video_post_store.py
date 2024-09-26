import hashlib
import time
from .db_initialize import db
from datetime import datetime

collection_name = "video_post_store"

def fetch_all_video_posts_data():
    prompt_ref = db.collection(collection_name)
    docs = prompt_ref.stream()
    video_posts_data = []
    for doc in docs:
        video_posts_data.append((doc.id, doc.to_dict()))
    return video_posts_data


def fetch_specific_video_post_data(key):
    prompt_ref = db.collection(collection_name).document(key)
    video_posts_data = prompt_ref.get().to_dict()
    return video_posts_data


def fetch_video_posts_when(in_state, not_in_state):
    # Fetch all the caption posts with the given state
    collection_ref = db.collection(collection_name)
    docs = collection_ref.where("document_state", "array_contains", in_state).stream()
    
    filtered_data = []
    for doc in docs:
        doc_data = doc.to_dict()
        # Check if not_in_state is NOT in the document's state array
        if not_in_state not in doc_data.get("document_state", []):
            filtered_data.append((doc.id, doc_data))
    
    return filtered_data



def push_video_posts_data_to_firestore(video_posts_data):
    # Generate the key if it is not present
    if video_posts_data.get("key") is None:
        c = datetime.now()
        current_time = c.strftime('%H:%M:%S')
        
        # Displays Time
        video_posts_data['created_at'] = current_time
        key = get_hash_key(video_posts_data["doc_input"]["prompt_text"] + str(time.time_ns()))
        video_posts_data["key"] = key
    
    key = video_posts_data["key"]
    doc_ref = db.collection(collection_name).document(key)

    # Push the combined_data to Firestore
    doc_ref.set(video_posts_data)
    print(f"Data pushed for key: {key}")
    return key


def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key
