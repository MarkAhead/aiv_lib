
# Open AI transcribe api with granularity of 100ms

def transcribe_audio(audio_file_path):
    from openai import OpenAI
    
    client = OpenAI()
    with open(audio_file_path, "rb") as audio:
        response = client.audio.transcriptions.create(file=audio_file_path,
                                                      model="whisper-1",
                                                      response_format="verbose_json",
                                                      timestamp_granularities=["word"])
        return response


