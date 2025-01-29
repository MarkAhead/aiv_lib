
from faster_whisper import WhisperModel
model_size = "large-v3"
import numpy as np

model = WhisperModel(model_size, device="cpu", compute_type="int8")

def convert_to_list(segments):
    segment_list = []
    text_data = ""
    for segment in segments:
        # Convert words into dictionaries and ensure NumPy types are converted
        words_list = []
        if segment.words is not None:
            for word in segment.words:
                words_list.append({
                    "start": float(word.start),  # Convert np.float64 to float
                    "end": float(word.end),    # Convert np.float64 to float
                    "word": word.word,
                })
        
        # Convert Segment object into a dictionary
        segment_dict = {
            "id": segment.id,
            "seek": segment.seek,
            "start": float(segment.start),  # Convert np.float64 to float
            "end": float(segment.end),      # Convert np.float64 to float
            "text": segment.text,
            "words": words_list,
        }
        segment_list.append(segment_dict)
        text_data += segment.text + " "
    return segment_list, text_data

def transcribe_audio(audio_file):
    segments, info = model.transcribe(audio_file, beam_size=5, word_timestamps=True)
    return convert_to_list(segments)


if __name__ == "__main__":
    audio_file = "/Users/yadubhushan/Downloads/phil_ceef23117b67cc9722ba88932fb04b6a7e7b9e125eb2fefa3af8fddaa9589a32_Social_18_mono.wav"
    segments, info = transcribe_audio(audio_file)
    for segment in segments:
        print(segment.text)