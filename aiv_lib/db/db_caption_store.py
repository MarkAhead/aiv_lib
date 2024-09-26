from ..util import get_hash_key
from .db_initialize import db
import time

collection_name = "caption_post_store"

def fetch_all_caption_post_data():
    prompt_ref = db.collection(collection_name)
    docs = prompt_ref.stream()
    video_post_data = []
    for doc in docs:
        video_post_data.append((doc.id, doc.to_dict()))
    return video_post_data


def fetch_specific_caption_post_data(key):
    prompt_ref = db.collection(collection_name).document(key)
    video_post_data = prompt_ref.get().to_dict()
    return video_post_data


def fetch_caption_posts_when(in_state, not_in_state):
    # Fetch all the caption posts with the given state
    caption_ref = db.collection(collection_name)
    docs = caption_ref.where("document_state", "array_contains", in_state).stream()
    
    caption_data = []
    for doc in docs:
        doc_data = doc.to_dict()
        # Ensure that 'not_in_state' is NOT in the document's state array
        if not_in_state not in doc_data.get("document_state", []):
            caption_data.append((doc.id, doc_data))
    
    return caption_data


def push_caption_post_to_firestore(video_post_data, max_retries=3):
    # Generate the key if it is not present
    if video_post_data.get("key") is None:
        key = get_hash_key(str(time.time()))
        video_post_data["key"] = key
    
    key = video_post_data["key"]
    doc_ref = db.collection(collection_name).document(key)
    retry_count = 0

    while retry_count < max_retries:
        try:
            doc_ref.set(video_post_data)
            print(f"Data pushed for key: {key}")
            return key # Exit the function if successful
        except Exception as e:
            print(f"Error while pushing data to Firestore: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 3 seconds (retry {retry_count}/{max_retries})")
                time.sleep(3)  # Wait for 3 seconds before retrying

    print(f"Max retries ({max_retries}) reached. Data push failed for key: {key}")
    return key

