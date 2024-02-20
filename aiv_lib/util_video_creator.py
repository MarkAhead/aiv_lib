from moviepy.editor import *
import cv2
import traceback
import json
from PIL import Image
import numpy as np
from PIL import Image
import numpy as np
from .util_ConfigManager import get_config_value

python_space = get_config_value("python_space")


width = 1080
height = 1920
text_start_width_position = 100  # Starting width posit

max_width = 800
base_height = height*0.65
font_name = "YoungSerif-Regular"

# font_color = "#F3AA60"
# bg_color='#1D5B79'

# font_color = "#EE9322"
# bg_color='#219C90'

font_color = "#EEEEEE"
bg_color='#222831'

font_size = 55

from .cloud_gcp_storage import download_blob_with_remote_path

resouces_folder = os.path.join(python_space, "resources")
front_page_video_template = os.path.join(resouces_folder ,  'social, motivation_template, front_page_1.mp4')
swoosh_sound = os.path.join(resouces_folder ,  "sounds, swoosh-transition.mp3")

fps_to_use = 24

def zoom_effect(t, frame, original_size, width, height):
    zoom_factor = 1 + 0.03*t
    center_x, center_y = original_size[0] / 2, original_size[1] / 2

    # Calculate the size of the cropped region based on the zoom factor
    crop_width = original_size[0] / zoom_factor
    crop_height = original_size[1] / zoom_factor

    # Calculate the top-left corner coordinates of the cropped region
    x1 = center_x - crop_width / 2
    y1 = center_y - crop_height / 2

    # Crop the frame to create the zoom effect
    cropped_frame = frame[int(y1):int(y1+crop_height), int(x1):int(x1+crop_width)]

    # Resize the cropped frame to the original size
    return cv2.resize(cropped_frame, (width, height))
    


def getFrontPageVideoClip(audio_path, video_title) :
    audio_clip = AudioFileClip(audio_path)
    text_clip_duration = audio_clip.duration 


    front_video = VideoFileClip(front_page_video_template)  # Use VideoFileClip to load the video
    front_video = front_video.subclip(0, text_clip_duration)  # Trim the video to the duration of the text clip

    text_clip = TextClip(
        video_title,
        fontsize=70,
        font = "Lane",
        color="white",
        size=(800, 0),
        method="caption",
        align="center",
    )
    text_clip = text_clip.set_position(("center", "center"))
    text_clip = text_clip.set_duration(text_clip_duration)
    tc_width, tc_height = text_clip.size

    color_clip = ColorClip(size=(tc_width + 70, tc_height + 30), color=(0, 0, 0))


    final_clip = CompositeVideoClip([color_clip, text_clip])
    final_clip = final_clip.set_duration(text_clip.duration)  # Set the duration for final_clip
    final_clip = final_clip.set_position('center' , "center")  # Set the position of the text
    final_clip = final_clip.set_opacity(0.3)
    final_clip = final_clip.set_audio(audio_clip)
    final_clip = final_clip.crossfadein(1)


    final_output_video = CompositeVideoClip([front_video, final_clip])
    final_output_video = final_output_video.set_duration(text_clip_duration)  # Set the total duration
    return final_output_video



from PIL import Image
import numpy as np

def horizontal_scroll(input_file, audio_duration, fps, toggle=True):
    # Load your image (replace 'your_image.jpg' with the path to your image)
    img = Image.open(input_file)
    img_width, img_height = img.size

    # Define the screen size and calculate the scaling factor
    screen_width = 1080  # For a 9:16 aspect ratio
    screen_height = 1920
    scaling_factor = screen_height / img_height
    img = img.resize((int(img_width * scaling_factor), screen_height))

    # Convert the image to a numpy array
    img_np = np.array(img)

    # Calculate the number of steps needed for the given audio duration (based on the fps)
    steps = int(audio_duration * fps)

    # Calculate the step size for horizontal scrolling
    step_size = int((img_width * scaling_factor - screen_width) / steps)

    # List to store frames
    frames = []

    for i in range(steps):
        # If toggle is True, scan from left to right, else right to left
        if toggle:
            frame = img_np[:, i*step_size:i*step_size+screen_width]
        else:
            start_index = int(img_width * scaling_factor - (i + 1) * step_size - screen_width)
            end_index = int(img_width * scaling_factor - (i + 1) * step_size)
            frame = img_np[:, start_index:end_index]

        # Add frame to list
        frames.append(frame)

    return frames


def create_movie(output_folder, prompt_data):
    original_aspect_ratio = 1
    socialMediaPost = prompt_data['socialMediaPost']
    pages = socialMediaPost['scenes']
    clips = []
    toggle = True
    for entry in pages:
        img_clip = ImageClip(download_blob_with_remote_path(entry['selected_image_path'], output_folder))
        img_array = np.array(img_clip.get_frame(0))
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack((img_array,)*3, axis=-1)
            original_aspect_ratio = img_clip.size[0] / img_clip.size[1]
        img_clip = ImageClip(img_array)
        desired_aspect_ratio = 9 / 16
        audio_clip = AudioFileClip(download_blob_with_remote_path(entry['audio_path'], output_folder))

        if original_aspect_ratio >= 1:  # wide image
            # Apply horizontal scroll effect
            frames = horizontal_scroll(download_blob_with_remote_path(entry['selected_image_path'], output_folder), audio_clip.duration, 24, toggle)
            img_clip = ImageSequenceClip(frames, fps=fps_to_use)  # Assuming 24 fps, adjust as necessary
            toggle = not toggle

        else:  # tall image
            # Apply zoom effect
            if original_aspect_ratio > desired_aspect_ratio:
                img_clip = img_clip.resize(width=width)
            else:
                img_clip = img_clip.resize(height=height)
            
            img_clip = img_clip.on_color(size=(width, height), color=(0,0,0), pos=('center', 'center'))
            img_clip = img_clip.fl(lambda gf, t: zoom_effect(t, gf(t), img_clip.size, width, height))

        #swoosh_sound_clip = AudioFileClip(swoosh_sound)
        silence = AudioClip(lambda t: [0, 0], duration=2, fps=audio_clip.fps)
        audio_clip = concatenate_audioclips([audio_clip, silence])
        
        img_clip = img_clip.set_duration(audio_clip.duration)
        
        # Composite video clip with text
        img_clip = CompositeVideoClip([img_clip])
        
        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip.crossfadein(1))

    final_clip = concatenate_videoclips(clips, method="compose", padding=-1)
    output_video_file = os.path.join(output_folder, "video.mp4")
    final_clip.write_videofile(output_video_file, fps=fps_to_use)

    return output_video_file

# Function to group words into lines and lines into groups
def wrap_words_into_lines(words, max_width):
    line_groups = []
    current_line = []
    current_group = []
    current_width = 0

    for word in words:
        text_clip = TextClip(word=font_size, color=font_color, bg_color=bg_color, font=font_name)
        word_clip_width, word_clip_height = text_clip.size

        if current_width + word_clip_width > max_width:
            current_group.append(current_line)
            current_line = []
            current_width = 0
            
            if len(current_group) == 2:  # If two lines have been added to the current group
                line_groups.append(current_group)
                current_group = []

        current_line.append(word)
        current_width += word_clip_width

    if current_line:  # Append the last line if it's not empty
        current_group.append(current_line)

    if current_group:  # Append the last group if it's not empty
        line_groups.append(current_group)
    
    return line_groups

def write_to_box_at_height_y(input_line, initial_y,  box_color=None, max_width=900, font_size=70, font_color=None, font_name="Lane", bg_color="black"):
        words = input_line.split()
        line_groups = wrap_words_into_lines(words, max_width)
        lines = [' '.join(line) for group in line_groups for line in group]
        total_height = sum([TextClip(txt, fontsize=font_size, color=font_color, font=font_name).size[1] for txt in lines])
        y_to_use = initial_y
        text_clips = [] 
        for text in lines: 
            text_clip = TextClip(text, fontsize=font_size, color=font_color, bg_color=bg_color, font=font_name)
            text_clip_width, text_clip_height = text_clip.size
            y_to_use = y_to_use + text_clip_height
            x_to_use = (width - text_clip_width) / 2

            text = text.set_position((x_to_use, y_to_use))
            text_clips.append(text)
        
        # Create the text clips and concatenate them vertically to create the complete text box
        text_clips = [TextClip(txt, fontsize=font_size, color=font_color, font=font_name, size=(max_width, None)).set_position(('center', 'center')) for txt in lines]
        text_box = CompositeVideoClip(text_clips, size=(max_width, total_height)).set_position(('center', 'center'))


# Function to group words into lines and lines into groups
def group_words_into_lines(words, max_width):
    line_groups = []
    current_line = []
    current_group = []
    current_width = 0

    for word_seq in words:
        text_clip = TextClip(word_seq['word'], fontsize=font_size, color=font_color, bg_color=bg_color, font=font_name)
        word_clip_width, word_clip_height = text_clip.size

        if current_width + word_clip_width > max_width:
            current_group.append(current_line)
            current_line = []
            current_width = 0
            
            if len(current_group) == 2:  # If two lines have been added to the current group
                line_groups.append(current_group)
                current_group = []

        current_line.append(word_seq)
        current_width += word_clip_width

    if current_line:  # Append the last line if it's not empty
        current_group.append(current_line)

    if current_group:  # Append the last group if it's not empty
        line_groups.append(current_group)
    
    return line_groups

last_end = 0  # Initialize the end time of the last word

def create_text_for_line(line, height, end_time):
    global last_end
    texts = []
    last_x = text_start_width_position
    for word_seq in line:
        try:
            if 'word' not in word_seq:
                print(f"Invalid word: {word}")
                continue
            if 'start' not in word_seq:
                word_seq['start'] = last_end + 0.2
            if 'end' not in word_seq:
                word_seq['end'] = last_end + 0.8
            word = word_seq['word']
            start = word_seq['start']
            end =  word_seq['end']
            # validate if word has start end and word

            text = TextClip(word, fontsize=font_size, color=font_color, bg_color=bg_color, font=font_name)
            text_clip_width, text_clip_height = text.size
            x = last_x + 10 + text_clip_width

            text = text.set_position((last_x, height)).set_duration(end_time - start).set_start(start)
            last_x = x
            texts.append(text)
            last_end = end  # Update the end time of the last word
        except Exception as e:
                print(f"Error occurred with word '{word}' (start: {start}, end: {end}): {e}")


    return texts

def create_text_for_group(group):
    end_time = group[-1][-1]['end']
    texts = []
    for j, line in enumerate(group):
        line_text = create_text_for_line(line, base_height + j * 100, end_time)
        texts.extend(line_text)
    return texts

def create_text_for_line_group(line_groups):
    texts = []
    for i, group in enumerate(line_groups):
        group_text = create_text_for_group(group)
        texts.extend(group_text)
    return texts


def generate_video_with_subtitle_multiline(subtitle_data, video_file_path, output_file_path):
    """
    subtitle_data: JSON string with subtitle data
    video_file_path: Path to the video file
    output_file_path: Path to the output video file
    """
    print("Generating video with subtitle....")
    data = json.loads(subtitle_data)
    video = VideoFileClip(video_file_path)
    video_width, video_height = video.size
    # Step 3: Create text clips for each word
    text_clips = []
    for sentence in data:
        words = sentence['words']
        line_groups = group_words_into_lines(words, max_width)
        texts = create_text_for_line_group(line_groups)
        text_clips.extend(texts)

    # Step 4: Create a composite video clip with the original video and all the text clips
    try:
        video = CompositeVideoClip([video] + text_clips)
    except Exception as e:
        print(f"Error occurred during video composition: {e}")
        exit(1)

    print("FPS before setting:", video.fps)  # Debug statement to print the FPS before setting it
    video.fps = fps_to_use  # Set the fps attribute manually on the video object
    print("FPS after setting:", video.fps)  # Debug statement to print the FPS after setting it

    try:
        video.write_videofile(output_file_path, codec='libx264', fps=24)  # Pass the fps value directly
    except Exception as e:
        print(f"Error occurred during video writing: {e}")
        print("Stack Trace:")
        traceback.print_exc()
        exit(1)
    print("Video file created successfully at : ", output_file_path)

def generate_video_with_subtitle(subtitle_data, video_file_path, output_file_path):
    """
    subtitle_data: JSON string with subtitle data
    video_file_path: Path to the video file
    output_file_path: Path to the output video file
    """
    print("Generating video with subtitle....")
    data = json.loads(subtitle_data)
    # Step 2: Open the MP4 file
    video = VideoFileClip(video_file_path)

    video_width, video_height = video.size

    # Step 3: Create text clips for each word
    text_clips = []
    for sentence in data:
        for word in sentence['words']:
            # validate if word has start end and word
            if 'start' not in word or 'end' not in word or 'word' not in word:
                print(f"Invalid word: {word}")
                continue


            start_time = word['start']
            end_time = word['end']
            text = word['word']
            
            try:
                # Create a text clip with the correct duration
                text_clip = (TextClip(text, fontsize=70, color='yellow3', bg_color='black', font='Courier')
                             .set_start(start_time)
                             .set_end(end_time)
                             .set_duration(end_time - start_time))

                text_clip_width, text_clip_height = text_clip.size

                # Position the text clip at the bottom of the video
                text_clip = text_clip.set_position(addPositionToText('bottom', (video_width, video_height), text_clip.size, padding=10))
                
                # Add the text clip to the list
                text_clips.append(text_clip)
            except Exception as e:
                print(f"Error occurred with word '{text}' (start: {start_time}, end: {end_time}): {e}")

    # Step 4: Create a composite video clip with the original video and all the text clips
    try:
        video = CompositeVideoClip([video] + text_clips)
    except Exception as e:
        print(f"Error occurred during video composition: {e}")
        exit(1)

    print("FPS before setting:", video.fps)  # Debug statement to print the FPS before setting it
    video.fps = fps_to_use  # Set the fps attribute manually on the video object
    print("FPS after setting:", video.fps)  # Debug statement to print the FPS after setting it

    try:
        video.write_videofile(output_file_path, codec='libx264', fps=24)  # Pass the fps value directly
    except Exception as e:
        print(f"Error occurred during video writing: {e}")
        print("Stack Trace:")
        traceback.print_exc()
        exit(1)
    print("Video file created successfully at : ", output_file_path)


# Helper function to add position to text
def addPositionToText(pos, video_size, text_size, padding = 0) -> (int, int) : 
    video_width, video_height = video_size
    text_width, text_height = text_size
    if pos == 'bottom' : 
        x = video_width/2 - text_width/2
        y = (video_height * 0.8) - text_height - padding
        return (x, y)

    if pos == 'top' : 
        x = video_width/2 - text_width/2
        y = padding
        return (x, y)

    if pos == 'center' :
        x = video_width/2 - text_width/2
        y = video_height/2 - text_height/2
        return (x, y)


def get_audio_from_video(video_file, filename = "audio.mp3"):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio_file = os.path.join(os.path.dirname(video_file), filename)
    audio.write_audiofile(audio_file)
    return audio_file
