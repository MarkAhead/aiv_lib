from elevenlabs.client import ElevenLabs
from elevenlabs import save
from  .util_ConfigManager import get_config_value
import requests

VOICE_MAP = {
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

API_KEYS = [
    get_config_value("ELEVEN_LABS_API_KEY"),
]



def generateHindiAudio(text, output_file):
    return generateAudio(text, output_file, "Daksh")

def generateMaleAudio(text, output_file):
    return generateAudio(text, output_file, "Markus")



def generateFemaleAudio(text, output_file):
    return generateAudio(text, output_file, "Sally")


def generateAudio(text, output_file, voice = "Markus"): 
    """Generate speech and save it to *output_file* using the new SDK.

    The function keeps the original public signature but now:

    1. Selects a working ElevenLabs API key via :pyfunc:`findValidApiKey`.
    2. Constructs an :pyclass:`elevenlabs.client.ElevenLabs` client with that
       key.
    3. Resolves the *voice* alias to a concrete *voice_id* (see
       :pyfunc:`_resolve_voice_id`).
    4. Calls the *text_to_speech.convert* endpoint and stores the resulting
       audio (an iterator of bytes) with :pyfunc:`elevenlabs.save`.
    """

    valid_api_key = findValidApiKey(text)
    if not valid_api_key:
        return None

    client = ElevenLabs(api_key=valid_api_key)
    voice_query = VOICE_MAP.get(voice, voice)
    voice_id = _resolve_voice_id(client, voice_query)

    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    save(audio_iter, output_file)
    return audio_iter

def generateSoundEffects(effect_description, output_file):
    """
    Generate sound effects using ElevenLabs Sound Effects API based on text description.
    
    Args:
        effect_description (str): Text description of the sound effect (e.g., "door creaking", "rain falling")
        output_file (str): Path where the generated audio file should be saved
        voice (str): Not used for sound effects, kept for compatibility
    
    Returns:
        audio: Generated audio data or None if failed
    """
    
    valid_api_key = findValidApiKey(effect_description)
    if not valid_api_key:
        return None

    client = ElevenLabs(api_key=valid_api_key)
    
    try:
        # Use the Sound Effects API instead of text-to-speech
        audio_iter = client.text_to_sound_effects.convert(
            text=effect_description
        )
        
        save(audio_iter, output_file)
        print(f"[util_audio_elevenlabs] Sound effect '{effect_description}' saved to {output_file}")
        return audio_iter
        
    except Exception as exc:
        print(f"[util_audio_elevenlabs] Error generating sound effect '{effect_description}': {exc}")
        return None

def _generateAudio(text, output_file, voice="Daniel", client: ElevenLabs | None = None):
    """Internal helper that performs the actual call to ElevenLabs.

    Parameters
    ----------
    text : str
        Text that will be synthesised.
    output_file : str
        Path where the audio will be stored.
    voice : str, optional
        Alias defined in *VOICE_MAP* (default: ``"Daniel"``).
    client : ElevenLabs, optional
        An initialised client.  If ``None`` the function will attempt to pick a
        valid API key and create its own client instance.
    """

    if voice not in VOICE_MAP:
        raise ValueError(f"Invalid voice: {voice}")

    if client is None:
        api_key = findValidApiKey(text)
        if not api_key:
            return None
        client = ElevenLabs(api_key=api_key)

    voice_query = VOICE_MAP[voice]
    voice_id = _resolve_voice_id(client, voice_query)

    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    save(audio_iter, output_file)
    return audio_iter

def _resolve_voice_id(client: ElevenLabs, voice_query: str) -> str:
    """Return a *voice_id* given either an ID or a human-readable name.

    The SDK requires a concrete voice_id.  If *voice_query* already looks like
    one (rough heuristic: alphanum and > 20 chars) we return it directly;
    otherwise we search the account's voices for the first match by name.
    """

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
                    print(f"[util_audio_elevenlabs] Found exact match for voice '{voice_query}': {voice.voice_id}")
                    return voice.voice_id
            
            # If no exact match, try partial match (case insensitive)
            voice_query_lower = voice_query.lower()
            for voice in search_result.voices:
                if voice_query_lower in voice.name.lower():
                    print(f"[util_audio_elevenlabs] Found partial match for voice '{voice_query}': {voice.name} ({voice.voice_id})")
                    return voice.voice_id
                    
            # If still no match, use first result
            first_voice = search_result.voices[0]
            print(f"[util_audio_elevenlabs] No exact match for '{voice_query}', using first result: {first_voice.name} ({first_voice.voice_id})")
            return first_voice.voice_id
            
    except Exception as exc:
        print(f"[util_audio_elevenlabs] Could not search voices for '{voice_query}': {exc}")

    # Try to get all voices and search manually
    try:
        all_voices = client.voices.get_all()
        if all_voices.voices:
            # Look for exact match first
            for voice in all_voices.voices:
                if voice.name == voice_query:
                    print(f"[util_audio_elevenlabs] Found exact match in all voices for '{voice_query}': {voice.voice_id}")
                    return voice.voice_id
            
            # Try partial match
            voice_query_lower = voice_query.lower()
            for voice in all_voices.voices:
                if voice_query_lower in voice.name.lower():
                    print(f"[util_audio_elevenlabs] Found partial match in all voices for '{voice_query}': {voice.name} ({voice.voice_id})")
                    return voice.voice_id
                    
            # List available voices for debugging
            print(f"[util_audio_elevenlabs] Available voices:")
            for voice in all_voices.voices[:10]:  # Show first 10
                print(f"  - {voice.name} ({voice.voice_id})")
                
            # Use first available voice as fallback
            fallback_voice = all_voices.voices[0]
            print(f"[util_audio_elevenlabs] No match found for '{voice_query}', using fallback: {fallback_voice.name} ({fallback_voice.voice_id})")
            return fallback_voice.voice_id
            
    except Exception as exc:
        print(f"[util_audio_elevenlabs] Could not get all voices: {exc}")

    # If all else fails, raise an error instead of passing invalid ID
    raise ValueError(f"Could not resolve voice '{voice_query}' to a valid voice ID. Please check the voice name or use a valid voice ID.")

def findValidApiKey(text):
    text_length = len(text)
    for api_key in API_KEYS:
        
        if getAPIWithPendingLimit(api_key, text_length):
            return api_key
    print("No valid API key found.")
    return None

def getAPIWithPendingLimit(api_key, text_length):
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"API key has {data['character_count']} characters used out of {data['character_limit']}")
        if data["character_count"] + text_length < data["character_limit"]:
            return True
    return False

if __name__ == "__main__":
    should_test_voice = False    
    if should_test_voice:
        print("Testing voice generation")
        text = "The quick brown fox jumps over the lazy dog."
        generateAudio(text, "/Users/admin_user/Documents/media/python_space/output/temp/test2.mp3")
    else:
        text = "A gunshot"
        print(f"Generating sound effect: {text}")
        generateSoundEffects(text, "/Users/admin_user/Documents/media/python_space/output/temp/gunshot.mp3")
