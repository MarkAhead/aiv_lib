from elevenlabs import generate, save, set_api_key
from .util_ConfigManager import get_config_value
import requests

VOICE_MAP = {
    "Daniel": "Daniel",
    "Markus": "Markus - Mature and Chill",
    "Sally": "Sally - very realistic, super",
    "Daksh": "Daksh - Suspenseful and Gripping Voice"
}

API_KEYS = [
    get_config_value("eleven_labs_api_key_uday"),
]



def generateHindiAudio(text, output_file):
    return generateAudio(text, output_file, "Daksh")

def generateMaleAudio(text, output_file):
    return generateAudio(text, output_file, "Markus")



def generateFemaleAudio(text, output_file):
    return generateAudio(text, output_file, "Sally")


def generateAudio(text, output_file, voice = "Markus"): 
    valid_api_key = findValidApiKey(text)
    if valid_api_key:
        set_api_key(valid_api_key)
        return _generateAudio(text, output_file, voice)
    return None

def generateSoundEffects(effect_description, output_file, voice="Daniel"):
    """
    Generate sound effects using ElevenLabs TTS based on text description.
    
    Args:
        effect_description (str): Text description of the sound effect (e.g., "door creaking", "rain falling")
        output_file (str): Path where the generated audio file should be saved
        voice (str): Voice to use for generating the effect (default: "Daniel")
    
    Returns:
        audio: Generated audio data or None if failed
    """
    # Format the description for sound effect generation
    formatted_text = f"Sound effect: {effect_description}"
    
    valid_api_key = findValidApiKey(formatted_text)
    if valid_api_key:
        set_api_key(valid_api_key)
        return _generateAudio(formatted_text, output_file, voice)
    return None

def _generateAudio(text, output_file, voice = "Daniel"): 
    if voice not in VOICE_MAP:
        raise ValueError(f"Invalid voice: {voice}")
    audio = generate(
        text = text,
        voice=VOICE_MAP[voice],
        model="eleven_multilingual_v2"
    )
    save(audio, output_file)
    return audio    



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
    text = "The quick brown fox jumps over the lazy dog."
    generateAudio(text, "/Users/yadubhushan/Documents/media/python_space/output/temp/test2.mp3")
