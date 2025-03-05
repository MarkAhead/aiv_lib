
from aiv_lib.db.model import ArtifactType, ArtifactState
from .db_initialize import db
from .common import get_hash_key, get_current_time
from .model import CaptionData
collection_name = "ready_artifacts"

def fetch_specific_artifact(key):
    artifact = db.collection(collection_name).document(key)
    return artifact.get().to_dict()

def fetch_all_artifacts():
    collection_ref = db.collection(collection_name)
    documents = collection_ref.stream()
    return [doc.id for doc in documents]

def fetch_all_ready_artifacts_with_category(category):
    collection_ref = db.collection(collection_name).where("category", "==", category)
    documents = collection_ref.stream()
    return [doc.id for doc in documents]

def fetch_text_data(key):
    # Reference to the main artifact document
    artifact_doc_ref = db.collection(collection_name).document(key)
    
    # Add subtitle data to the "subtitle_data" sub-collection
    text_doc_ref = artifact_doc_ref.collection("data").document("text_data")
    text_doc = text_doc_ref.get()
    if text_doc.exists:
        return text_doc.to_dict()
    else:
        print(f"No text data found for key: {key}")
        return None
    
def fetch_subtitle_data(key):
    artifact_doc_ref = db.collection(collection_name).document(key)
    subtitle_doc_ref = artifact_doc_ref.collection("data").document("subtitle_data")
    subtitle_doc = subtitle_doc_ref.get()
    if subtitle_doc.exists:
        return subtitle_doc.to_dict()
    else:
        print(f"No subtitle data found for key: {key}")
        return None
    

