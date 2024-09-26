from pyexpat import model
import uuid
from imageio import imopen
from instagrapi import Client
import requests
import os
import sys
import json

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
# Define the relative path to go back one directory and then into the 'util' directory
relative_path = os.path.join(current_directory, '../util')

# Get the absolute path
full_path = os.path.abspath(relative_path)

sys.path.insert(0, '/Users/yadubhushan/Documents/workplace/prod/python_scripts/util')
os.path.join(current_directory, '../util')
import util_ConfigManager as ConfigManager
from pydantic import parse_obj_as, HttpUrl
import urllib.request
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag, Usertag
import pprint
from PIL import Image
from os import listdir
from os.path import isfile, join
from pathlib import Path
from . import util_ai_service
from langchain.agents import load_tools
from . import util_google_api
from . import util_audio_elevenlabs

posts_base_dir = "/Users/yadubhushan/Documents/media/python_space/resources/social/insta/bot"
font_loc = "/Users/yadubhushan/Documents/media/python_space/resources/font/Handlee-Regular.ttf"



unique_folder_name = str(uuid.uuid4())
output_folder = os.path.join(posts_base_dir, unique_folder_name)
os.makedirs(output_folder, exist_ok=True)





# Social Media Bot

# Initial Prompt 
initial_prompt = """
Highest grossing Hollywood movies in 1950s.
line1: Name of the movie
line2: Year of release and total collection in USD
"""

inst_content_prompt = """
"As an Instagram content generator, 
your task is to create post content based on 
'{initial_prompt}'.
 The output should span {pages} pages. 
 On each page, include the following data:
 line1 : page title
 line2 : page content
 google_image_search_keyword: Provide keywords for google image search to would result in an image that can be used for the post.
 voice over: provide additional information about the prompt in the voice over. Provide atleast 
 final output : JSON format with keys: {{page_no, line1, line2, voice_over, google_image_search_keyword}}."
 Do not provide anything other than json format as the final output.
"""

llm = ChatOpenAI(temperature=0)

tools_name = ["wolfram-alpha"]
tools = load_tools(tool_names=tools_name)



inst_content_prompt = inst_content_prompt.format(initial_prompt=initial_prompt, pages=5)
result = util_ai_service.get_response_from_gpt4(inst_content_prompt)
# convert the result to json
result_json = json.loads(result)

for idx, page_no in enumerate(result_json):
    page = result_json[page_no]
    
    line1 = page["line1"]
    line2 = page["line2"]
    voice_over = page["voice_over"]
    google_image_search_keyword = page["google_image_search_keyword"]
    best_image_path = util_google_api.get_best_size_image(google_image_search_keyword, output_folder)
    audio_output_file = os.path.join(output_folder, f"audio_{idx}.mp3")
    audio = util_audio_elevenlabs.generateAudio(voice_over, audio_output_file)
    result_json[idx]["image_path"] = best_image_path
    result_json[idx]["audio_path"] = audio_output_file


print(result_json)

