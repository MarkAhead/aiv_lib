import hashlib
from .db_initialize import db



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
        key = get_hash_key(prompt_data["doc_input"]["prompt_text"])
        prompt_data["key"] = key
    
    key = prompt_data["key"]
    doc_ref = db.collection("social_prompt_store").document(key)

    # Push the combined_data to Firestore
    doc_ref.set(prompt_data)
    print(f"Data pushed for key: {key}")
    return key


def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key
