from aiv_lib.db.model import PostDocProcessingStatus, PostDoc
from .db_initialize import db
from .common import get_current_time
from typing import List, Tuple, Optional, Dict, Any
from google.cloud.firestore import Transaction  

# Collection name for PostDocs (internal artifacts)
COLLECTION_NAME = "internal_artefacts"

def filter_postdocs_by_processing_status(processing_status: PostDocProcessingStatus) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Filter PostDocs from internal_artefacts collection by processingStatus.
    
    Args:
        processing_status (PostDocProcessingStatus): The processing status enum to filter by
    
    Returns:
        List[Tuple[str, Dict[str, Any]]]: List of tuples (doc_id, doc_data) for matching PostDocs
    """
    try:
        print(f"Querying PostDocs with processingStatus: {processing_status.value}")
        collection_ref = db.collection(COLLECTION_NAME)
        docs = collection_ref.where("processingStatus", "==", processing_status.value).stream()
        
        postdocs_data = []
        for doc in docs:
            doc_data = doc.to_dict()
            postdocs_data.append((doc.id, doc_data))
        
        print(f"Found {len(postdocs_data)} PostDocs with status: {processing_status.value}")
        return postdocs_data
    
    except Exception as e:
        print(f"Error filtering PostDocs by status {processing_status.value}: {e}")
        return []

def update_postdoc_processing_status(doc_id: str, new_status: PostDocProcessingStatus, error_message: Optional[str] = None) -> bool:
    """
    Update the processingStatus of a PostDoc document.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        new_status (PostDocProcessingStatus): The new processing status enum
        error_message (str, optional): Error message if status is "FAILED"
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        update_data = {
            "processingStatus": new_status.value,
            "lastUpdated": get_current_time()
        }
        
        if error_message:
            update_data["errorMessage"] = error_message
            
        doc_ref.update(update_data)
        print(f"Updated PostDoc {doc_id} status to: {new_status.value}")
        return True
        
    except Exception as e:
        print(f"Failed to update PostDoc {doc_id} status: {e}")
        return False

def fetch_postdoc_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a specific PostDoc by its document ID.
    
    Args:
        doc_id (str): The document ID of the PostDoc
    
    Returns:
        Optional[Dict[str, Any]]: PostDoc data if found, None otherwise
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc_snapshot = doc_ref.get()
        
        if doc_snapshot.exists:
            return doc_snapshot.to_dict()
        else:
            print(f"PostDoc with ID {doc_id} not found")
            return None
            
    except Exception as e:
        print(f"Error fetching PostDoc {doc_id}: {e}")
        return None

def get_character_voice_id(account_id: str, character_id: str) -> Optional[str]:
    """
    Retrieve the voice ID for a specific character from the characters subcollection.
    
    Args:
        account_id (str): The account ID
        character_id (str): The character ID
    
    Returns:
        Optional[str]: The ElevenLabs voice ID if found, None otherwise
    """
    try:
        character_ref = db.collection('accounts').document(account_id)\
                         .collection('characters').document(character_id)
        character_doc = character_ref.get()
        
        if character_doc.exists:
            character_data = character_doc.to_dict()
            voice_id = character_data.get('voiceId')
            if voice_id:
                print(f"Found voice ID {voice_id} for character {character_id}")
                return voice_id
            else:
                print(f"No voiceId found for character {character_id}")
                return None
        else:
            print(f"Character {character_id} not found for account {account_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching character voice ID for {account_id}/{character_id}: {e}")
        return None

def update_postdoc_atomic(doc_id: str, post_doc: PostDoc) -> bool:
    """
    Update a PostDoc document atomically.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        post_doc (PostDoc): The PostDoc object to update
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc_ref.set(post_doc.to_dict())
        print(f"Updated PostDoc {doc_id}")
        return True
    except Exception as e:
        print(f"Failed to update PostDoc {doc_id}: {e}")
        return False