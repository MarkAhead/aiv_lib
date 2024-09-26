import os
import torch
import gc
from aiv_lib.util_ConfigManager import get_config_value
from PIL import Image
import numpy
from diffusers import DiffusionPipeline


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

    # Define steps and fraction
    n_steps = 40
    high_noise_frac = 0.8
else:
    base = None
    refiner = None
    print("Local Stable Diffusion model usage is disabled or not configured correctly.")


def generateImageByPrompt(output_file, prompt):
    if base is not None and refiner is not None:
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
        print(f"Image saved to {output_file}")
        gc.collect()
    else:
        print("Local Stable Diffusion models are not loaded. Cannot generate image by prompt.")
        

def generateImageWithExistingCharacter(existing_image_path, output_file_path, prompt):
    if base is not None and refiner is not None:
        # Load the existing image and convert it to a tensor
        existing_image = Image.open(existing_image_path).convert('RGB')
        existing_image_tensor = torch.from_numpy(np.array(existing_image)).permute(2, 0, 1).unsqueeze(0).to(device)
        
        # Resize the image to the model's expected size
        from torchvision.transforms.functional import resize
        existing_image_tensor = resize(existing_image_tensor, (512, 512))  # Adjust size if necessary

        # Normalize the image tensor
        existing_image_tensor = existing_image_tensor / 255.0

        # Run the base model to encode the existing image
        with torch.no_grad():
            base_encoded = base.vae.encode(existing_image_tensor)[0].sample()

        # Run both experts with the existing image as context
        image = base(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
            init_image=base_encoded,
            strength=0.8  # You can adjust this to control how much the original image influences the result
        ).images
        image = refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        image.save(output_file_path)
        print(f"Image with existing character saved to {output_file_path}")
        gc.collect()
    else:
        print("Local Stable Diffusion models are not loaded. Cannot generate image with existing character.")



if __name__ == "__main__":
    output_folder = os.getenv("output_folder")
    existing_image_path = "/Users/yadubhushan/Downloads/2e30ef20-ef76-4ebd-b9f0-13b541140e34.jpeg"
    generateImageWithExistingCharacter(existing_image_path, f"{output_folder}/output.jpg", "A character with a sword")
       
