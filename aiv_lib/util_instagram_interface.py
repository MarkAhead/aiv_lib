
import time
from instagrapi import Client
import os
from pydantic import parse_obj_as, HttpUrl
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag, Usertag, UserShort
from PIL import Image
from os import listdir
from os.path import isfile, join
from pathlib import Path
import sys
from pydantic import ValidationError
import random
from aiobotocore import credentials
from .util_ConfigManager import get_config_value

from .util_gcp_secret_manager import  get_secret_value


parent_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta"
posts_base_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta/bollywood"

mode = 0o777


def waitForRandomTime():
    wait_time = random.randint(40, 120)  # Renamed the variable to avoid shadowing
    print("Waiting for ", wait_time, " seconds")
    time.sleep(wait_time)  # Using the time module's sleep function as intended


def login(UserName, Password) -> Client:
    client = Client()
    client.login(UserName, Password)
    waitForRandomTime()
    return client

def get_credetials(key):
    USERNAME, PASSWORD = get_config_value(key).split(':')
    return USERNAME, PASSWORD

def loginWithConfig(key):
    USERNAME, PASSWORD = get_credetials(key)
    client = login(USERNAME, PASSWORD)
    return client

techPhilosophyInstaClient = None

credentials = {}


def getUserTags(users_to_mention_list):
    user_tags = []
    for user in users_to_mention_list:
        if isinstance(user, UserShort):
            user_tags.append(Usertag(user=user, x=0.23, y=0.32))
        else:
            print(f"Skipping invalid user data: {user}")
    return user_tags



def get_user_to_mention(client: Client, users_to_mention_string):
    if users_to_mention_string == '' or users_to_mention_string is None:
        return []
    users_to_mention_list = []
    users_to_mention = users_to_mention_string.split(",")
    # get random 10 users from the list
    if len(users_to_mention) > 10:
        random.shuffle(users_to_mention)
        users_to_mention = users_to_mention[:5]
    
    print(users_to_mention)
    for user in users_to_mention:
        user = user.strip()
        if user == '':
            continue
        try:
            user_info = client.user_info_by_username(user)
            users_to_mention_list.append(user_info)
        except:
            print("An exception occurred for ", user)
    return getUserTags(users_to_mention_list)



def get_request_hash_tag(client: Client, hash_tag_string):
    hash_tags = hash_tag_string.split(" ")
    request_hash_tag_list = []
    for hash_tag in hash_tags:
        if hash_tag == '':
            continue
        try:
            hashtag_info = client.hashtag_info(hash_tag)
            request_has_tag = StoryHashtag(hashtag=hashtag_info, x=0.23, y=0.32, width=0.5, height=0.22)
            request_hash_tag_list.append(request_has_tag)
        except:
            print("An exception occurred for ", hash_tag )
    return request_hash_tag_list




def upload_image_to_profile(client: Client, paths, caption, hash_tags_list = None):
    
    if hash_tags_list is not None:
        caption = caption + "\n\n\n\n" + " ".join(hash_tags_list)
    
    if len(paths) == 1 :
        client.photo_upload(path = paths[0], caption = caption)
    else:
        client.album_upload(paths = paths, caption = caption)
    
    print("Photo uploaded successfully")
    

#
# if users_to_mention_string is not None:
#         user_tags = get_user_to_mention(client, users_to_mention_string)
#     else:
#         user_tags = []
#

def upload_video_to_profile(client: Client, video_path, caption, hash_tags_list = None, thumbnail = None): 
    
    if hash_tags_list is not None:
        caption = caption + "\n\n\n\n" + " ".join(hash_tags_list)
    
    client.clip_upload(path = video_path, caption = caption, thumbnail = thumbnail)
    print("Video uploaded successfully")



if __name__ == "__main__":
    video_path = '/Users/yadubhushan/Documents/media/python_space/resources/social/insta/tech_philosophy/f65f0990-4373-44b2-88cb-6bb3b0037381/video.mp4'
    caption = 'Delve deep into the unique insights of the philosopher Arthur Schopenhauer. Discover how his views on life and existence might stimulate your thoughts 🤔💭 #SchopenhauerWisdom #KeenInsights \n \n \n \n #SchopenhauerWisdom, #KeenInsights, #Philosophy, #LifeInterpretations'
    #uploadToTechPhilosophyInsta(caption=caption, video_path = video_path)

    
