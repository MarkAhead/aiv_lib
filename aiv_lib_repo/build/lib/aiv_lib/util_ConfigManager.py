import configparser
import os
import shutil
import platform


def load_config():
    # check if the os has a environment variable named config_file_key
    if 'workspace_config_file_path' not in os.environ:
        print('workspace_config_file_path not found in environment variables.')
        print('If using Visual studio code, set the env in the .evn file')
        SystemExit('workspace_config_file_path not found in environment variables.')
    # get the path of the config file
    config_file_path = os.environ.get('workspace_config_file_path')
    print(f'workspace config file path: {config_file_path}')
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_file_path)
    common_config = config['DEFAULT']
    platform_key = os.environ.get('platform_key', 'DEFAULT')
    print(f'platform_key: {platform_key}')
    platform_config = config[platform_key] if platform_key in config else {}
    final_config = {**common_config, **platform_config}
    return final_config


config_manager = load_config()


def get_config_value(key):
    return config_manager.get(key)

def get_google_cred_path():
    print(get_config_value('credentials_folder'))
    return get_config_value('credentials_folder') + get_config_value('gcp_cred_folder')

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

        
def set_google_cred_path():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_google_cred_path()
    print("Google credentials path set")

set_google_cred_path()

if __name__ == "__main__":
    print(get_google_cred_path())
