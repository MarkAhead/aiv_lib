import base64
import requests
from .util_ConfigManager import get_config_value

API_KEY = get_config_value("STABILITY_API_KEY")

def generateImageByPrompt(output_file, prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    # Prepare the body of the request with the dynamic prompt
    body = {
      "steps": 40,
      "width": 1024,
      "height": 1024,
      "seed": 0,  # You might want to randomize this for varied outputs
      "cfg_scale": 5,
      "samples": 1,
      "text_prompts": [
        {
          "text": prompt,
          "weight": 1
        }
      ],
    }
    
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      # Ensure to replace 'YOUR_API_KEY' with your actual API key
      "Authorization": "Bearer " + API_KEY,
    }
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Non-200 response: {response.text}")
    
    data = response.json()
    
    # Save the generated image
    for image in data["artifacts"]:
        with open(output_file, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        print(f"Image saved to {output_file}")