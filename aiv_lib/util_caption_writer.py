import json
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
image_width, image_height = 1080, 1080
from .util_ConfigManager import get_config_value

caption_font_size = 50
watermark_font_size = 24
font_caption_path = "/Users/yadubhushan/Downloads/Salsa/Salsa-Regular.ttf"  # Replace with the path to your .ttf file
font_body = ImageFont.truetype(font_caption_path, caption_font_size)
watermark_font = ImageFont.truetype(font_caption_path, watermark_font_size)

# Create a new image with white background
width, height = 1080, 1080

name_color = "#ffffff"
watermark_color = "#A0C3D2"
caption_color = "#FF8080"
#caption_color = "#94A684

python_space = get_config_value('python_space')
json_file = os.path.join(python_space, "resources/files/philosophy_inputs/Gues_the_philosopher.json")


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def darken_image(image):
    # Create a copy of the original image
    darker_image = image.copy()

    # Define the darkness intensity (0 for no darkness, 255 for completely black)
    darkness_intensity = 200  # Adjust this value as needed

    # Calculate the overlay color (black with the specified intensity)
    overlay_color = (0, 0, 0, darkness_intensity)

    # Create an overlay layer with the same size as the image
    overlay = Image.new('RGBA', image.size, overlay_color)

    # Composite the overlay onto the darker_image
    darker_image.paste(overlay, (0, 0), overlay)
    return darker_image

def crop_to_square(image):
    width, height = image.size
    new_dimension = min(width, height)
    
    left = (width - new_dimension) / 2
    top = (height - new_dimension) / 2
    right = (width + new_dimension) / 2
    bottom = (height + new_dimension) / 2

    image = image.crop((left, top, right, bottom))
    return image


def draw_caption(draw, content):
    text_color = hex_to_rgb(caption_color)
    wrapped_text = textwrap.fill(content, width=40)  # Adjust the width parameter as needed
    # calculate the number of lines
    lines = wrapped_text.count('\n') + 1
    # calculate the height
    text_height = image_height * 0.80 - lines * caption_font_size * 1.2 
    # Draw the body
    body_position = (image_width * 0.10, text_height)
    draw.multiline_text(body_position, wrapped_text, font=font_body, fill=text_color, align="center", spacing = 15)

def draw_watermark(draw, watermark):
    watermark = "©" + watermark
    text_color = hex_to_rgb(watermark_color)
    width = watermark_font.getlength(watermark)

    body_position = (image_width * 0.50 - width/2, image_height * 0.95)
    draw.text(body_position, watermark, font=watermark_font, fill=text_color, align="center", spacing = 15)

def draw_name(draw, name, height_above):
    font_to_use = watermark_font
    text_color = hex_to_rgb(name_color)
    # convert to uppercase
    name = name.upper()
    name = "- " + name + " -" 
    width = font_to_use.getlength(name)

    body_position = (image_width * 0.50 - width * 0.50, height_above + 60)
    draw.text(body_position, name, font=font_to_use, fill=text_color, align="center", spacing = 15)

def draw_single_caption(original_image, caption, output_file,  name = None, watermark = None):
    image = original_image.copy()
    image = crop_to_square(image)
    image = image.resize((1080, 1080), Image.LANCZOS)
    image = darken_image(image)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    draw_caption(draw, caption)
    if watermark:
        draw_watermark(draw, watermark)
    if name:
        draw_name(draw, name, image_height * 0.80)
    image.save(output_file)
    return output_file


def runner():
    # Read the JSON data from the file
    with open(json_file, 'r') as file:
        quotes = json.load(file)

    # Update each quote with a "published" key set to False
    for quote in quotes:
        quote['published'] = False

    open_line  = "Guess the philosopher w"
 
    save_caption_output = "/Users/yadubhushan/Documents/media/python_space/output/save_caption_output"
    watermark = "tech.philosophy.school"
    output_file = os.path.join(save_caption_output, "caption_image.jpg")
    # Save the image
    original_image = Image.open('/Users/yadubhushan/Documents/media/python_space/resources/images/philosophers/camus.png')
    caption = "A serious and good philosophical work could be written consisting entirely of jokes. "
    caption = caption 
    name = "Albert Camus"
    output_file = draw_single_caption(original_image, caption, output_file, name, watermark)
    print(f"Saved caption image to: {output_file}")
    


if __name__ == "__main__":
    runner()
