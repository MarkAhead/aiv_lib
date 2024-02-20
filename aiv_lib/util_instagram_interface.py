
import time
from instagrapi import Client
import os
from pydantic import parse_obj_as, HttpUrl
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag, Usertag
from PIL import Image
from os import listdir
from os.path import isfile, join
from pathlib import Path
import sys
from pydantic import ValidationError
import random
from aiobotocore import credentials
from .util_ConfigManager import get_config_value

category_hash_map = {
    "Travel": ["#Wanderlust", "#TravelDiaries", "#AdventureSeeker", "#TravelMore"],
    "Food": ["#Foodie", "#Delicious", "#Yummy", "#TastyTreats"],
    "Fitness": ["#FitLife", "#GymRat", "#FitnessAddict", "#HealthyLife"],
    "Fashion": ["#Fashionista", "#OOTD", "#StyleInspo", "#TrendSetter"],
    "Photography": ["#PicOfTheDay", "#PhotoGraphyLovers", "#Capture", "#CameraReady"],
    "SOCIAL_MEDIA_philosophy": ["#TechGeek", "#Gadgets", "#Innovation", "#LatestTech", "#Philosophy", "#Life", "#Meaning", "#Exitenstialism", "#LifeInterpretations", "#LifeLessons", "#LifeQuotes", "#LifeWisdom", "#LifeTeachings", "#Satre", "Nietzche"],
    "Nature": ["#MotherNature", "#NatureLovers", "#BeautifulScenery", "#NaturePhotography"],
    "Music": ["#MusicLife", "#Beats", "#JamSession", "#NewRelease"],
    "Art": ["#ArtisticSoul", "#Creative", "#Artwork", "#Masterpiece"],
    "Books": ["#Bookworm", "#AmReading", "#Literature", "#BookLovers"],
    "bollywood" : ["#bollywood", "#actor", "#actress", "#Hindi", "#HindiNews",  "#LatestNews",  "#LatestUpdates", "#ABPNews", "#India"],
    "hollywood" : ["#hollywood", "#actor", "#actress", "#English", "#EnglishNews",  "#LatestNews",  "#LatestUpdates", "#ABPNews", "#India", "#USA", "#UK", "#Cinema", "#Movie", "#Film", "#Entertainment", "CinematoGraphy", ],
}

os.environ['STABILITY_KEY'] = 'sk-ZqcAMw7xluufMM29499fEddeSQ3EiniRjGKgpJdDiqpQ9bSY'
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
        user_tags.append(Usertag(user = user, x=0.23, y=0.32))

    return user_tags


def get_user_to_mention(client: Client, users_to_mention_string):
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



# Extend to go to AI and return the 
def getBestHashTagsForCategory(category):
    return category_hash_map[category]


def upload_image_to_profile(client: Client, paths, caption, users_to_mention_string, category):
    user_tags = get_user_to_mention(client, users_to_mention_string)
    print("user list obtained...")   
    caption_with_tags = caption + "\n\n\n\n" + " ".join(getBestHashTagsForCategory(category))
    if len(paths) == 1 :
        client.photo_upload(path = paths[0], caption = caption_with_tags, usertags = user_tags)
    else:
        client.album_upload(paths = paths, caption = caption_with_tags, usertags =  user_tags)
    print("Photo uploaded successfully")
    


def uploadVideoToInsta(client: Client, video_path, caption, users_to_mention_string, category, thumbnail = None): 
    user_tags = get_user_to_mention(client, users_to_mention_string)
    caption_with_tags = caption + "\n\n\n\n" + " ".join(getBestHashTagsForCategory(category))
    client.clip_upload(path = video_path, caption = caption_with_tags, usertags = user_tags, thumbnail = thumbnail)
    print("Video uploaded successfully")



def uploadToBollywoodInsta() :
    users_to_mention_string = "nris_adda, caveofapelles,theneonshoww, tezroke, samharrisorg" 
    USERNAME, PASSWORD = get_config_value('SOCIAL_MEDIA_BOLLYWOOD_GOSSIP').split(':')
    client= login(USERNAME, PASSWORD)



def uploadToCinemaInsta():
    users_to_mention_string = "nris_adda, caveofapelles,theneonshoww, tezroke, samharrisorg" 
    USERNAME, PASSWORD = get_config_value('SOCIAL_MEDIA_CINEMA_INSTA').split(':')


def uploadToInsta(caption, video_path=None, images_path=None, thumbnail=None , user_cred_key="SOCIAL_MEDIA_philosophy"):
    
    if credentials.get(user_cred_key) is None:
        USERNAME, PASSWORD = get_config_value(user_cred_key).split(':')
        client = login(USERNAME, PASSWORD)
        credentials[user_cred_key] = client

    client = credentials[user_cred_key]
    if video_path is None and images_path is None:
        raise Exception("Either video_path or images_path should be provided")

    users_to_mention_string = ""
    
    published_TO = {}
    published_TO['INSTAGRAM'] = get_credetials('SOCIAL_MEDIA_philosophy')[0]
    category = "SOCIAL_MEDIA_philosophy"

    try:
        if video_path is not None:
            uploadVideoToInsta(techPhilosophyInstaClient, video_path, caption, users_to_mention_string, thumbnail)

        if images_path is not None:
            upload_image_to_profile(techPhilosophyInstaClient, images_path, caption, users_to_mention_string, category)

    except ValidationError as e:
        print(f"Validation Error: {e}")  # You might want to log this error instead of printing
        # Handle the error appropriately here (e.g., maybe you want to modify published_TO to indicate an error state)
    
    return published_TO



if __name__ == "__main__":
    video_path = '/Users/yadubhushan/Documents/media/python_space/resources/social/insta/tech_philosophy/f65f0990-4373-44b2-88cb-6bb3b0037381/video.mp4'
    caption = 'Delve deep into the unique insights of the philosopher Arthur Schopenhauer. Discover how his views on life and existence might stimulate your thoughts 🤔💭 #SchopenhauerWisdom #KeenInsights \n \n \n \n #SchopenhauerWisdom, #KeenInsights, #Philosophy, #LifeInterpretations'
    #uploadToTechPhilosophyInsta(caption=caption, video_path = video_path)
    

    pass

def uploadToTechPhilosophyInsta(caption, video_path=None, images_path=None, thumbnail=None):
    global techPhilosophyInstaClient
    if techPhilosophyInstaClient is None:
        techPhilosophyInstaClient = loginWithConfig(key='SOCIAL_MEDIA_philosophy')
    else:
        print("Using existing client")

    if video_path is None and images_path is None:
        raise Exception("Either video_path or images_path should be provided")

    users_to_mention_string = "philosophyideas,philosophyofexistence,philosophy_fix,philosophors,thephilosophyquote,vedanta.philosophy,brutal.philosophy,philosophical_knowledge,philosophymemecollector,philosophicaloutlaws,existentialism.now,philosophy.of.science,philosophy_now,philosophy_anime_memes,existential.reflections, quotes.from.underground,the_secrets_of_the_universe,philosophyteaches,krishnamurtifoundationtrust,writtenwordss,dostoevsky_is_immortal,classicaldamn,"
    users_to_mention_string = ""
    
    published_TO = {}
    published_TO['INSTAGRAM'] = get_credetials('SOCIAL_MEDIA_philosophy')[0]
    category = "SOCIAL_MEDIA_philosophy"
    try:
        if video_path is not None:
            uploadVideoToInsta(client = techPhilosophyInstaClient, video_path = video_path, caption = caption, users_to_mention_string = users_to_mention_string, category = category, thumbnail = thumbnail)

        if images_path is not None:
            upload_image_to_profile(techPhilosophyInstaClient, images_path, caption, users_to_mention_string, category)

    except ValidationError as e:
        print(f"Validation Error: {e}")  
        
        # Check if the error contains "No sidecar children."
        if "No sidecar children" in str(e):
            print("Error: No sidecar children detected.")
            # Add further handling for this specific error here if needed
            
        # Handle other types of validation errors here
        
    return published_TO




if __name__ == "__main__":
    video_path = '/Users/yadubhushan/Documents/media/python_space/resources/social/insta/tech_philosophy/f65f0990-4373-44b2-88cb-6bb3b0037381/video.mp4'
    caption = 'Delve deep into the unique insights of the philosopher Arthur Schopenhauer. Discover how his views on life and existence might stimulate your thoughts 🤔💭 #SchopenhauerWisdom #KeenInsights \n \n \n \n #SchopenhauerWisdom, #KeenInsights, #Philosophy, #LifeInterpretations'
    #uploadToTechPhilosophyInsta(caption=caption, video_path = video_path)
    
