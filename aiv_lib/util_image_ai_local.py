import os
import torch
import gc
from .util_ConfigManager import get_config_value


use_local_stable_diffusion_model = get_config_value("use_local_stable_diffusion_model").upper()

print(f"use_local_stable_diffusion_model: {use_local_stable_diffusion_model}")
if use_local_stable_diffusion_model == "TRUE":
    device = torch.device("cuda" if torch.cuda.is_available() else "mps")
    print(f"Using device {device}")
    print(f"Using torch version {torch.__version__}")
    if torch.cuda.is_available():
        print(f"torch.cuda.is_available() {torch.cuda.is_available()}")
        print(f"torch.cuda.current_device() {torch.cuda.current_device()}")
    
    from diffusers import DiffusionPipeline
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

    # Define steps and fraction
    n_steps = 40
    high_noise_frac = 0.8
else:
    base = None
    refiner = None
    print("Local Stable Diffusion model usage is disabled or not configured correctly.")

def generateImageByPrompt(output_file_path, prompt):
    if base is not None and refiner is not None:
        # Run both experts
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
        image.save(output_file_path)
        print(f"Image saved to {output_file_path}")
        gc.collect()
    else:
        print("Local Stable Diffusion models are not loaded. Cannot generate image.")

if __name__ == "__main__":
    output_folder = os.getenv("output_folder")
       
