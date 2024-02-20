

import os
from . import cloud_gcp_storage as cloud_gcp_storage

bucket_name = "media_artifacts"
cloud_base_path = "posts"


def upload_artifacts_to_cloud(source_file, destination_path_suffix, key): 
    # get file name with extension
    filename = os.path.basename(source_file)
    if destination_path_suffix:
        destination_path_suffix = destination_path_suffix + "/"
    else:
        destination_path_suffix = ""
    
    destination_path = cloud_base_path  + "/" + key + "/" + destination_path_suffix + filename
    cloud_gcp_storage.upload_blob(bucket_name, source_file, destination_path)
    return bucket_name  + "/" +  destination_path


def return_remote_folder_path(destination_path_suffix, key) : 
    if destination_path_suffix:
        destination_path_suffix = destination_path_suffix + "/"
    else:
        destination_path_suffix = ""
    return bucket_name  + "/" + cloud_base_path  + "/" + key + "/" + destination_path_suffix