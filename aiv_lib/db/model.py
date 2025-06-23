from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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
    

# PostDoc Processing States for Asset Generation
class PostDocProcessingStatus(Enum):
    PENDING = "PENDING"
    ASSET_GENERATION_IN_PROGRESS = "ASSET_GENERATION_IN_PROGRESS"
    ASSET_GENERATION_COMPLETED = "ASSET_GENERATION_COMPLETED"
    TIMELINE_FINALIZED = "TIMELINE_FINALIZED"
    VIDEO_RENDERED = "VIDEO_RENDERED"
    FAILED = "FAILED"

# Asset Types for Generation
class AssetType(Enum):
    IMAGE = "image"
    AUDIO = "audio"
    SFX = "sfx"
    VIDEO = "video"

# Block Types in PostDoc Scenes
class BlockType(Enum):
    DIALOGUE = "dialogue"
    NARRATION = "narration"
    ACTION = "action"
    SFX = "sfx"
    VISUAL = "visual"

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

# PostDoc-related Models
class PostDocMetadata(BaseModel):
    accountId: str
    
class PostDocCloudData(BaseModel):
    bucketName: str
    mainFolder: str

class SceneBlock(BaseModel):
    type: str  # BlockType enum value
    content: str
    character: Optional[str] = None
    assets: Optional[List[str]] = None
    startTime: Optional[float] = None
    duration: Optional[float] = None

class Scene(BaseModel):
    id: str
    title: str
    blocks: List[SceneBlock] = []
    visualPrompt: Optional[str] = None
    audioPrompt: Optional[str] = None
    sfxPrompts: Optional[List[str]] = None

class StoryDoc(BaseModel):
    scenes: List[Scene]

class PostDoc(BaseModel):
    metadata: PostDocMetadata
    cloudData: PostDocCloudData
    storyDoc: StoryDoc
    processingStatus: str  # PostDocProcessingStatus enum value
    lastUpdated: Optional[str] = None
    errorMessage: Optional[str] = None
