"""
Artifact quality definitions for AI artifact generation.
"""

from enum import Enum

class ArtifactQuality(Enum):
    """Artifact quality levels for generation"""
    MOCK = "MOCK"  # Mock - for testing
    LQ = "LQ"  # Low Quality - for testing
    HQ = "HQ"  # High Quality - for production 


    def get_quality_level(self, quality: str | None = None):
        if quality is None:
            return self
        elif isinstance(quality, str):
            quality_upper = quality.upper()
            if quality_upper == "LQ":
                return ArtifactQuality.LQ
            elif quality_upper == "HQ":
                return ArtifactQuality.HQ
            elif quality_upper == "MOCK":
                return ArtifactQuality.MOCK
            else:
                return ArtifactQuality.LQ