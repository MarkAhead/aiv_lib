from enum import Enum
from pydantic import BaseModel

class AccountType(Enum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"

class ArtifactOrigin(Enum):
    CUSTOM = "CUSTOM"
    EXISTING = "EXISTING"
    ORIGINAL = "ORIGINAL"

class ArtifactState(Enum):
    INITIAL_ARTIFACT_CREATED = "INITIAL_ARTIFACT_CREATED"
    MOVE_AND_EXTRACT_COMPLETED = "MOVE_AND_EXTRACT_COMPLETED"
    AUDIO_CREATED = "AUDIO_CREATED"
    IMAGE_TEXT_EXTRACTED = "IMAGE_TEXT_EXTRACTED"
    TEXT_DATA_CREATED = "TEXT_DATA_CREATED"
    SUBTITLE_DATA_CREATED = "SUBTITLE_DATA_CREATED"
    MOVED_TO_READY_ARTIFACTS = "MOVED_TO_READY_ARTIFACTS"
    

class PublishingState(Enum):
    INIT = "INIT"
    AI_CAPTION_CREATED = "AI_CAPTION_CREATED"
    NO_TEXT_DATA_FOUND = "NO_TEXT_DATA_FOUND"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHED = "PUBLISHED"
    

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
    
    
class CaptionData(BaseModel):
    captions: str
    hashtags: list
    title: str
