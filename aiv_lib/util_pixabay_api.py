import os
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, quote_plus, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import logging
import time

from .util_ConfigManager import get_config_value

# IMPORTANT: Pixabay API Limitations
# The Pixabay API only supports two endpoints:
# 1. /api/ - for images (photos, illustrations, vectors)
# 2. /api/videos/ - for videos
# 
# There is NO /api/music/ or audio endpoint available.
# Audio-related functions in this module will return empty results and log warnings.

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PIXABAY_API_KEY = get_config_value("PIXABAY_API_KEY")
PIXABAY_BASE_URL = "https://pixabay.com/api/"

class PixabayAPI:
    """Optimized Pixabay API client with rate limiting and error handling.
    
    Note: Pixabay API only supports images and videos. Audio/music endpoints are not available.
    """
    
    BASE_URL = "https://pixabay.com/api/"
    
    def __init__(self, api_key: str = PIXABAY_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _rate_limit(self):
        """Implement rate limiting to avoid API abuse."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with error handling and rate limiting."""
        self._rate_limit()
        
        params['key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"hits": [], "total": 0}
    
    def _download_file(self, url: str, filepath: str) -> bool:
        """Download file with optimized settings."""
        try:
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Downloaded: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def search_images(self, query: str, image_type: str = "all", 
                     orientation: str = "all", per_page: int = 20) -> List[Dict]:
        """Search for images with optimized parameters."""
        params = {
            'q': query,
            'image_type': image_type,  # "all", "photo", "illustration", "vector"
            'orientation': orientation,  # "all", "horizontal", "vertical"
            'category': 'all',
            'min_width': 640,
            'min_height': 480,
            'safesearch': 'true',
            'order': 'popular',
            'per_page': min(per_page, 200),  # Max 200 per request
            'pretty': 'false'
        }
        
        result = self._make_request('', params)
        return result.get('hits', [])
    
    def search_videos(self, query: str, video_type: str = "all", 
                     orientation: str = "all", per_page: int = 20) -> List[Dict]:
        """Search for videos with optimized parameters."""
        params = {
            'q': query,
            'video_type': video_type,  # "all", "film", "animation"
            'orientation': orientation,  # "all", "horizontal", "vertical"
            'category': 'all',
            'min_width': 1280,
            'min_height': 720,
            'safesearch': 'true',
            'order': 'popular',
            'per_page': min(per_page, 200),
            'pretty': 'false'
        }
        
        result = self._make_request('videos/', params)
        return result.get('hits', [])
    
    def search_audio(self, query: str, audio_type: str = "all", per_page: int = 20, max_duration: int = 10) -> List[Dict]:
        """Search for music and sound effects.
        
        NOTE: The Pixabay API does not currently support audio/music search.
        This method returns an empty list and logs a warning.
        """
        logger.warning("Pixabay API does not support audio/music search. The /api/music/ endpoint does not exist.")
        logger.warning(f"Audio search requested for query: '{query}' but will return empty results.")
        return []


def download_images(download_dir: str, query: str, orientation: str = "all", 
                   max_downloads: int = 5) -> List[str]:
    """Download images with optimized concurrent downloads."""
    if not PIXABAY_API_KEY:
        logger.error("PIXABAY_API_KEY not configured")
        return []
    
    api = PixabayAPI()
    images = api.search_images(query, orientation=orientation, per_page=max_downloads)
    
    if not images:
        logger.warning(f"No images found for query: {query}")
        return []
    
    download_dir = Path(download_dir)
    downloaded_files = []
    
    def download_image(img_data):
        """Download single image."""
        img_id = img_data['id']
        # Prefer higher quality images
        img_url = img_data.get('largeImageURL') or img_data.get('webformatURL')
        
        if not img_url:
            return None
        
        # Get file extension from URL
        parsed_url = urlparse(img_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
        
        # Create safe filename
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_query}_{img_id}{file_ext}"
        filepath = download_dir / filename
        
        if api._download_file(img_url, str(filepath)):
            return str(filepath)
        return None
    
    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_img = {executor.submit(download_image, img): img for img in images}
        
        for future in as_completed(future_to_img):
            filepath = future.result()
            if filepath:
                downloaded_files.append(filepath)
    
    logger.info(f"Downloaded {len(downloaded_files)} images for query: {query}")
    return downloaded_files


def download_videos(download_dir: str, query: str, orientation: str = "all", 
                   max_downloads: int = 5) -> List[str]:
    """Download videos with optimized settings."""
    if not PIXABAY_API_KEY:
        logger.error("PIXABAY_API_KEY not configured")
        return []
    
    api = PixabayAPI()
    videos = api.search_videos(query, orientation=orientation, per_page=max_downloads)
    
    if not videos:
        logger.warning(f"No videos found for query: {query}")
        return []
    
    download_dir = Path(download_dir)
    downloaded_files = []
    
    def download_video(video_data):
        """Download single video."""
        video_id = video_data['id']
        # Get highest quality video URL
        video_urls = video_data.get('videos', {})
        
        # Priority order for video quality
        for quality in ['large', 'medium', 'small', 'tiny']:
            if quality in video_urls:
                video_url = video_urls[quality]['url']
                break
        else:
            return None
        
        # Create safe filename
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_query}_{video_id}.mp4"
        filepath = download_dir / filename
        
        if api._download_file(video_url, str(filepath)):
            return str(filepath)
        return None
    
    # Sequential download for videos (they're larger files)
    for video in videos:
        filepath = download_video(video)
        if filepath:
            downloaded_files.append(filepath)
    
    logger.info(f"Downloaded {len(downloaded_files)} videos for query: {query}")
    return downloaded_files


def download_music(download_dir: str, query: str, max_downloads: int = 5) -> List[str]:
    """Download music tracks with optimized settings.
    
    NOTE: The Pixabay API does not support music downloads.
    This function will return an empty list and log a warning.
    """
    logger.warning("Pixabay API does not support music downloads. No music endpoint is available.")
    logger.warning(f"Music download requested for query: '{query}' but Pixabay API only supports images and videos.")
    return []


def download_sound_effects(download_dir: str, query: str, max_downloads: int = 5) -> List[str]:
    """Download sound effects with optimized settings.
    
    NOTE: The Pixabay API does not support audio/sound effects downloads.
    This function will return an empty list and log a warning.
    """
    logger.warning("Pixabay API does not support sound effects downloads. No audio endpoint is available.")
    logger.warning(f"Sound effects download requested for query: '{query}' but Pixabay API only supports images and videos.")
    return []





