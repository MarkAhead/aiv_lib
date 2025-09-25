import base64
import requests
from aiv_lib.util_ConfigManager import get_config_value
from aiv_lib.ArtifactQuality import ArtifactQuality

API_KEY = get_config_value("STABILITY_API_KEY")

def generateImageByPrompt(output_file, prompt, quality=None):
    """
    Generate image using Stability AI API with quality settings.
    
    Args:
        output_file: Path where the generated image will be saved
        prompt: Text prompt for image generation
        quality: Quality level (ArtifactQuality.LQ or ArtifactQuality.HQ or string "LQ"/"HQ")
    """
    
    # Handle quality parameter
    if quality is None or (isinstance(quality, str) and quality.upper() == "LQ"):
        quality_level = ArtifactQuality.LQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.LQ
    
    # Select appropriate model endpoint based on quality
    if quality_level == ArtifactQuality.HQ:
        # High Quality: Use Ultra model
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        model_name = "Ultra"
    else:  # LQ
        # Low Quality: Use Stable Diffusion 3.5 model
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        model_name = "Stable Diffusion 3.5"
    
    print(f"Generating image with prompt: {prompt} using {model_name} model ({quality_level.value} quality)")
    
    # Prepare the multipart form data as required by v2beta API
    # Adjust parameters based on quality level
    if quality_level == ArtifactQuality.HQ:
        # Ultra model parameters
        data = {
            "prompt": prompt,
            "output_format": "jpeg",  # Can be "jpeg", "png", or "webp"
            "aspect_ratio": "1:1",    # Square aspect ratio (1024x1024)
            "seed": 0,                # Random seed for variety
        }
    else:  # LQ quality
        # SD 3.5 model parameters
        data = {
            "prompt": prompt,
            "model": "sd3.5-large",   # Specify the SD 3.5 model variant
            "output_format": "jpeg",  # Can be "jpeg", "png", or "webp"
            "aspect_ratio": "1:1",    # Square aspect ratio
            "seed": 42,               # Fixed seed for consistent testing results
        }
    
    files = {
        "none": "",  # Required placeholder for multipart form
    }
    
    headers = {
        "Accept": "image/*",  # Updated to accept image response
        "Authorization": f"Bearer {API_KEY}",
    }
    
    response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code != 200:
        raise Exception(f"Non-200 response: Status {response.status_code}, {response.text}")
    
    # The v2beta API returns the image directly as binary data
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"Image saved to {output_file} using {model_name} ({quality_level.value} quality)")
    


if __name__ == "__main__":
    from util_ConfigManager import get_temp_folder
    import os
    
    temp_folder = get_temp_folder()
    
    # Test with different quality levels
    print("Testing LQ quality (SD 3.5 model):")
    generateImageByPrompt(
        os.path.join(temp_folder, "test_lq.jpg"), 
        "A beautiful sunset over a calm ocean", 
        ArtifactQuality.LQ
    )
    
    # print("\nTesting HQ quality (Ultra model):")
    # generateImageByPrompt(
    #     os.path.join(temp_folder, "test_hq.jpg"), 
    #     "A beautiful sunset over a calm ocean", 
    #     ImageQuality.HQ
    # )