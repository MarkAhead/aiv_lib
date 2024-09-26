import os
import uuid
import requests
import re
import shutil


CX = get_config_value("GOOGLE_SEARCH_CX")
GOOGLE_SEARCH_API_KEY = get_config_value("GOOGLE_SEARCH_API_KEY")

def fetch_images(search_term, output_folder,  number_images_to_search = 10, num_images_to_download = 5):
    # Endpoint for Google Custom Search JSON API
    endpoint = "https://www.googleapis.com/customsearch/v1"

    # Parameters for the search
    params = {
        'q': search_term,
        'num': number_images_to_search,
        'start': 1,
        'imgSize': 'HUGE',
        'imgType' : 'photo',
        'fileType': 'png, jpeg, jpg',
        'searchType': 'image',
        'key': GOOGLE_SEARCH_API_KEY,  # Replace with your API key
        'cx': CX  # Replace with your Custom Search Engine ID
    }

    # Make the API request
    response = requests.get(endpoint, params=params)
    results = response.json()

    
    # Create a temporary directory to store images
    temp_folder = os.path.join(output_folder, 'temp_images')
    os.makedirs(temp_folder, exist_ok=True)



        # Download images
    downloaded_count = 0
    for index, item in enumerate(results.get('items', []), start=1):
        if downloaded_count >= num_images_to_download:
            break

        image_url = item['link']
        file_extension = os.path.splitext(image_url)[1]
        image_name = os.path.join(temp_folder, f"{index}_{clean_search_term}{file_extension}")
        
        try:
            with open(image_name, 'wb') as img_file:
                img_file.write(requests.get(image_url).content)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e}")
            continue      
        # Check the size of the downloaded image
        if os.path.getsize(image_name) < 100 * 1024:  # 100 KB
            os.remove(image_name)
        else:
            downloaded_count += 1

    return temp_folder


def get_best_size_image(search_term, output_folder, number_images_to_search=10, num_images_to_download=5):
    # Fetch images using the existing function
    folder_path = fetch_images(search_term, output_folder, number_images_to_search, num_images_to_download)
    
    # Initialize variables to track the best image
    best_image_path = None
    best_image_size = 0

    # Iterate through the downloaded images
    for image_file in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_file)
        image_size = os.path.getsize(image_path)

        # Update the best image if the current image is larger
        if image_size > best_image_size:
            best_image_size = image_size
            best_image_path = image_path

    # copy best_image_path to output_folder
    final_output = os.path.join(output_folder, os.path.basename(best_image_path))
    os.rename(best_image_path, final_output)
    # Delete the temporary folder
    shutil.rmtree(folder_path)
    return final_output







if __name__ == "__main__":
    posts_base_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta/bollywood"
    unique_folder_name = str(uuid.uuid4())
    output_folder = os.path.join(posts_base_dir, unique_folder_name)
    os.makedirs(output_folder, exist_ok=True)
    # Example usage:
    folder_path = fetch_images("Salman Khan, solo", output_folder)
    print(f"Images downloaded to: {folder_path}")
