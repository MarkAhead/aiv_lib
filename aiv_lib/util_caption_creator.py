import os
from PIL import Image, ImageDraw, ImageFont
import uuid
import cv2
import shutil


CX = get_config_value("GOOGLE_SEARCH_CX")
PEXELS_API_KEY = get_config_value("PEXELS_API_KEY")

def adjust_font_size(draw, quote, image_width, font_loc, initial_font_size=70):
    font_size = initial_font_size
    while font_size > 10:
        try:
            font = ImageFont.truetype(font_loc, font_size)
        except IOError:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), quote, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= image_width:
            return font, bbox
        
        font_size -= 1
    return font, bbox

def add_quote_to_image(output_folder, input_filepath, opacity, quote):
    # Load the image
    img = Image.open(input_filepath)
    
    # Define the quote and split it into lines 

    quotes = quote.split("\n")
    
    # Add opacity over the entire image
    opacity_layer = Image.new('RGBA', img.size, (0, 0, 0, opacity))  # 40% opacity
    img = Image.alpha_composite(img.convert('RGBA'), opacity_layer)
    
    draw = ImageDraw.Draw(img)
    font, bbox = adjust_font_size(draw, quote, img.width, font_loc)
    
    # Calculate total height of the text block
    total_text_height = len(quotes) * (font.getbbox(quotes[0])[3] - font.getbbox(quotes[0])[1] + 5)
    
    # Calculate starting y position for center-aligning the quote vertically
    y = (img.height - total_text_height) / 2
    
    # Draw each line of the quote over the image
    for line in quotes:
        text_width = font.getlength(line)
        x = (img.width - text_width) / 2  # Center-align horizontally
        draw.text((x, y), line, font=font, fill="white")
        y += font.getbbox(line)[3] - font.getbbox(line)[1] + 5  # 5 is spacing between lines
    
    # Save the new image
    output_filepath = os.path.join(output_folder, f"image_{opacity}.png")
    img.save(output_filepath)
    
    return output_filepath


def create_images_with_opacity(input_filepath, output_folder, font_loc, quote):
    opacities = list(range(10, 300, 10))
    for opacity in opacities:
        add_quote_to_image(output_folder, input_filepath, opacity, quote)

    

def images_to_video(image_folder, video_output_file, fps=30, rotate = True):
    """
    Convert images in 'image_folder' to a video named 'video_output_file' with 'fps' frames per second.
    """
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()  # Make sure images are in the correct order
    
    # Custom sorting function
    images.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    if rotate:
        # Create a new collection with forward and reverse sorted images
        images = images + images[::-1]
    # Determine the width and height from the first image

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    h, w, layers = frame.shape
    size = (w, h)

    out = cv2.VideoWriter(video_output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for image in images:
        img_path = os.path.join(image_folder, image)
        img = cv2.imread(img_path)
        out.write(img)

    out.release()

posts_base_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta/bollywood"
font_loc = "/Users/yadubhushan/Documents/media/python_space/resources/font/Handlee-Regular.ttf"
input_filepath = os.path.join(posts_base_dir, "Shahrukh.png.png")




def create_insta_posts(base_file_path):
    pass



unique_folder_name = str(uuid.uuid4())
output_folder = os.path.join(posts_base_dir, unique_folder_name)
os.makedirs(output_folder, exist_ok=True)

# Example usage:

quote = "Life is abundant, and life is beautiful. \n And it's a good place that we're all in, \n you know, on this earth, if we take care of it."

# Create images with opacity
create_images_with_opacity(input_filepath, output_folder, font_loc, quote)
video_output_path = os.path.join(posts_base_dir, "output_" + str(unique_folder_name) + ".mp4")
images_to_video(output_folder, video_output_path, fps=5)

# print(f"New Video saved at: {video_output_path}")
# shutil.rmtree(output_folder)


# update the above code to create a new unique folder (use uuid) inside posts_base_dir and use the input_filepath
# to create images with quotes and a series of opacity with opacity starting from 0 to 100 and then 100 to 0
# and then create a video out of it inside posts_base_dir and then delete the folder