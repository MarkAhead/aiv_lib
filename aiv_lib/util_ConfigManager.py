import configparser
import os

config_manager = configparser.ConfigParser()
# fetch from environment variable
# Try to fetch from environment variable, if not set use a default value
file_path = os.environ.get('CONFIG_FILE_PATH',
                           '/Users/yadubhushan/Documents/media/python_space/resources/credentials/credentials_social_media/dev_config.cfg')

config_manager.read(file_path)

def config():    
    return config_manager


def get_config_value(key):
    return config_manager['DEFAULT'].get(key)

def get_google_cred_path():
    return get_config_value('credentials_folder') + get_config_value('SOCIAL_MEDIA_BOT_CRED')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_google_cred_path()

if __name__ == "__main__":
    print(get_google_cred_path())
