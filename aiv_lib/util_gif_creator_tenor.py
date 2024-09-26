
import os

from .util_ConfigManager import get_config_value

import requests
import json
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


TENOR_API_KEY = get_config_value("TENOR_API_KEY")
output_folder = get_config_value("output_folder")
local_output_folder = os.path.join(output_folder, "gif_images")
os.makedirs(local_output_folder, exist_ok=True)


def get_gif_for_search(search_term):
    apikey = TENOR_API_KEY  # click to set to your apikey
    lmt = 8
    ckey = "socialmediabot"  # set the client_key for the integration and use the same value for all API calls


    # get the top 8 GIFs for the search term
    r = requests.get(
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_8gifs = json.loads(r.content)
    else:
        top_8gifs = None

    return top_8gifs


def scrape_and_download(page_url, output_file_path):
    # Send an HTTP GET request to the web page
    response = requests.get(page_url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all image tags in the HTML (including GIFs)
        img_tags = soup.find_all('img')

        # Initialize variables to store the maximum width, height, and URL of the largest GIF
        max_width = 0
        max_height = 0
        max_gif_url = ''

        # Loop through all the image tags
        for img_tag in img_tags:
            # Get the URL of the image (GIF)
            img_url = img_tag.get('src')

            # Check if the URL ends with '.gif' to identify GIFs
            if img_url and img_url.lower().endswith('.gif'):
                # Fetch the image content
                img_response = requests.get(img_url)

                # Open the image using Pillow to get its dimensions
                img = Image.open(BytesIO(img_response.content))
                img_width, img_height = img.size

                # Check if this GIF has larger dimensions
                if img_width > max_width and img_height > max_height:
                    max_width = img_width
                    max_height = img_height
                    max_gif_url = img_url

        # Download the GIF with the maximum width and height
        if max_gif_url:
            gif_response = requests.get(max_gif_url)
            with open(output_file_path, 'wb') as f:
                f.write(gif_response.content)
            print(f'Downloaded the GIF with maximum dimensions ({max_width}x{max_height}) at {output_file_path}')

        else:
            print('No GIFs found on the page.')

    else:
        print('Failed to fetch the web page. HTTP status code:', response.status_code)

def download_all_gif(output_folder, search_term):
    result = get_gif_for_search(search_term)
    # loop through the top 8 GIFs returned, download each to the temp dir
    for gif in result['results']:
        gifurl = gif['url']
        # download gif to temp dir, named by gif id
        gifpath = os.path.join(output_folder, gif['id'] + '.gif')
        # create a gif file at path gifpath
        scrape_and_download(gifurl, gifpath)
    print("done")




if __name__ == "__main__":
    download_all_gif(local_output_folder, "sachin tendulkar")




