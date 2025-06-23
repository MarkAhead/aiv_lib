import os
import mimetypes
from google.cloud import storage
from .util_ConfigManager import get_config_value
from urllib.parse import urlparse


def parse_file_path(file_path):
    # Split the path into parts
    path_parts = file_path.strip('/').split('/')
    
    # Get the bucket name
    bucket_name = path_parts[0]
    
    # Get the folder path
    folder_path = '/'.join(path_parts[1:-1])
    
    # Get the file name
    file_name = path_parts[-1]
    
    return bucket_name, folder_path, file_name

def get_content_type(file_path):
    """
    Determine the content type based on file extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type for the file
    """
    # Get the file extension
    _, ext = os.path.splitext(file_path.lower())
    
    # Define content types for common asset types
    content_type_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.mov': 'video/quicktime',
        '.json': 'application/json',
        '.txt': 'text/plain',
        '.md': 'text/markdown'
    }
    
    # Return specific content type or use mimetypes as fallback
    content_type = content_type_map.get(ext)
    if content_type:
        return content_type
    
    # Use mimetypes library as fallback
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

def upload_blob(bucket_name, local_path, cloud_destination_path):
    """
    Uploads a file to the bucket with appropriate content type.
    
    Args:
        bucket_name (str): Firebase Storage bucket name
        local_path (str): Local file path to upload
        cloud_destination_path (str): Destination path in cloud storage
        
    Raises:
        Exception: If upload fails for any reason
    """
    try:
        # Validate inputs
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        if os.path.getsize(local_path) == 0:
            raise ValueError(f"Local file is empty: {local_path}")
        
        # Initialize storage client and bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(cloud_destination_path)
        
        # Determine and set content type
        content_type = get_content_type(local_path)
        blob.content_type = content_type
        
        # Upload the file
        blob.upload_from_filename(local_path)
        
        print(f"File {local_path} uploaded to {cloud_destination_path} with content type {content_type}")
        
    except FileNotFoundError as e:
        print(f"Upload failed - File not found: {e}")
        raise
    except ValueError as e:
        print(f"Upload failed - Invalid file: {e}")
        raise
    except Exception as e:
        print(f"Upload failed - Firebase Storage error: {e}")
        raise

def download_blob(bucket_name, cloud_path, local_file_path):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(cloud_path)

    blob.download_to_filename(local_file_path)

    print(f"Blob {cloud_path} downloaded to {local_file_path}.")

def download_blob_with_remote_path(source_blob_path, local_bucket_path):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    
    bucket_name, remote_folder_path, file_name = parse_file_path(source_blob_path)
    local_folder_path = os.path.join(local_bucket_path, remote_folder_path)
    os.makedirs(local_folder_path, exist_ok=True)
    destination_file_path = os.path.join(local_folder_path , file_name)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_folder_path + "/" + file_name)
    
    blob.download_to_filename(destination_file_path)

    print(f"Blob {source_blob_path} downloaded to {destination_file_path}.")
    return destination_file_path


def delete_blob(bucket_name, blob_path):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.delete()
    print(f"Blob {blob_path} deleted.")

def list_files_in_bucket(bucket_name):
    """Lists all the files in the bucket."""

    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)
    
    # List all files in the bucket
    blobs = bucket.list_blobs()
    
    # Create a list to store the file paths
    file_paths = []
    
    for blob in blobs:
        file_paths.append(blob.name)
    
    return file_paths

def list_files_in_bucket(bucket_name, prefix):
    """Lists all the files in the bucket at the specified path."""
    
    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)
    
    # List all files in the bucket at the specified path
    blobs = bucket.list_blobs(prefix=prefix)
    
    # Create a list to store the file paths
    file_paths = []
    
    for blob in blobs:
        file_paths.append(blob.name)
    
    return file_paths


def test_storage(bucket_name):
    resouces_folder = get_config_value("resources_folder")
    output_folder = get_config_value("output_folder")
    source_file_name = resouces_folder + "audio/Soft_background_small.mp3"
    destination_blob_name = "input/file.mp3"
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    output_file_path = output_folder + "temp/file.mp3"
    download_blob(bucket_name, destination_blob_name, output_file_path)
    delete_blob(bucket_name, destination_blob_name)


if __name__ == "__main__":
    bucket_name = "social_bot_subtitles"
    files = list_files_in_bucket(bucket_name, prefix="input/")
    print(files)


