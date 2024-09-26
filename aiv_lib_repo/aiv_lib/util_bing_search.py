import os
import re
import requests
import shutil
from .util_ConfigManager import get_config_value


BING_SEARCH_API_KEY = get_config_value("BING_SEARCH_API_KEY")


def api_call(search_term, number_images_to_search=35):
    endpoint = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_API_KEY}
    search_params = {
        "q": search_term,
        "mkt": "en-US",
        "imageType": "Photo",
        "aspect": "Tall",
        "size": "Large",
        "count": number_images_to_search,
    }

    try:
        response = requests.get(endpoint, headers=headers, params=search_params)
        results = response.json()
        return results.get("value", [])
    except Exception as ex:
        raise ex


def download_image(image_url, filename):
    try:
        with open(filename, "wb") as img_file:
            img_file.write(requests.get(image_url, timeout=30).content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")
        return False


def fetch_best_images(search_term, output_folder, num_images_to_download=1):
    image_results = api_call(search_term, number_images_to_search=50)

    temp_folder = os.path.join(output_folder, "temp_images")
    os.makedirs(temp_folder, exist_ok=True)

    clean_search_term = re.sub(r"[^\w]", "", search_term)
    downloaded_count = 0

    for index, item in enumerate(image_results, start=1):
        if downloaded_count >= num_images_to_download:
            break

        image_url = item["contentUrl"]
        file_extension = item["encodingFormat"]
        image_name = os.path.join(
            temp_folder, f"{index}_{clean_search_term}.{file_extension}"
        )

        # Download the image
        if download_image(image_url, image_name):
            # Check if image size meets the criteria
            if os.path.getsize(image_name) >= 0.1 * 1024 * 1024:
                downloaded_count += 1
            else:
                os.remove(image_name)  # Remove the file that doesn't meet the criteria

    return temp_folder


def get_best_image(search_term, output_folder):
    folder_path = fetch_best_images(search_term, output_folder)
    best_image_path = max(
        (os.path.join(folder_path, f) for f in os.listdir(folder_path)),
        key=lambda x: os.path.getsize(x),
    )

    final_output = os.path.join(output_folder, os.path.basename(best_image_path))
    shutil.move(best_image_path, final_output)

    shutil.rmtree(folder_path)
    return final_output


if __name__ == "__main__":
    output = get_best_image(
        "puppies",
        "/Users/yadubhushan/Documents/media/python_space/resources/social/bing_images",
    )
    print(f"Best Image Downloaded to: {output}")
