import os

# shuffle the art types
import random
from aiv_lib.util_ConfigManager import get_config_value
from aiv_lib.ArtifactQuality import ArtifactQuality

from aiv_lib.image_generator.image_generator_external import generateImageByPrompt as remote_generateImageByPrompt
from aiv_lib.image_generator.image_generator_local import generateImageByPrompt as local_generateImageByPrompt
from aiv_lib.image_generator.image_generator_mock import generateImageByPrompt as mock_generateImageByPrompt

# Properly convert the config value to boolean
config_value = get_config_value("use_local_stable_diffusion_model")
use_local_stable_diffusion_model = config_value and str(config_value).upper() == "TRUE"

art_type_index = 0

art_types = [
    " fantasy art",
    " abstract art",
    " surreal art",
    " impressionism",
    " expressionism",
    " pop art",
    " minimalism",
    " realism",
    " art nouveau",
    " cubism",
    "anime art",
    " conceptual art",
    " digital art",
    " street art",
    " fine art",
    " modern art",
    "cartoon art",
]

random.shuffle(art_types)


def generateImages(output_folder, prompt, num_images_to_generate=1, art_type=None, quality=ArtifactQuality.LQ):
    """
    Generate images using AI with specified quality level.
    
    Args:
        output_folder: Directory to save generated images
        prompt: Text prompt for image generation
        num_images_to_generate: Number of images to generate (default: 1)
        art_type: Specific art style to use (default: None, cycles through art_types)
        quality: Image quality level - ArtifactQuality.LQ, ArtifactQuality.HQ, or ArtifactQuality.MOCK (default: LQ)
    """
    global art_type_index  # Declare the variable as global
    generated_file_paths = []
    # Validate quality parameter
    if isinstance(quality, str):
        quality_upper = quality.upper()
        if quality_upper == "LQ":
            quality = ArtifactQuality.LQ
        elif quality_upper == "HQ":
            quality = ArtifactQuality.HQ
        elif quality_upper == "MOCK":
            quality = ArtifactQuality.MOCK
        else:
            quality = ArtifactQuality.LQ
    elif not isinstance(quality, ArtifactQuality):
        quality = ArtifactQuality.LQ
    
    print(f"Generating {num_images_to_generate} image(s) with {quality.value} quality")
    
    for i in range(num_images_to_generate):
        # For MOCK quality, use original prompt without art style modifications
        if quality == ArtifactQuality.MOCK:
            prompt_to_use = prompt
        else:
            if art_type is not None:
                art_type_to_use = art_type
            else:
                art_type_to_use = art_types[art_type_index]
                art_type_index = (art_type_index + 1) % len(art_types)
            
            # Adjust prompt based on quality
            if quality == ArtifactQuality.HQ:
                prompt_to_use = prompt + ", " + art_type_to_use + " style, ultra real, dramatic lighting, photorealistic, 4k, high resolution, detailed"
            else:  # LQ
                prompt_to_use = prompt + ", " + art_type_to_use + " style, simple, basic quality"
        
        file_path = os.path.join(output_folder, f"ai_{i}.jpeg")
        
        # Choose the appropriate generator based on quality
        if quality == ArtifactQuality.MOCK:
            print(f"Generating mock image with prompt: {prompt_to_use}")
            mock_generateImageByPrompt(file_path, prompt_to_use, quality)
        elif use_local_stable_diffusion_model:
            print(f"Generating image with prompt: {prompt_to_use} with local stable diffusion model ({quality.value})")
            local_generateImageByPrompt(file_path, prompt_to_use, quality)
        else:
            print(f"Generating image with prompt: {prompt_to_use} with remote stable diffusion model ({quality.value})")
            remote_generateImageByPrompt(file_path, prompt_to_use, quality)
        print(f"Image {i} saved to {output_folder}")
        generated_file_paths.append(file_path)
    return generated_file_paths


if __name__ == "__main__":
    output_folder = get_config_value("output_folder")  
    text_to_generate = "penguin in a snowstorm"
    ai_images_output_folder = os.path.join(output_folder, "ai_images")
    os.makedirs(ai_images_output_folder, exist_ok=True)
    
    # Test with different quality levels
    print("Testing LQ quality:")
    generateImages(
        ai_images_output_folder,
        text_to_generate,
        num_images_to_generate=1,
        quality=ArtifactQuality.LQ
    )
    
    print("\nTesting MOCK quality:")
    generateImages(
        ai_images_output_folder,
        text_to_generate,
        num_images_to_generate=1,
        quality=ArtifactQuality.MOCK
    )
    
    # print("\nTesting HQ quality:")
    # generateImages(
    #     ai_images_output_folder,
    #     text_to_generate,
    #     num_images_to_generate=1,
    #     quality=ArtifactQuality.HQ
    # )
    
    print(ai_images_output_folder)

