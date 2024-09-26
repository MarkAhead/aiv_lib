from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import numpy as np

from PIL import Image, ImageDraw, ImageFont
font_path = '/Users/yadubhushan/Documents/workplace/repo/social_media_bot_website/social_media_site/fonts/YoungSerif-Regular.ttf'

color_config = [
    {
        'dark': '#02343F',
        'light': '#F0EDCC' 
    },
    {
        'dark': '#331B3F',
        'light': '#ACC7B4'
    },
    {
        'dark': '#F0EDCC',
        'light': '#02343F'
    },
    {
        'dark': '#0A174E',
        'light': '#F5D042'
    },
    {
        'dark': '#07553B',
        'light': '#CED46A'
    },
    {
        'dark': '#50586C',
        'light': '#DCE2F0'
    },
    {
        'dark': '#815854',
        'light': '#F9EBDE'
    },
    {
        'dark': '#1E4174',
        'light': '#DDA94B'
    },
    {
        'dark': '#A4193D',
        'light': '#FFDFB9'
    },
    {
        'dark': '#101820',
        'light': '#FEE715'
    }
]


def color_hex_to_rgb(hex_color: str):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def get_average_color(image, x, y, width=100, height=100):
    """Get the average color of the area around (x, y) in the given image."""
    # Get image dimensions
    img_height, img_width, _ = image.shape

    # Ensure coordinates and area are within the image bounds
    x_start = max(x - width // 2, 0)
    y_start = max(y - height // 2, 0)
    x_end = min(x + width // 2, img_width)
    y_end = min(y + height // 2, img_height)

    # Extract the region and calculate the average color
    region = image[y_start:y_end, x_start:x_end]
    average_color = np.mean(region, axis=(0, 1))
    return tuple(int(c) for c in average_color)

def classify_color(image, x, y):
    color = get_average_color(image, x, y)
    
    """Classify the color as 'dark' or 'light'."""
    r, g, b = color
    # Convert to grayscale using luminance to better match human perception
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    print("luminance", luminance)
    return 'dark' if luminance < 88 else 'light'



def create_font_image(sentence: str, current_word_index, font_size: int, text_color: tuple, font_background_color: tuple, max_width: int):
    font = ImageFont.truetype(font_path, font_size)
    words = sentence.split()
    lines = []
    line = ''
    word_indices = []  # To track the index of each word in the lines
    max_text_width = 0  # To store the maximum text width

    # Create an image to calculate text size
    temp_image = Image.new('RGB', (max_width, 1))
    temp_draw = ImageDraw.Draw(temp_image)

    for index, word in enumerate(words):
        word_with_space = word + ' '
        test_line = line + word_with_space
        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        max_text_width = max(max_text_width, text_width)

        if text_width > max_width and line:
            lines.append(line)
            max_text_width = max(max_text_width, text_width)
            line = word_with_space
            word_indices.append(0)  # Starting a new line, so index is 0
        else:
            line += word_with_space
            word_indices.append(len(line.split()) - 1)
        
    lines.append(line)  # Add the last line if any

    # Calculate the total height of the text
    line_height = temp_draw.textbbox((0, 0), 'Ay', font=font)[3]  # 'Ay' gives max height
    text_height = len(lines) * line_height

    # Calculate a light and translucent version of the font_background_color
    # Increase each color component to make it lighter, and add an alpha value for translucency
    bg_color = tuple(int(c + (255 - c) * 0.4) for c in font_background_color[:3]) + (int(255 * 0.6),)
    
    image = Image.new('RGBA', (max_text_width, text_height), bg_color)  # Transparent background
    draw = ImageDraw.Draw(image)
    
    y_text = 0
    highlight_index = 0
    for line_index, line in enumerate(lines):
        x_text = 0
        for word_index, word in enumerate(line.split()):
            word_with_space = word + ' '
            bbox = draw.textbbox((x_text, y_text), word_with_space, font=font)
            word_width = bbox[2] - bbox[0]

            if highlight_index == current_word_index:
                # Draw background for the current word
                draw.rectangle((x_text, y_text, x_text + word_width, y_text + line_height), fill=font_background_color)
            draw.text((x_text, y_text), word, font=font, fill=text_color)
            highlight_index += 1
            x_text += word_width

        y_text += line_height

    return image


def get_screen_position(screen_image, position='center', caption_image=None):
    # Assume screen_image is a numpy array and get its dimensions
    height, width = screen_image.shape[:2]

    # padding is 10% of the screen width
    padding = width * 0.15
    x = 0
    y = 0

    caption_width = caption_image.width if caption_image else 0
    caption_height = caption_image.height if caption_image else 0
    print("width and height of screen", width, height)
    print("width and height of caption", caption_width, caption_height)
    if position == 'top':
        x = (width - caption_width) // 2
        y = int(padding)
    elif position == 'center':
        x = (width - caption_width) // 2
        y = (height - caption_height) // 2
    elif position == 'bottom':
        x = (width - caption_width) // 2
        y = height - caption_height - int(padding)

    return x, y



def create_movie_overlay(sentences_data: list, font_size: int, text_color: tuple, font_background_color: tuple, output_path: str):
    video = VideoFileClip(video_path)
    fps = video.fps if video.fps else 30
    print(f"FPS set to: {fps}")

    clips = [video]  # Keep the entire video as the base layer
    image_max_width = int(video.size[0] - video.size[0] * 0.3)


    text_color_to_use = text_color
    font_background_color_to_use = font_background_color

    for item in sentences_data:
        sentence = item['text']
        start_time = item['start']
        end_time = item['end']

            
        print(f"Processing sentence: {sentence} from {start_time} to {end_time}")

        total_display_duration = end_time - start_time
        sample_frame = video.get_frame(start_time)
        
        x_to_use, y_to_use = get_screen_position(sample_frame, 'bottom', caption_image=None)
        print(f"Position: for image average {x_to_use}, {y_to_use}")

        color_class = classify_color(sample_frame, x_to_use, y_to_use)
        print(f"Color class: {color_class}")
        if color_class == 'light':
            text_color_to_use = font_background_color
            font_background_color_to_use = text_color
    
        # if item has 'words' in it
        if 'words' in item:
            words = item['words']
        else:
            words = sentence.split()
        
        print(f"Words: {words}")
        display_time_per_word = total_display_duration / len(words)
        print(f"Display time per word: {display_time_per_word}")

        current_sentence = ""
        for index, word in enumerate(words):
            image = create_font_image(sentence, index, font_size, text_color_to_use, font_background_color_to_use, image_max_width)
            temp_path = f'temp_{int(index)}_{sentence}.png'
            image.save(temp_path)

            # Each word appears at its designated time and remains until the end_time
            x_to_use, y_to_use = get_screen_position(sample_frame, 'bottom', caption_image=image)
            print(f"Position: for image {x_to_use}, {y_to_use}")
            if "start" in word:
                start_time = word["start"]
            
            if "end" in word:
                if index + 1 < len(words):
                    duration = words[index + 1]["start"] - word["start"]
                else:
                    duration =  word["end"] - word["start"]
            else:
                duration = display_time_per_word
            
            txt_clip = ImageClip(temp_path).set_duration(duration).set_start(start_time).set_position((x_to_use, y_to_use))
            clips.append(txt_clip)

            start_time += duration

    final_clip = CompositeVideoClip(clips)

    final_clip.write_videofile(output_path, codec="libx264", fps=fps)




from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

# Load the video
video_path = '/Users/yadubhushan/Downloads/20433217-hd_1920_1080_30fps.mp4'
#video_path = '/Users/yadubhushan/Downloads/623064168.mp4'

subtitle_config = {
    'font_size' : 40,
    'text_color' : (255, 255, 255),
    'font_background_color' : (0, 0, 0),
    'arrangement': 'bottom',
}



sentences_data = [
    {
        "start": 6.735,
        "end": 7.736,
        "text": " Is this all to life?",
        "words": [
            {
                "word": "Is",
                "start": 6.735,
                "end": 6.815,
                "score": 0.834
            },
            {
                "word": "this",
                "start": 6.855,
                "end": 7.015,
                "score": 0.863
            },
            {
                "word": "all",
                "start": 7.115,
                "end": 7.215,
                "score": 0.82
            },
            {
                "word": "to",
                "start": 7.235,
                "end": 7.395,
                "score": 0.753
            },
            {
                "word": "life?",
                "start": 7.476,
                "end": 7.736,
                "score": 0.89
            }
        ]
    },
    {
        "start": 7.876,
        "end": 8.696,
        "text": "What's the design?",
        "words": [
            {
                "word": "What's",
                "start": 7.876,
                "end": 8.036,
                "score": 0.408
            },
            {
                "word": "the",
                "start": 8.076,
                "end": 8.156,
                "score": 0.798
            },
            {
                "word": "design?",
                "start": 8.196,
                "end": 8.696,
                "score": 0.791
            }
        ]
    },
    {
        "start": 9.056,
        "end": 19.74,
        "text": "Invincible as rhyme, my story intertwined Echoes of the past in my mind In the city's cold embrace I seek change Through the shadows I range",
        "words": [
            {
                "word": "Invincible",
                "start": 9.056,
                "end": 9.776,
                "score": 0.705
            },
            {
                "word": "as",
                "start": 9.836,
                "end": 9.916,
                "score": 0.473
            },
            {
                "word": "rhyme,",
                "start": 10.036,
                "end": 10.257,
                "score": 0.456
            },
            {
                "word": "my",
                "start": 10.277,
                "end": 10.397,
                "score": 0.47
            },
            {
                "word": "story",
                "start": 10.417,
                "end": 10.837,
                "score": 0.752
            },
            {
                "word": "intertwined",
                "start": 10.917,
                "end": 11.677,
                "score": 0.55
            },
            {
                "word": "Echoes",
                "start": 12.177,
                "end": 12.437,
                "score": 0.428
            },
            {
                "word": "of",
                "start": 12.537,
                "end": 12.597,
                "score": 0.664
            },
            {
                "word": "the",
                "start": 12.657,
                "end": 12.877,
                "score": 0.513
            },
            {
                "word": "past",
                "start": 12.937,
                "end": 13.258,
                "score": 0.827
            },
            {
                "word": "in",
                "start": 13.378,
                "end": 13.458,
                "score": 0.37
            },
            {
                "word": "my",
                "start": 13.498,
                "end": 13.698,
                "score": 0.699
            },
            {
                "word": "mind",
                "start": 13.778,
                "end": 14.158,
                "score": 0.716
            },
            {
                "word": "In",
                "start": 15.098,
                "end": 15.178,
                "score": 0.952
            },
            {
                "word": "the",
                "start": 15.198,
                "end": 15.298,
                "score": 0.807
            },
            {
                "word": "city's",
                "start": 15.458,
                "end": 15.799,
                "score": 0.651
            },
            {
                "word": "cold",
                "start": 15.859,
                "end": 16.079,
                "score": 0.857
            },
            {
                "word": "embrace",
                "start": 16.139,
                "end": 16.619,
                "score": 0.83
            },
            {
                "word": "I",
                "start": 16.739,
                "end": 16.799,
                "score": 0.548
            },
            {
                "word": "seek",
                "start": 16.879,
                "end": 17.139,
                "score": 0.692
            },
            {
                "word": "change",
                "start": 17.219,
                "end": 17.699,
                "score": 0.879
            },
            {
                "word": "Through",
                "start": 18.299,
                "end": 18.479,
                "score": 0.562
            },
            {
                "word": "the",
                "start": 18.499,
                "end": 18.6,
                "score": 0.938
            },
            {
                "word": "shadows",
                "start": 18.72,
                "end": 19.2,
                "score": 0.902
            },
            {
                "word": "I",
                "start": 19.28,
                "end": 19.4,
                "score": 0.297
            },
            {
                "word": "range",
                "start": 19.48,
                "end": 19.74,
                "score": 0.748
            }
        ]
    }
]

# Load your custom font
font_size = 40
font_background_color = (0, 0, 0)
output_video_path = 'output_video.mp4'
i = 0
for color in color_config[:1]:
    text_color = color_hex_to_rgb(color['light'])
    font_background_color = color_hex_to_rgb(color['dark'])
    output_video_path = f'output_video_{i}.mp4'
    i += 1
    create_movie_overlay(sentences_data, font_size, text_color, font_background_color, output_video_path)
    

    



