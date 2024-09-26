import uuid
import requests
import os



PEXELS_API_KEY = get_config_value("PEXELS_API_KEY")


posts_base_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta/bollywood"

unique_folder_name = str(uuid.uuid4())
output_folder = os.path.join(posts_base_dir, unique_folder_name)
os.makedirs(output_folder, exist_ok=True)

# Base URL for Pexels API
BASE_URL = 'https://api.pexels.com/videos/search'

headers = {
    'Authorization': PEXELS_API_KEY
}

def search_videos(query, orientation):
    """
    Search for videos on Pexels based on the given query and orientation.
    
    Args:
    - query (str): The search term.
    - orientation (str): The orientation of the video (landscape, portrait, etc.)
    
    Returns:
    - list: A list of video URLs.
    """
    params = {
        'query': query,
        'orientation': orientation,
        'size': 'medium',
        'per_page': 5
    }
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    response_data = response.json()
    
    video_urls = [video['video_files'][0]['link'] for video in response_data['videos']]
    
    return video_urls

def download_videos(video_urls):
    """
    Download videos from the provided URLs.
    
    Args:
    - video_urls (list): A list of video URLs.
    """
    for idx, url in enumerate(video_urls, 1):
        response = requests.get(url)
        output_file_path = os.path.join(output_folder, f'video_{idx}.mp4')
        with open(output_file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded video_{idx}.mp4")

if __name__ == "__main__":
    query = "philosophy"  # Replace with your desired query
    orientation = "portrait"  # Replace with your desired orientation
    
    video_urls = search_videos(query, orientation)
    download_videos(video_urls)
