from .db_initialize import db
import time
from enum import Enum
from .common import get_hash_key, get_current_time

collection_name = "existing_artifacts_workflow"
ready_artifacts_collection_name = "ready_artifacts"
current_state = "current_state"
class ArtifactState(Enum):
    INITIAL_ARTIFACT_CREATED = "INITIAL_ARTIFACT_CREATED"
    AUDIO_CREATED = "AUDIO_CREATED"
    IMAGE_TEXT_EXTRACTED = "IMAGE_TEXT_EXTRACTED"
    TEXT_DATA_CREATED = "TEXT_DATA_CREATED"
    SUBTITLE_DATA_CREATED = "SUBTITLE_DATA_CREATED"
    MOVED_TO_READY_ARTIFACTS = "MOVED_TO_READY_ARTIFACTS"
    

class ArtifactType:
    IMAGE = "image"
    VIDEO = "video"
    ZIP = "zip"

    _EXTENSION_MAP = {
        IMAGE: ('.jpg', '.jpeg', '.png'),
        VIDEO: ('.mp4', '.avi', '.mov'),
        ZIP: ('.zip', '.rar', '.7z')
    }

    @staticmethod
    def get_artifact_type(location):
        if not location:
            return None
        
        location = location.lower()
        for artifact_type, extensions in ArtifactType._EXTENSION_MAP.items():
            if location.endswith(extensions):
                return artifact_type
        return None
    

def create_new_artifact_document(location, category, bucket_name):
    if location is None:
        print("Location is None")
        return None  
    
    if category is None:
        print("Category is None")
        return None 
    
    # Assuming ArtifactType is a class with a get_artifact_type method
    artifact_type = ArtifactType.get_artifact_type(location)
    if artifact_type is None:
        print("Artifact type is None")
        return None
    
    # Define the artifact document
    existing_artifact = {
        "category": category,
        "artifact_type": artifact_type,
        "artifact_location": location,
        "bucket_name": bucket_name,
        current_state: ArtifactState.INITIAL_ARTIFACT_CREATED.value,
    }
    
    return push_existing_artifact_to_firestore(existing_artifact)
    
def push_existing_artifact_to_firestore(existing_artifact):
    # Generate the key if it is not present
    if existing_artifact.get("key") is None:
        existing_artifact['created_at'] = get_current_time()
        key = get_hash_key(existing_artifact["artifact_location"])
        existing_artifact["key"] = key
    
    key = existing_artifact["key"]
    doc_ref = db.collection(collection_name).document(key)
    # Push the combined_data to Firestore
    doc_ref.set(existing_artifact)
    print(f"Data pushed for key: {key}")
    return key, existing_artifact
        
def fetch_all_exisiting_artifacts_from_collection():
    try:
        collection_ref = db.collection(collection_name)
        documents = collection_ref.stream()
        document_list = []
        for doc in documents:
            document_data = doc.to_dict()
            document_data['id'] = doc.id  # Include document ID
            document_list.append(document_data)
        return document_list
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []



def fetch_specific_existing_artifact_data(key):
    prompt_ref = db.collection(collection_name).document(key)
    video_post_data = prompt_ref.get().to_dict()
    return video_post_data


def filter_existing_artifacts_by_state(current_state: ArtifactState):
    document_ref = db.collection(collection_name)
    docs = document_ref.where(current_state, "==", current_state.value).stream()
    
    existing_artifacts_data = []
    for doc in docs:
        doc_data = doc.to_dict()
        existing_artifacts_data.append((doc.id, doc_data))
    
    return existing_artifacts_data

def filter_existing_artifacts_by_state_and_type(current_state: ArtifactState, artifact_type: ArtifactType):
    document_ref = db.collection(collection_name)
    
    # Query using correct field names
    docs = document_ref.where("current_state", "==", current_state.value) \
        .where("artifact_type", "==", artifact_type) \
        .stream()
    
    existing_artifacts_data = []
    for doc in docs:
        doc_data = doc.to_dict()
        existing_artifacts_data.append((doc.id, doc_data))
    
    return existing_artifacts_data


def add_text_data_to_existing_artifact(key, text_data):
    try:
        # Reference to the main artifact document
        artifact_doc_ref = db.collection(collection_name).document(key)
        
        # Add text data to the "text_data" sub-collection
        text_doc_ref = artifact_doc_ref.collection("data").document("text_data")
        data = {"text_data": text_data}
        text_doc_ref.set(data)  # Save text data to the sub-collection
        
        # Update the main document's state
        artifact_doc_ref.update({"current_state": ArtifactState.TEXT_DATA_CREATED.value})
        print(f"Text data successfully added for key: {key}")
        return key
    except Exception as e:
        print(f"Failed to add text data for key: {key}. Error: {e}")
        return None

def get_text_data_from_existing_artifact(key):
    try:
        # Reference to the main artifact document
        artifact_doc_ref = db.collection(collection_name).document(key)
        
        # Reference to the "text_data" sub-collection
        text_collection_ref = artifact_doc_ref.collection("data").document("text_data")
        
        # Get the text data from the sub-collection
        text_doc = text_collection_ref.get()
        if text_doc.exists:
            return text_doc.to_dict()  # Return the text data as a dictionary
        else:
            print(f"No text data found for key: {key}")
            return None
    except Exception as e:
        print(f"Failed to get text data for key: {key}. Error: {e}")
        return None

def add_subtitle_data_to_existing_artifact(key, subtitle_data):
    try:
        # Reference to the main artifact document
        artifact_doc_ref = db.collection(collection_name).document(key)
        
        # Add subtitle data to the "subtitle_data" sub-collection
        subtitle_doc_ref = artifact_doc_ref.collection("data").document("subtitle_data")
        data = {"subtitle_data": subtitle_data}
        subtitle_doc_ref.set(data)  # Save subtitle data to the sub-collection
        
        # Update the main document's state
        artifact_doc_ref.update({"current_state": ArtifactState.SUBTITLE_DATA_CREATED.value})
        print(f"Subtitle data successfully added for key: {key}")
        return key
    except Exception as e:
        print(f"Failed to add subtitle data for key: {key}. Error: {e}")
        return None


def get_subtitle_data_from_existing_artifact(key):
    try:
        # Reference to the main artifact document
        artifact_doc_ref = db.collection(collection_name).document(key)
        
        # Reference to the "subtitle_data" sub-collection
        subtitle_collection_ref = artifact_doc_ref.collection("data").document("subtitle_data")
        
        # Get the subtitle data from the sub-collection
        subtitle_doc = subtitle_collection_ref.get()
        if subtitle_doc.exists:
            return subtitle_doc.to_dict()  # Return the subtitle data as a dictionary
        else:
            print(f"No subtitle data found for key: {key}")
            return None
    except Exception as e:
        print(f"Failed to get subtitle data for key: {key}. Error: {e}")
        return None


def move_to_ready_artifacts(key):
    try:
        # Get the artifact data from the existing collection
        artifact_doc_ref = db.collection(collection_name).document(key)
        artifact_snapshot = artifact_doc_ref.get()

        if not artifact_snapshot.exists:
            print(f"Artifact with key {key} not found.")
            return None

        # Extract artifact data
        artifact_data = artifact_snapshot.to_dict()
        artifact_data["current_state"] = ArtifactState.MOVED_TO_READY_ARTIFACTS.value

        # Get the category for the final destination
        category = artifact_data.get("category")
        if not category:
            print(f"Category is missing for artifact with key {key}.")
            return None

        # Define the new location for the artifact
        ready_artifact_ref = (
            db.collection(ready_artifacts_collection_name)
            .document(category)
            .collection("artifacts")
            .document(key)
        )

        # Start a Firestore batch
        batch = db.batch()

        # Add the parent document to the batch
        batch.set(ready_artifact_ref, artifact_data)

        # Fetch all sub-collections of the original document
        sub_collections = artifact_doc_ref.collections()
        for sub_collection in sub_collections:
            # For each sub-collection, fetch all documents
            for sub_doc in sub_collection.stream():
                sub_doc_data = sub_doc.to_dict()

                # Define the corresponding sub-document in the new location
                new_sub_doc_ref = ready_artifact_ref.collection(sub_collection.id).document(sub_doc.id)

                # Add the sub-document to the batch
                batch.set(new_sub_doc_ref, sub_doc_data)

        # Commit the batch (this writes the parent and all sub-collections atomically)
        batch.commit()

        # Delete the original document (parent and sub-collections)
        delete_document_and_subcollections(artifact_doc_ref)

        print(f"Artifact and sub-collections moved successfully for key: {key}")
        return key

    except Exception as e:
        print(f"Failed to move artifact for key: {key}. Error: {e}")
        return None


def delete_document_and_subcollections(doc_ref):
    """
    Deletes a document and all its sub-collections recursively.
    """
    try:
        # Fetch all sub-collections of the document
        sub_collections = doc_ref.collections()
        for sub_collection in sub_collections:
            for sub_doc in sub_collection.stream():
                # Recursively delete each sub-document
                delete_document_and_subcollections(sub_doc.reference)

        # Delete the document itself
        doc_ref.delete()
        print(f"Deleted document and its sub-collections: {doc_ref.id}")
    except Exception as e:
        print(f"Failed to delete document or its sub-collections: {e}")

