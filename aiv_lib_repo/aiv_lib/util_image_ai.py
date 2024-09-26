import os

# shuffle the art types
import random
from .util_ConfigManager import get_config_value

from .util_image_ai_remote import generateImageByPrompt as remote_generateImageByPrompt
from .util_image_ai_local import generateImageByPrompt as local_generateImageByPrompt

use_local_stable_diffusion_model = get_config_value("use_local_stable_diffusion_model")   

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


def generateImages(output_folder, prompt, num_images_to_generate=1, art_type = None):
    global art_type_index  # Declare the variable as global
    for i in range(num_images_to_generate):
        if art_type is not None:
            art_type_to_use = art_type
        else:
            art_type_to_use = art_types[art_type_index]
            art_type_index = (art_type_index + 1) % len(art_types)
        prompt =  prompt +  ", " + art_type_to_use + " style, ultra real, dramatic lighting, photorealistic, 4k "
        file_path = os.path.join(output_folder, f"ai_{i}.jpeg")
        if use_local_stable_diffusion_model:
            local_generateImageByPrompt(file_path, prompt)
        else:
            remote_generateImageByPrompt(file_path, prompt)
        print(f"Image {i} saved to {output_folder}")



if __name__ == "__main__":
    output_folder = get_config_value("output_folder")   
    ai_images_output_folder = os.path.join(output_folder, "ai_images")
    os.makedirs(ai_images_output_folder, exist_ok=True)
    output = generateImages(
       ai_images_output_folder,
        "little girl darkhair, kodak portra 100, split into multiple different images, shot from different angles",
        num_images_to_generate=1,
    )
    print(ai_images_output_folder)

