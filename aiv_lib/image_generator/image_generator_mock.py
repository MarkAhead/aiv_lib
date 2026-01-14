import os
import random
from PIL import Image, ImageDraw, ImageFont
from aiv_lib.ArtifactQuality import ArtifactQuality
from aiv_lib.util_ConfigManager import get_config_value
import textwrap

def break_text_into_lines(text, max_chars_per_line=None):
    """
    Break text into multiple lines intelligently.
    If max_chars_per_line is provided, use it. Otherwise, use smart breaking.
    """
    words = text.split()
    
    if max_chars_per_line:
        # Use textwrap for character-based breaking
        return textwrap.wrap(text, width=max_chars_per_line)
    
    # Smart breaking based on word count
    if len(words) <= 3:
        return [text]  # Keep short text on one line
    elif len(words) <= 6:
        # Split into 2 lines
        mid = len(words) // 2
        return [' '.join(words[:mid]), ' '.join(words[mid:])]
    elif len(words) <= 9:
        # Split into 3 lines
        third = len(words) // 3
        return [
            ' '.join(words[:third]),
            ' '.join(words[third:third*2]),
            ' '.join(words[third*2:])
        ]
    else:
        # For longer text, use textwrap with reasonable line length
        return textwrap.wrap(text, width=40)

def calculateMultiLineTextSize(draw, lines, font):
    """Calculate the total bounding box for multi-line text"""
    total_width = 0
    total_height = 0
    line_heights = []
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        total_width = max(total_width, line_width)
        total_height += line_height
        line_heights.append(line_height)
    
    return total_width, total_height, line_heights

def generateImageByPrompt(output_file, prompt, quality=None):
    """
    Generate a mocked image with:
      - a fully random background color
      - a centered "scanner" rectangle outlined in the inverse color
      - the prompt in bold, as large as possible, in the inverse color (multi-line)
    """
    if quality != ArtifactQuality.MOCK and quality != ArtifactQuality.LQ:
        raise ValueError(f"Unsupported quality level: {quality}")

    # 1) Pick a random background color and its inverse
    bg = tuple(random.randint(0, 255) for _ in range(3))
    inv = tuple(255 - c for c in bg)

    # 2) Create the base image
    size = (1024, 1024)
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)

    # 3) Define a centered "scanner" rectangle (10% margin)
    margin = int(min(size) * 0.10)
    rect = (margin, margin, size[0] - margin, size[1] - margin)

    # 4) Draw a thick outline in the inverse color
    border_thickness = int(min(size) * 0.015)  # ~1.5% of width
    for i in range(border_thickness):
        draw.rectangle(
            (rect[0] + i, rect[1] + i, rect[2] - i, rect[3] - i),
            outline=inv
        )

    # 5) Calculate available space inside the rectangle (accounting for border)
    inner_padding = 20  # Reasonable padding inside the border
    max_w = rect[2] - rect[0] - (border_thickness * 2) - (inner_padding * 2)
    max_h = rect[3] - rect[1] - (border_thickness * 2) - (inner_padding * 2)

    # 6) Get font path from resources directory
    try:
        resources_folder = get_config_value('resources_folder')
        if resources_folder:
            font_path = os.path.join(resources_folder, "font", "Roboto-Bold.ttf")
        else:
            # Fallback - try relative path from current file location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate up to find the project root containing resources
            project_root = current_dir
            for _ in range(10):  # Safety limit
                if os.path.exists(os.path.join(project_root, "resources", "font")):
                    break
                parent = os.path.dirname(project_root)
                if parent == project_root:  # Reached filesystem root
                    break
                project_root = parent
            font_path = os.path.join(project_root, "resources", "font", "Roboto-Bold.ttf")
        
        print(f"Trying font path: {font_path}")
        
        if os.path.exists(font_path):
            font_available = True
            print(f"Font found at: {font_path}")
        else:
            print(f"Font not found at: {font_path}")
            font_available = False
            font_path = None
    except Exception as e:
        print(f"Error getting font path: {e}")
        font_available = False
        font_path = None

    # 7) Try different line breaking strategies and find the best font size
    best_font = None
    best_size = 12
    best_lines = [prompt]  # fallback to single line
    
    # Try different line breaking strategies
    line_strategies = [
        break_text_into_lines(prompt),  # Smart word-based breaking
        break_text_into_lines(prompt, 30),  # Character-based breaking - shorter lines
        break_text_into_lines(prompt, 20),  # Even shorter lines
        [prompt]  # Single line as fallback
    ]
    
    for lines in line_strategies:
        print(f"Trying {len(lines)} lines: {lines}")
        
        # Start with a large font size and work down
        font_size = 200
        strategy_best_font = None
        strategy_best_size = 12
        
        while font_size >= 12:
            try:
                if font_available and font_path:
                    test_font = ImageFont.truetype(font_path, font_size)
                else:
                    test_font = ImageFont.load_default()
                    if not font_available:
                        strategy_best_font = test_font
                        strategy_best_size = font_size
                        break
                
                # Calculate multi-line text size
                total_width, total_height, line_heights = calculateMultiLineTextSize(draw, lines, test_font)
                
                if total_width <= max_w and total_height <= max_h:
                    # This size fits! 
                    strategy_best_font = test_font
                    strategy_best_size = font_size
                    print(f"Strategy with {len(lines)} lines fits at font size: {font_size}")
                    break
                
                font_size -= 5
                
            except Exception as e:
                print(f"Error with font size {font_size}: {e}")
                font_size -= 5
        
        # If this strategy gave us a better (larger) font size, use it
        if strategy_best_size > best_size:
            best_font = strategy_best_font
            best_size = strategy_best_size
            best_lines = lines

    # Fallback if nothing worked
    if best_font is None:
        try:
            if font_available and font_path:
                best_font = ImageFont.truetype(font_path, 24)
                best_size = 24
            else:
                best_font = ImageFont.load_default()
                best_size = 12
            best_lines = [prompt]
        except:
            best_font = ImageFont.load_default()
            best_size = 12
            best_lines = [prompt]

    # 8) Draw the multi-line text centered in the rectangle
    total_width, total_height, line_heights = calculateMultiLineTextSize(draw, best_lines, best_font)
    
    # Calculate starting position to center the entire text block
    inner_rect_x = rect[0] + border_thickness + inner_padding
    inner_rect_y = rect[1] + border_thickness + inner_padding
    inner_rect_w = max_w
    inner_rect_h = max_h
    
    # Center the text block
    start_x = inner_rect_x + (inner_rect_w - total_width) / 2
    start_y = inner_rect_y + (inner_rect_h - total_height) / 2
    
    # Draw each line
    current_y = start_y
    for i, line in enumerate(best_lines):
        # Get line dimensions for horizontal centering
        line_bbox = draw.textbbox((0, 0), line, font=best_font)
        line_width = line_bbox[2] - line_bbox[0]
        
        # Center this line horizontally
        line_x = inner_rect_x + (inner_rect_w - line_width) / 2
        
        draw.text((line_x, current_y), line, fill=inv, font=best_font)
        current_y += line_heights[i]

    # 9) Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    img.save(output_file)
    print(f"Mocked image saved to {output_file} (font size: {best_size}, {len(best_lines)} lines)")


if __name__ == "__main__":
    from aiv_lib.util_ConfigManager import get_temp_folder
    temp_folder = get_temp_folder()
    output_file = os.path.join(temp_folder, "test.jpg")
    generateImageByPrompt(output_file, "A beautiful sunset over a calm ocean", ArtifactQuality.MOCK)
    print(f"Mocked image saved to {output_file}")