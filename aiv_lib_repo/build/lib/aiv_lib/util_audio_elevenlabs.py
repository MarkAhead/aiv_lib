from elevenlabs import generate, save, set_api_key
from .util_ConfigManager import get_config_value
import requests


API_KEYS = [
    get_config_value("ELEVEN_LABS_API_KEY_Family"),
]


def generateMaleAudio(text, output_file):
    audio = generate(
        text = text,
        voice="Markus - Mature and Chill",
        model="eleven_multilingual_v2"
    )
    save(audio, output_file)
    return audio


def generateFemaleAudio(text, output_file):
    audio = generate(
        text = text,
        voice="Sally - very realistic, super",
        model="eleven_multilingual_v2"
    )
    save(audio, output_file)
    return audio


def generateAudio(text, output_file, voice = "Daniel"): 
    valid_api_key = findValidApiKey(text)
    if valid_api_key:
        set_api_key(valid_api_key)
        audio = generate(
            text = text,
            voice="Daniel",
            model="eleven_multilingual_v2"
        )
        save(audio, output_file)
        return audio
    else:
        print("No valid API key found.")
        return None

def findValidApiKey(text):
    text_length = len(text)
    for api_key in API_KEYS:
        if getAPIWithPendingLimit(api_key, text_length):
            return api_key
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
