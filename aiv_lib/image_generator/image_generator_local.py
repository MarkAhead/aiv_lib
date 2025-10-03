import os
import torch
import gc
from aiv_lib.util_ConfigManager import get_config_value
from aiv_lib.ArtifactQuality import ArtifactQuality
from PIL import Image
import numpy
from diffusers import DiffusionPipeline
from torchvision.transforms.functional import resize

use_local_stable_diffusion_model = get_config_value("use_local_stable_diffusion_model").upper()

print(f"use_local_stable_diffusion_model: {use_local_stable_diffusion_model}")
if use_local_stable_diffusion_model == "TRUE":
    device = torch.device("cuda" if torch.cuda.is_available() else "mps")
    print(f"Using device {device}")
    print(f"Using torch version {torch.__version__}")
    if torch.cuda.is_available():
        print(f"torch.cuda.is_available() {torch.cuda.is_available()}")
        print(f"torch.cuda.current_device() {torch.cuda.current_device()}")
    
    # Load both base & refiner
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    )
    base.to(device)
    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    refiner.to(device)

    # Quality-based parameters will be set per generation call
else:
    base = None
    refiner = None
    print("Local Stable Diffusion model usage is disabled or not configured correctly.")


def get_quality_params(quality):
    """
    Get generation parameters based on quality level.
    
    Args:
        quality: Quality level (ImageQuality.LQ or ImageQuality.HQ)
        
    Returns:
        tuple: (n_steps, high_noise_frac) for generation
    """
    
    # Handle quality parameter
    if quality is None or (isinstance(quality, str) and quality.upper() == "LQ"):
        quality_level = ArtifactQuality.LQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.LQ
    
    if quality_level == ArtifactQuality.HQ:
        # High quality: more inference steps, better refinement
        return 50, 0.8  # n_steps, high_noise_frac
    else:  # LQ
        # Low quality: fewer inference steps for faster generation
        return 20, 0.7  # n_steps, high_noise_frac


def generateImageByPrompt(output_file, prompt, quality=None):
    """
    Generate image using local Stable Diffusion with quality settings.
    
    Args:
        output_file: Path where the generated image will be saved
        prompt: Text prompt for image generation
        quality: Quality level (ImageQuality.LQ or ImageQuality.HQ or string "LQ"/"HQ")
    """
    
    # Handle quality parameter
    if quality is None or (isinstance(quality, str) and quality.upper() == "LQ"):
        quality_level = ArtifactQuality.LQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.LQ
    
    if base is not None and refiner is not None:
        # Get quality-specific parameters
        n_steps, high_noise_frac = get_quality_params(quality_level)
        
        print(f"Generating image with {quality_level.value} quality (steps: {n_steps}, noise_frac: {high_noise_frac})")
        
        image = base(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
        ).images
        image = refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        image.save(output_file)
        print(f"Image saved to {output_file} ({quality_level.value} quality)")
        gc.collect()
    else:
        print("Local Stable Diffusion models are not loaded. Cannot generate image by prompt.")
        

def generateImageWithExistingCharacter(existing_image_path, output_file_path, prompt, quality=None):
    """
    Generate image with existing character using local Stable Diffusion with quality settings.
    
    Args:
        existing_image_path: Path to the existing image to use as reference
        output_file_path: Path where the generated image will be saved
        prompt: Text prompt for image generation
        quality: Quality level (ImageQuality.LQ or ImageQuality.HQ or string "LQ"/"HQ")
    """
    
    # Handle quality parameter
    if quality is None or (isinstance(quality, str) and quality.upper() == "LQ"):
        quality_level = ArtifactQuality.LQ
    elif isinstance(quality, str) and quality.upper() == "HQ":
        quality_level = ArtifactQuality.HQ
    else:
        quality_level = quality if hasattr(quality, 'value') else ArtifactQuality.LQ
    
    if base is not None and refiner is not None:
        # Get quality-specific parameters
        n_steps, high_noise_frac = get_quality_params(quality_level)
        
        print(f"Generating character image with {quality_level.value} quality (steps: {n_steps}, noise_frac: {high_noise_frac})")
        
        # Load the existing image and convert it to a tensor
        existing_image = Image.open(existing_image_path).convert('RGB')
        existing_image_tensor = torch.from_numpy(numpy.array(existing_image)).permute(2, 0, 1).unsqueeze(0).to(device)
        
        # Resize the image to the model's expected size
        existing_image_tensor = resize(existing_image_tensor, (512, 512))  # Adjust size if necessary

        # Normalize the image tensor
        existing_image_tensor = existing_image_tensor / 255.0

        # Run the base model to encode the existing image
        with torch.no_grad():
            base_encoded = base.vae.encode(existing_image_tensor)[0].sample()

        # Adjust strength based on quality
        strength = 0.8 if quality_level == ArtifactQuality.HQ else 0.6  # Less aggressive for LQ

        # Run both experts with the existing image as context
        image = base(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
            init_image=base_encoded,
            strength=strength
        ).images
        image = refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        image.save(output_file_path)
        print(f"Image with existing character saved to {output_file_path} ({quality_level.value} quality)")
        gc.collect()
    else:
        print("Local Stable Diffusion models are not loaded. Cannot generate image with existing character.")



if __name__ == "__main__":
    output_folder = os.getenv("output_folder")
    existing_image_path = "/Users/admin_user/Downloads/2e30ef20-ef76-4ebd-b9f0-13b541140e34.jpeg"
    
    # Test with different quality levels
    print("Testing LQ quality:")
    generateImageWithExistingCharacter(
        existing_image_path, 
        f"{output_folder}/output_lq.jpg", 
        "A character with a sword", 
        ArtifactQuality.LQ
    )
    
    print("\nTesting HQ quality:")
    generateImageWithExistingCharacter(
        existing_image_path, 
        f"{output_folder}/output_hq.jpg", 
        "A character with a sword", 
        ArtifactQuality.HQ
    )
       
