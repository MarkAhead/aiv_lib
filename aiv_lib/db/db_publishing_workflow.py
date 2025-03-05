from .db_initialize import db
from .common import get_random_hash_key, add_current_time_to_data
from aiv_lib.db.model import PublishingState
collection_name = "publishing-workflow"
attibute_current_state = "current_state"
attibute_account_id = "account_id"
attibute_ready_artifact_id = "ready_artifact_id"

def create_publishing_document(ready_artifact_key, account_id):
    
    posting_document = {
        attibute_ready_artifact_id: ready_artifact_key,
        attibute_account_id: account_id,
        attibute_current_state: PublishingState.INIT.value,
    }
    key = get_random_hash_key(posting_document)
    posting_document['key'] = key
    posting_document = add_current_time_to_data(posting_document)
    doc_ref = db.collection(collection_name).document(key)
    if doc_ref.get().exists:
        print(f"Account document already exists for key: {posting_document}")
    else:
        doc_ref.set(posting_document)
        print(f"Data pushed for key: {key}")
    
    return key, posting_document


def save_caption_data(key, caption_data):
    artifact_doc_ref = db.collection(collection_name).document(key)
    subtitle_doc_ref = artifact_doc_ref.collection("data").document("caption-data")
    subtitle_doc_ref.set(caption_data)
    print(f"Caption data saved for key: {key}")
    return key

def fetch_caption_data(key):
    artifact_doc_ref = db.collection(collection_name).document(key)
    caption_doc_ref = artifact_doc_ref.collection("data").document("caption-data")
    caption_doc = caption_doc_ref.get()
    if caption_doc.exists:
        return caption_doc.to_dict()
    else:
        print(f"No caption data found for key: {key}")
        return None



def move_to_state(key, state: PublishingState):
    doc_ref = db.collection(collection_name).document(key)
    doc_ref.update({attibute_current_state: state.value})
    print(f"Data updated for key: {key}")
    return key


def filter_publishing_document_by_account_id(account_id):
    try:
        collection_ref = db.collection(collection_name)
        query = collection_ref.where(attibute_account_id, "==", account_id)
        documents = query.stream()
        document_list = []
        for doc in documents:
            document_data = doc.to_dict()
            document_data['id'] = doc.id  # Include document ID
            document_list.append(document_data)
        return document_list
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []
    

def fetch_specific_publishing_document_data(key):
    prompt_ref = db.collection(collection_name).document(key)
    data = prompt_ref.get().to_dict()
    return data

def update_publishing_document(key, data):
    doc_ref = db.collection(collection_name).document(key)
    doc_ref.set(data)
    print(f"Data updated for key: {key}")
    return key, data

def filter_publishing_document_by_state(current_state):
    document_ref = db.collection(collection_name)
    docs = document_ref.where(attibute_current_state, "==", current_state.value).stream()
    
    data_list = []
    for doc in docs:
        doc_data = doc.to_dict()
        data_list.append((doc.id, doc_data))
    
    return data_list

def filter_publishing_document_by_state_and_account_id(current_state, account_id):
    document_ref = db.collection(collection_name)
    docs = document_ref.where(attibute_current_state, "==", current_state.value).where(attibute_account_id, "==", account_id).stream()
    
    data_list = []
    for doc in docs:
        doc_data = doc.to_dict()
        data_list.append((doc.id, doc_data))
    
    return data_list