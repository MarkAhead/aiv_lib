import os
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

def upload_blob(bucket_name, source_path, destination_path):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_path)

    blob.upload_from_filename(source_path)

    print(f"File {source_path} uploaded to {destination_path}.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

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


