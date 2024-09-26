import os
from google.cloud import storage
from util_ConfigManager import get_config_value


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


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


