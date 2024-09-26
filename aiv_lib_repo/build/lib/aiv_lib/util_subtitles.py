import json
import os
import sys
from aiv_lib.util_ConfigManager import get_config_value
from aiv_lib.cloud_gcp_storage import download_blob_with_remote_path
output_dir = get_config_value("output_folder") + "social/"
local_output_folder = None
import re
import gc 

def convertAudioToSubtitle(audio_file, shorten_segment=False):
    import whisperx
    
    device = "cpu" 
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result["segments"]) # before alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    print(result["segments"]) # after alignment
    if shorten_segment:
        result["segments"] = segment_data_with_text(result["segments"], 8)
        print("After shortening the segments : ", result["segments"])
    return result["segments"]

def segment_data_with_text(data, max_words_per_segment):
    if not isinstance(data, list) or not isinstance(max_words_per_segment, int) or max_words_per_segment <= 0:
        raise ValueError("Invalid input: data must be a list and max_words_per_segment must be a positive integer")

    segments = []
    all_words = [word for item in data for word in item['words'] if isinstance(item, dict) and 'words' in item and all(isinstance(word, dict) for word in item['words'])]

    for i in range(0, len(all_words), max_words_per_segment):
        segment_words = all_words[i:i + max_words_per_segment]
        if not segment_words:
            continue  # Skip empty segment_words

        # Fill missing start/end times
        for j, word in enumerate(segment_words):
            if 'start' not in word or 'end' not in word:
                prev_end = segment_words[j - 1]['end'] if j > 0 else word.get('start', 0)
                next_start_index = j + 1 if j + 1 < len(segment_words) else i + max_words_per_segment
                next_start = all_words[next_start_index]['start'] if next_start_index < len(all_words) else word.get('end', prev_end)

                word['start'] = word.get('start', (prev_end + next_start) / 2)
                word['end'] = word.get('end', (prev_end + next_start) / 2)

        segment_text = ' '.join(word['word'] for word in segment_words)
        segment = {
            'start': segment_words[0]['start'],
            'end': segment_words[-1]['end'],
            'text': segment_text,
            'words': segment_words
        }
        segments.append(segment)

    return segments


def convertSrtToWhisperOutput(srt_file):
    with open(srt_file, 'r') as file:
        srt_data = file.read()

    pattern = re.compile(r'\d+\n(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})\n(.*?)\n', re.DOTALL)

    output_data_array = []

    # Find all matches and convert them to JSON format
    for match in pattern.finditer(srt_data):
        start_hours, start_minutes, start_seconds, start_milliseconds, \
        end_hours, end_minutes, end_seconds, end_milliseconds, text = match.groups()

        start_time = int(start_hours) * 3600 + int(start_minutes) * 60 + int(start_seconds) + int(start_milliseconds) / 1000
        end_time = int(end_hours) * 3600 + int(end_minutes) * 60 + int(end_seconds) + int(end_milliseconds) / 1000

        output_data_array.append({
            'start': round(start_time, 3),
            'end': round(end_time, 3),
            'text': text.strip().replace('\n', ' ')
        })

    return output_data_array


if __name__ == "__main__":
    test_data = [
        {
            "words": [
                {"word": "Hello", "end": 1.5},  # No start time
                {"word": "world", "start": 1.5, "end": 3.0},
                {"word": "this", "start": 3.0, "end": 4.0},
                {"word": "is", "start": 4.0, "end": 5.0},
                {"word": "a", "start": 5.0, "end": 6.0},
                {"word": "test", "start": 6.0}  # No end time
            ]
        },
        {
            "words": [
                {"word": "Another", "start": 6.5, "end": 7.0},
                {"word": "sentence", "start": 7.0, "end": 8.0},
                {"word": "without", "end": 9.0},  # No start time
                {"word": "start", "start": 9.0, "end": 10.0}
            ]
        },
        {
            "words": [
                {"word": "Final", "end": 11.0},  # No start time
                {"word": "segment", "start": 11.0}  # No end time
            ]
        }
    ]
    segmented_data = segment_data_with_text(test_data, 3)  # Test with max_words_per_segment = 3
    for segment in segmented_data:
        print(segment)
