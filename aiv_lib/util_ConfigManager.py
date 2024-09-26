import os
import shutil

from .util_gcp_secret_manager import get_secret_value
import configparser

def load_config():
    # Get the secret key from the environment variable
    which_config_key = os.environ.get('which_config')
    if not which_config_key:
        raise SystemExit('which_config environment variable not found.')
    
    # Fetch the secret value
    config_value = get_secret_value(which_config_key)
    
    # Parse the config value using configparser
    config = configparser.ConfigParser()
    config.read_string(config_value)

    # Get the platform key from the environment variable
    platform_key = os.environ.get('platform_key', 'DEFAULT')
    print(f"platform_key: {platform_key}")
    
    platform_config = config[platform_key] if platform_key in config else {}
    
    final_config = {**config['DEFAULT'], **platform_config}
    return final_config

def get_config_value(key):
    return config_manager.get(key)

def create_output_folder(name : str):
    output_folder = get_config_value('output_folder')
    output_folder = os.path.join(output_folder, name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    return output_folder
        
def empty_and_delete_directory(dir_path):
    # Check if the directory exists
    if os.path.exists(dir_path):
        # Remove all files and subdirectories in the directory
        shutil.rmtree(dir_path)
        print(f"The directory '{dir_path}' has been emptied and deleted.")
    else:
        print(f"The directory '{dir_path}' does not exist.")

def get_firestore_client():
    import firebase_admin
    from firebase_admin import firestore
    firebase_admin.initialize_app()
    
    # Get a Firestore client
    db = firestore.client()
    
    return db

config_manager = load_config()

if __name__ == "__main__":
    print(get_config_value("output_folder"))
