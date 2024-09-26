import random
import time

from .aws_s3_util import download_s3_object
import shutil
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
from tempfile import gettempdir
amazon_voice_list = ["Kimberly", "Matthew", "Brian", "Joanna", "Ivy", "Arthur"]


def poll_for_task_completion(task_id):
    download_uri = None
    response = fetch_current_task_status(task_id)
    task_status = response["SynthesisTask"]["TaskStatus"]

    counter = 100
    while task_status in ['scheduled', 'inProgress'] and counter > 0:
        print("waiting for the task to complete....")
        time.sleep(5)
        response = fetch_current_task_status(task_id)
        task_status = response["SynthesisTask"]["TaskStatus"]
        counter = counter + 1

    if task_status == 'completed':
        print("audio creation task completed")
        download_uri = response["SynthesisTask"]['OutputUri']
    else:
        print("audio creation task failed")

    return download_uri


def download_s3_file(uri, output_file):
    uri_split = uri.split("/")
    download_s3_object(uri_split[-2], uri_split[-1], output_file)


def fetch_current_task_status(task_id):
    polly = create_polly_client()
    try:
        response = polly.get_speech_synthesis_task(TaskId=str(task_id))

    except (BotoCoreError, ClientError) as error:
        print(error)
        sys.exit(-1)

    if "SynthesisTask" in response:
        return response
    else:
        print("Could not fetch audio conversion status")
        sys.exit(-1)


def start_and_download_audio(content, file_prefix, voiceId="Matthew", TextType='text', output_file=None):
    polly = create_polly_client()
    try:
        # call polly to fetch the audio
        response = polly.start_speech_synthesis_task(
            Engine='neural',
            LanguageCode='en-US',
            OutputFormat='mp3',
            OutputS3BucketName='udaydefaultbucket',
            OutputS3KeyPrefix=file_prefix,
            Text=content,
            TextType=TextType,
            VoiceId=voiceId)
    except (BotoCoreError, ClientError) as error:
        print(error)
        sys.exit(-1)

    if "SynthesisTask" in response:
        task_id = response["SynthesisTask"]['TaskId']
        uri = poll_for_task_completion(task_id)
        download_s3_file(uri, output_file=output_file)
    else:
        print("Could not initiate audio conversion")
        sys.exit(-1)


def create_polly_client():
    session = Session(profile_name="default")
    polly = session.client("polly")
    return polly


# Method to call AWS polly and get the audio file created at given location.
# Use this method if the content size is less than 6000
def getAudioFileForSmallContent(content, output_dir, file_name, voiceId="Matthew"):
    if len(content) > 6000:
        raise Exception("The method should only be used for string content less than 6000 chars")  # example
    session = Session(profile_name="default")
    polly = session.client("polly")

    try:
        # call polly to fetch the audio
        response = polly.synthesize_speech(Engine='neural',
                                           TextType="text",
                                           Text=content,
                                           OutputFormat="mp3",
                                           VoiceId=voiceId)
    except (BotoCoreError, ClientError) as error:
        print(error)
        sys.exit(-1)

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(), file_name)

            try:
                # open the file for writing
                with open(output, "wb") as file:  # writing binary
                    file.write(stream.read())
            except IOError as error:
                print(error)
                sys.exit(-1)

    else:
        print("Could not stream audio")
        sys.exit(-1)

    # Copy file to final output
    final_output = os.path.join(output_dir, file_name)
    shutil.copyfile(output, final_output)
    return final_output



def fetch_random_voice_list():
    combined_voice_list = amazon_voice_list + amazon_voice_list
    random.shuffle(combined_voice_list)
    random_index = random.randint(0, len(combined_voice_list) - 1)
    return combined_voice_list[random_index]


def local_test():
    content = "In a broad sense, philosophy is an activity people undertake when" \
              " they seek to understand fundamental truths about themselves," \
              " the world in which they live, and their relationships to the world and to each other. "
    # start_and_download_audio(content, "first_task")

# local_test()


