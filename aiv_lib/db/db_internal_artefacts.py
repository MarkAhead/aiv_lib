from aiv_lib.db.model import PostDocProcessingStatus
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

def update_postdoc_scene_assets(doc_id: str, scene_id: str, asset_urls: List[str]) -> bool:
    """
    Update the generated asset URLs for a specific scene in a PostDoc.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        scene_id (str): The ID of the scene to update
        asset_urls (List[str]): List of generated asset URLs
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        
        # Build the field path for the specific scene's assets
        # This assumes the scene assets are stored at storyDoc.scenes[index].generatedAssets
        # We'll need to fetch the document first to find the scene index
        doc_data = fetch_postdoc_by_id(doc_id)
        if not doc_data:
            return False
        
        scenes = doc_data.get('storyDoc', {}).get('scenes', [])
        scene_index = None
        
        for i, scene in enumerate(scenes):
            if scene.get('id') == scene_id:
                scene_index = i
                break
        
        if scene_index is None:
            print(f"Scene {scene_id} not found in PostDoc {doc_id}")
            return False
        
        # Update the specific scene's generated assets
        update_field = f"storyDoc.scenes.{scene_index}.generatedAssets"
        doc_ref.update({update_field: asset_urls})
        
        print(f"Updated scene {scene_id} assets in PostDoc {doc_id}")
        return True
        
    except Exception as e:
        print(f"Failed to update scene assets for PostDoc {doc_id}, scene {scene_id}: {e}")
        return False

def update_postdoc_block_assets(doc_id: str, scene_id: str, block_index: int, asset_urls: List[str]) -> bool:
    """
    Update the generated asset URLs for a specific block within a scene.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        scene_id (str): The ID of the scene containing the block
        block_index (int): The index of the block within the scene
        asset_urls (List[str]): List of generated asset URLs
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        
        # Find the scene index first
        doc_data = fetch_postdoc_by_id(doc_id)
        if not doc_data:
            return False
        
        scenes = doc_data.get('storyDoc', {}).get('scenes', [])
        scene_index = None
        
        for i, scene in enumerate(scenes):
            if scene.get('id') == scene_id:
                scene_index = i
                break
        
        if scene_index is None:
            print(f"Scene {scene_id} not found in PostDoc {doc_id}")
            return False
        
        # Update the specific block's assets
        update_field = f"storyDoc.scenes.{scene_index}.blocks.{block_index}.assets"
        doc_ref.update({update_field: asset_urls})
        
        print(f"Updated block {block_index} assets in scene {scene_id} of PostDoc {doc_id}")
        return True
        
    except Exception as e:
        print(f"Failed to update block assets for PostDoc {doc_id}, scene {scene_id}, block {block_index}: {e}")
        return False

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

def update_postdoc_with_assets_atomic(doc_id: str, generated_assets: List[Dict[str, Any]]) -> bool:
    """
    Atomically update a PostDoc with generated assets and set status to ASSET_GENERATION_COMPLETED.
    Uses Firestore transaction to ensure data consistency.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        generated_assets (List[Dict[str, Any]]): List of generated asset metadata
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        print(f"Starting atomic update for PostDoc {doc_id} with {len(generated_assets)} assets")
        
        # Use Firestore transaction for atomic operations
        @db.transaction
        def update_postdoc_transaction(transaction: Transaction):
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            
            # Read current document state
            doc_snapshot = doc_ref.get(transaction=transaction)
            if not doc_snapshot.exists:
                raise ValueError(f"PostDoc {doc_id} not found")
            
            doc_data = doc_snapshot.to_dict()
            
            # Prepare update data
            update_data = {
                "processingStatus": PostDocProcessingStatus.ASSET_GENERATION_COMPLETED.value,
                "lastUpdated": get_current_time(),
                "assetGenerationCompletedAt": get_current_time()
            }
            
            # Organize assets by scene and update scene data
            scenes = doc_data.get('storyDoc', {}).get('scenes', [])
            updated_scenes = []
            
            for scene in scenes:
                scene_id = scene.get('id')
                scene_assets = [asset for asset in generated_assets if asset.get('scene_id') == scene_id]
                
                # Add generated assets to scene
                if scene_assets:
                    scene['generatedAssets'] = scene_assets
                    print(f"  Added {len(scene_assets)} assets to scene {scene_id}")
                
                updated_scenes.append(scene)
            
            # Update the scenes with asset information
            update_data['storyDoc.scenes'] = updated_scenes
            
            # Perform atomic update
            transaction.update(doc_ref, update_data)
            print(f"Atomic update completed for PostDoc {doc_id}")
        
        # Execute the transaction
        update_postdoc_transaction()
        return True
        
    except Exception as e:
        print(f"Failed atomic update for PostDoc {doc_id}: {e}")
        return False

def update_postdoc_failure_atomic(doc_id: str, error_message: str) -> bool:
    """
    Atomically update a PostDoc to FAILED status with error message.
    Uses Firestore transaction to ensure data consistency.
    
    Args:
        doc_id (str): The document ID of the PostDoc
        error_message (str): The error message to record
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        print(f"Starting atomic failure update for PostDoc {doc_id}")
        
        # Use Firestore transaction for atomic operations
        @db.transaction
        def update_failure_transaction(transaction: Transaction):
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            
            # Read current document state
            doc_snapshot = doc_ref.get(transaction=transaction)
            if not doc_snapshot.exists:
                raise ValueError(f"PostDoc {doc_id} not found")
            
            # Prepare failure update data
            update_data = {
                "processingStatus": PostDocProcessingStatus.FAILED.value,
                "errorMessage": error_message,
                "lastUpdated": get_current_time(),
                "failedAt": get_current_time()
            }
            
            # Perform atomic update
            transaction.update(doc_ref, update_data)
            print(f"Atomic failure update completed for PostDoc {doc_id}")
        
        # Execute the transaction
        update_failure_transaction()
        return True
        
    except Exception as e:
        print(f"Failed atomic failure update for PostDoc {doc_id}: {e}")
        return False

def update_postdoc_processing_start_atomic(doc_id: str) -> bool:
    """
    Atomically update a PostDoc to indicate processing has started.
    Uses Firestore transaction to ensure data consistency.
    
    Args:
        doc_id (str): The document ID of the PostDoc
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        print(f"Starting atomic processing start update for PostDoc {doc_id}")
        
        # Use Firestore transaction for atomic operations
        @db.transaction
        def update_processing_start_transaction(transaction: Transaction):
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            
            # Read current document state
            doc_snapshot = doc_ref.get(transaction=transaction)
            if not doc_snapshot.exists:
                raise ValueError(f"PostDoc {doc_id} not found")
            
            # Prepare processing start update data
            update_data = {
                "processingStatus": PostDocProcessingStatus.ASSET_GENERATION_IN_PROGRESS.value,
                "lastUpdated": get_current_time(),
                "processingStartedAt": get_current_time()
            }
            
            # Perform atomic update
            transaction.update(doc_ref, update_data)
            print(f"Atomic processing start update completed for PostDoc {doc_id}")
        
        # Execute the transaction
        update_processing_start_transaction()
        return True
        
    except Exception as e:
        print(f"Failed atomic processing start update for PostDoc {doc_id}: {e}")
        return False

def update_postdoc_batch_assets(postdoc_updates: List[Dict[str, Any]]) -> bool:
    """
    Batch update multiple PostDocs with their generated assets atomically.
    Uses Firestore batch writes for efficient bulk operations.
    
    Args:
        postdoc_updates (List[Dict[str, Any]]): List of PostDoc update data
            Each item should contain: {'doc_id': str, 'assets': List[Dict], 'status': str}
    
    Returns:
        bool: True if batch update successful, False otherwise
    """
    try:
        print(f"Starting batch update for {len(postdoc_updates)} PostDocs")
        
        # Create batch write
        batch = db.batch()
        
        for update_item in postdoc_updates:
            doc_id = update_item['doc_id']
            assets = update_item.get('assets', [])
            status = update_item.get('status', PostDocProcessingStatus.ASSET_GENERATION_COMPLETED.value)
            
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            
            update_data = {
                "processingStatus": status,
                "lastUpdated": get_current_time()
            }
            
            if status == PostDocProcessingStatus.ASSET_GENERATION_COMPLETED.value:
                update_data["assetGenerationCompletedAt"] = get_current_time()
                if assets:
                    update_data["generatedAssets"] = assets
            elif status == PostDocProcessingStatus.FAILED.value:
                update_data["failedAt"] = get_current_time()
                error_message = update_item.get('error_message')
                if error_message:
                    update_data["errorMessage"] = error_message
            
            batch.update(doc_ref, update_data)
        
        # Commit batch operation
        batch.commit()
        print(f"Batch update completed for {len(postdoc_updates)} PostDocs")
        return True
        
    except Exception as e:
        print(f"Failed batch update: {e}")
        return False 