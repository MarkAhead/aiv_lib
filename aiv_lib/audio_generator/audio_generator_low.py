"""
Backward compatibility module for audio_generator_low.py
This module provides the same interface as before but now uses the unified audio generator.
"""

import os
import asyncio
from aiv_lib.ArtifactQuality import ArtifactQuality
from aiv_lib.util_pixabay_api import download_sound_effects
from aiv_lib.util_ConfigManager import get_config_value

# Try to import edge-tts, if not available, we'll provide fallback
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("Warning: edge-tts not installed. Install with: pip install edge-tts")

# Voice mappings for edge-tts
EDGE_TTS_VOICES = {
    "Christopher": "en-US-AriaNeural",
    "Brian": "en-US-BrianNeural", 
}

__all__ = [
    "generateAudioByPrompt",
    "generateSoundEffectsByPrompt",
    "listAvailableVoices",
    # Legacy helpers
    "generateAudioLowQuality",
    "generateAudioMock",
]

# -----------------------------
# Main Generation Functions
# -----------------------------

def generateAudioByPrompt(output_file: str, text: str, voice: str = "Christopher", quality: ArtifactQuality | str | None = None):
    """Generate speech using edge-tts or mock tone.

    Parameters
    ----------
    output_file : str
        Path to store the generated audio (``.wav``)
    text : str
        Text to convert to speech.
    voice : str, optional
        Voice alias, by default "Alice".
    quality : ArtifactQuality | str | None, optional
        ``LQ`` for low-quality (edge-tts) or ``MOCK`` for test tone.  Defaults to
        ``LQ``.
    """
    quality_level = _parse_quality(quality)
    print(f"Generating audio with {quality_level.value} quality using voice '{voice}'")

    return _generateEdgeTTSAudio(output_file, text, voice, quality_level)

def generateSoundEffectsByPrompt(output_file: str, effect_description: str, quality: ArtifactQuality | str | None = None):
    import shutil
    output_dir = os.path.dirname(output_file)
    resources_folder = get_config_value("resources_folder")
    mocked_file = os.path.join(resources_folder, "sounds/chime-sound.mp3")
    shutil.copy(mocked_file, output_file)
    print(f"Mocked sound effect saved → {output_file}")
    return True


# -----------------------------
# Implementation Helpers
# -----------------------------

def _parse_quality(q):
    if q is None:
        return ArtifactQuality.LQ
    if isinstance(q, ArtifactQuality):
        return q
    if isinstance(q, str):
        try:
            return ArtifactQuality[q.upper()]
        except KeyError:
            return ArtifactQuality.LQ
    return ArtifactQuality.LQ

async def _async_generate_edge_tts(path, text, edge_voice, rate, volume):
    communicate = edge_tts.Communicate(text, edge_voice)
    # edge-tts always outputs mp3; we want wav for consistency – generate temp then convert
    tmp_mp3 = f"{path}.tmp.mp3"
    await communicate.save(tmp_mp3)
    # Convert mp3→wav using pydub if available
    try:
        from pydub import AudioSegment
        AudioSegment.from_file(tmp_mp3).export(path, format="wav")
        os.remove(tmp_mp3)
    except Exception as exc:
        # Could not convert – keep mp3
        print(f"Warning: could not convert mp3→wav ({exc}). Keeping mp3")
        os.rename(tmp_mp3, path)

def _generateEdgeTTSAudio(output_file, text, voice, quality_level):
    edge_voice = EDGE_TTS_VOICES.get(voice, "en-US-AriaNeural")
    rate = "+10%" if quality_level == ArtifactQuality.LQ else "+0%"
    volume = "+0%"

    try:
        asyncio.run(_async_generate_edge_tts(output_file, text, edge_voice, rate, volume))
        print(f"edge-tts audio saved → {output_file}")
        return True
    except Exception as exc:
        print(f"edge-tts generation failed: {exc}. Falling back to mock tone")
        return _generateMockAudio(output_file, text, voice)

def _generateMockAudio(output_file, text, voice):
    import wave, struct, math
    words = max(1, len(text.split()))
    duration = max(1.0, words / 2.5)  # ≈150 WPM
    sr = 22050
    freqs = {
        "Alice": 440,
        "Brian": 220,
        "Aria": 523,
        "Daniel": 294,
        "Markus": 196,
        "Sally": 494,
        "Bill": 262,
        "Callum": 175,
        "VF": 330,
        "Daksh": 370,
    }
    f0 = freqs.get(voice, 440)
    with wave.open(output_file, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for i in range(int(sr * duration)):
            t = i / sr
            env = min(1.0, t * 4) * min(1.0, (duration - t) * 4)
            sample = env * 0.3 * math.sin(2 * math.pi * f0 * t)
            w.writeframes(struct.pack('<h', int(sample * 32767)))
    print(f"Mock tone saved → {output_file} ({duration:.1f}s)")
    return True

# -----------------------------
# Legacy Convenience Wrappers
# -----------------------------

def generateAudioMock(output_file, text, voice="Alice"):
    """Legacy helper → mock generation."""
    return generateAudioByPrompt(output_file, text, voice, ArtifactQuality.MOCK)

# -----------------------------
# Utilities
# -----------------------------

def listAvailableVoices():
    if not EDGE_TTS_AVAILABLE:
        print("edge-tts not installed – showing mock voices:")
        for v in ["Alice", "Brian", "Aria", "Daniel"]:
            print(f"  - {v}")
        return
    voices = asyncio.run(edge_tts.list_voices())
    print("Edge-TTS voices (first 10):")
    for v in voices[:10]:
        print(f"  - {v['Name']} ({v['Locale']}) – {v['Gender']}")

# -----------------------------
# Self-test
# -----------------------------

if __name__ == "__main__":
    import tempfile
    tmp = tempfile.gettempdir()
    print("Testing edge-tts low-quality generation …")
    generateAudioByPrompt(os.path.join(tmp, "edge_lq.wav"), "This is a low quality test using edge-tts.", quality=ArtifactQuality.LQ)
    print("Testing mock generation …")
    generateAudioByPrompt(os.path.join(tmp, "edge_mock.wav"), "This is a mock tone test.", voice="Brian", quality=ArtifactQuality.MOCK)
    print("Listing voices …")
    listAvailableVoices()
