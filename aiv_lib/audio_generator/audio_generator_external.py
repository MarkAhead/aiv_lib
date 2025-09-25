import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from aiv_lib.util_ConfigManager import get_config_value
from aiv_lib.ArtifactQuality import ArtifactQuality
import requests

def get_voice_map():
    return {
        "Daniel": "Alice",  # Using Alice as a default clear voice
        "Markus": "Brian",  # Middle-aged man voice for Markus
        "Sally": "Aria",    # Female voice for Sally
        "Daksh": "Daksh - Suspenseful and Gripping Voice",  # Exact name from the interface
        "VF": "VF",         # Dr. Von Fusion voice
        "Alice": "Alice",   # Clear and engaging voice
        "Brian": "Brian",   # Middle-aged man voice
        "Aria": "Aria",     # Female voice
        "Bill": "Bill",     # Friendly voice
        "Callum": "Callum", # Gravelly voice
    }
    
# Get API keys from configuration
API_KEYS = [
    get_config_value("ELEVEN_LABS_API_KEY_UDAY"),
]

def generateAudioByPrompt(output_file, text, voice="Alice", quality=None):
    """
    Generate speech using ElevenLabs API with quality settings.
    
    Args:
        output_file: Path where the generated audio will be saved
        text: Text to convert to speech
        voice: Voice to use for generation (default: "Alice")
        quality: Quality level (ArtifactQuality.HQ for high quality)
    """
    # Handle quality parameter
    if quality is None:
        quality_level = ArtifactQuality.HQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.HQ
    
    if quality_level not in [ArtifactQuality.HQ]:
        raise ValueError(f"External generator only supports HQ quality, got: {quality_level}")
    
    print(f"Generating audio with ElevenLabs: '{text[:50]}...' using voice '{voice}' ({quality_level.value} quality)")
    
    # Find a valid API key
    valid_api_key = _findValidApiKey(text)
    if not valid_api_key:
        raise Exception("No valid ElevenLabs API key found")

    # Create ElevenLabs client
    client = ElevenLabs(api_key=valid_api_key)
    
    # Resolve voice name to voice ID
    voice_query = get_voice_map().get(voice, voice)
    voice_id = _resolve_voice_id(client, voice_query)

    # Generate audio with high quality settings for HQ
    model_id = "eleven_multilingual_v2" if quality_level == ArtifactQuality.HQ else "eleven_monolingual_v1"
    output_format = "mp3_44100_128"  # High quality format
    
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        output_format=output_format,
    )

    # Save the audio file
    save(audio_iter, output_file)
    print(f"High quality audio saved to {output_file}")
    return audio_iter

def generateSoundEffectsByPrompt(output_file, effect_description, quality=None):
    """
    Generate sound effects using ElevenLabs Sound Effects API.
    
    Args:
        output_file: Path where the generated audio file should be saved
        effect_description: Text description of the sound effect (e.g., "door creaking", "rain falling")
        quality: Quality level (ArtifactQuality.HQ for high quality)
    
    Returns:
        audio: Generated audio data or None if failed
    """
    # Handle quality parameter
    if quality is None:
        quality_level = ArtifactQuality.HQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.HQ
    
    if quality_level not in [ArtifactQuality.HQ]:
        raise ValueError(f"External generator only supports HQ quality, got: {quality_level}")
    
    print(f"Generating sound effect with ElevenLabs: '{effect_description}' ({quality_level.value} quality)")
    
    valid_api_key = _findValidApiKey(effect_description)
    if not valid_api_key:
        raise Exception("No valid ElevenLabs API key found")

    client = ElevenLabs(api_key=valid_api_key)
    
    try:
        # Use the Sound Effects API
        audio_iter = client.text_to_sound_effects.convert(
            text=effect_description
        )
        
        save(audio_iter, output_file)
        print(f"Sound effect '{effect_description}' saved to {output_file}")
        return audio_iter
        
    except Exception as exc:
        print(f"Error generating sound effect '{effect_description}': {exc}")
        raise exc

def _resolve_voice_id(client: ElevenLabs, voice_query: str) -> str:
    """Return a voice_id given either an ID or a human-readable name."""
    
    # Heuristic: most IDs are 20+ alphanum characters
    if len(voice_query) >= 20 and voice_query.isalnum():
        return voice_query

    try:
        # First try searching for exact match
        search_result = client.voices.search(search=voice_query, page_size=10)
        if search_result.voices:
            # Look for exact name match first
            for voice in search_result.voices:
                if voice.name == voice_query:
                    print(f"Found exact match for voice '{voice_query}': {voice.voice_id}")
                    return voice.voice_id
            
            # If no exact match, try partial match (case insensitive)
            voice_query_lower = voice_query.lower()
            for voice in search_result.voices:
                if voice_query_lower in voice.name.lower():
                    print(f"Found partial match for voice '{voice_query}': {voice.name} ({voice.voice_id})")
                    return voice.voice_id
                    
            # If still no match, use first result
            first_voice = search_result.voices[0]
            print(f"No exact match for '{voice_query}', using first result: {first_voice.name} ({first_voice.voice_id})")
            return first_voice.voice_id
            
    except Exception as exc:
        print(f"Could not search voices for '{voice_query}': {exc}")

    # Try to get all voices and search manually
    try:
        all_voices = client.voices.get_all()
        if all_voices.voices:
            # Look for exact match first
            for voice in all_voices.voices:
                if voice.name == voice_query:
                    print(f"Found exact match in all voices for '{voice_query}': {voice.voice_id}")
                    return voice.voice_id
            
            # Try partial match
            voice_query_lower = voice_query.lower()
            for voice in all_voices.voices:
                if voice_query_lower in voice.name.lower():
                    print(f"Found partial match in all voices for '{voice_query}': {voice.name} ({voice.voice_id})")
                    return voice.voice_id
                    
            # Use first available voice as fallback
            fallback_voice = all_voices.voices[0]
            print(f"No match found for '{voice_query}', using fallback: {fallback_voice.name} ({fallback_voice.voice_id})")
            return fallback_voice.voice_id
            
    except Exception as exc:
        print(f"Could not get all voices: {exc}")

    # If all else fails, raise an error
    raise ValueError(f"Could not resolve voice '{voice_query}' to a valid voice ID. Please check the voice name or use a valid voice ID.")

def _findValidApiKey(text):
    """Find a valid API key that has enough character limit remaining."""
    text_length = len(text)
    for api_key in API_KEYS:
        if api_key and _getAPIWithPendingLimit(api_key, text_length):
            return api_key
    print("No valid API key found.")
    return None

def _getAPIWithPendingLimit(api_key, text_length):
    """Check if API key has enough character limit remaining."""
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"API key has {data['character_count']} characters used out of {data['character_limit']}")
            if data["character_count"] + text_length < data["character_limit"]:
                return True
    except Exception as e:
        print(f"Error checking API limit: {e}")
    return False

if __name__ == "__main__":
    from aiv_lib.util_ConfigManager import get_config_value
    import os
    
    # Get output folder for testing
    output_folder = get_config_value("output_folder")
    if not output_folder:
        output_folder = "/tmp"
    
    test_output_path = os.path.join(output_folder, "test_external_audio.mp3")
    
    # Test text-to-speech generation
    print("Testing HQ quality text-to-speech:")
    generateAudioByPrompt(
        test_output_path, 
        "Hello, this is a test of the external audio generator using ElevenLabs with high quality.", 
        voice="Alice",
        quality=ArtifactQuality.HQ
    )
    
    # Test sound effects generation
    sound_effect_path = os.path.join(output_folder, "test_sound_effect.mp3")
    print("\nTesting sound effects generation:")
    generateSoundEffectsByPrompt(
        sound_effect_path,
        "A gentle rain falling on leaves",
        quality=ArtifactQuality.HQ
    ) 