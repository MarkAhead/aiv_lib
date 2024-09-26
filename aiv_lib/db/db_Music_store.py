import json
from .db_initialize import db


collection_name = "music_store"


def fetch_all_music_document():
    prompt_ref = db.collection(collection_name)
    docs = prompt_ref.stream()
    music_document = []
    for doc in docs:
        music_document.append((doc.id, doc.to_dict()))
    return music_document


def fetch_specific_music_document(key):
    prompt_ref = db.collection(collection_name).document(key)
    music_document = prompt_ref.get().to_dict()
    return music_document


def push_music_document_to_firestore(music_document):
    # Generate the key if it is not present
    if music_document.get("key") is None:
        key = get_hash_key(music_document["song"])
        music_document["key"] = key
    
    key = music_document["key"]
    doc_ref = db.collection(collection_name).document(key)

    # Push the combined_data to Firestore
    doc_ref.set(music_document)
    print(f"Data pushed for key: {key}")
    return key

def fetch_all_caption_post_data():
    prompt_ref = db.collection("caption_post_store")
    docs = prompt_ref.stream()
    music_document = []
    for doc in docs:
        music_document.append((doc.id, doc.to_dict()))
    return music_document


def fetch_specific_caption_post_data(key):
    prompt_ref = db.collection("caption_post_store").document(key)
    music_document = prompt_ref.get().to_dict()
    return music_document


import time

def push_caption_post_to_firestore(music_document, max_retries=3):
    # Generate the key if it is not present
    if music_document.get("key") is None:
        key = get_hash_key(music_document["prompt"]["title"])
        music_document["key"] = key
    
    key = music_document["key"]
    doc_ref = db.collection("caption_post_store").document(key)
    time.sleep(3)
    # Initialize the retry count
    retry_count = 0

    while retry_count < max_retries:
        try:
            doc_ref.set(music_document)
            print(f"Data pushed for key: {key}")
            return  # Exit the function if successful
        except Exception as e:
            print(f"Error while pushing data to Firestore: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 3 seconds (retry {retry_count}/{max_retries})")
                time.sleep(3)  # Wait for 3 seconds before retrying

    print(f"Max retries ({max_retries}) reached. Data push failed for key: {key}")


def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key


def filter_documents_by_state(should_be_in_state, should_not_be_in_state):
    document_list = fetch_all_music_document()
    documents_in_state = []
    for key, document in document_list:
        if should_be_in_state in document['document_state'] and should_not_be_in_state not in document['document_state']:
            documents_in_state.append(document)
    return documents_in_state