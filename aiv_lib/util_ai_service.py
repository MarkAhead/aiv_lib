import json
import os
# new
from openai import OpenAI
from .util_ConfigManager import get_config_value


# Load your OpenAI API key from an environment variable or secret management service
client = OpenAI()

GPT_3_5 = "gpt-3.5-turbo"
GPT_4 = "gpt-4"


prompt_text_summarize_task = """Summarize: The following is a unorganized task description that 
needs to be summarized. The description should be action oriented and should not be longer than 3 sentences.
Try to use the original words from the description as much as possible.
Task description: {task_description}
"""


def get_response_from_gpt3_5(prompt_text: str):
    """Get a response from the ChatGPT 3.5 model."""
    response = client.Completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text},
        ],
    )
    return response.choices[0].message["content"].strip()


def get_response_from_gpt4(prompt_text: str):
    response = client.chat.completions.create(
        model= GPT_4,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text},
        ],
    )
    return response.choices[0].message["content"].strip()


def summarize_task(task_description):
    formatted_prompt = prompt_text_summarize_task.format(
        task_description=task_description
    )
    response = get_response_from_gpt3_5(formatted_prompt)
    print(f"Response from AI: {response}")
    return response


prompt_text_description_summarize_task = """
    Title: Enhancing Jira Task Descriptions with AI in less than 10 sentences

    Description: You are tasked with improving the quality of task descriptions 
    in your project's Jira board. Your goal is to create more detailed and action-oriented 
    descriptions that include a breakdown of the task and a problem-solving approach.

    Prompt:
    You're working on a task titled "{title}". 

    The current description outlines "{task_description}"

    Your task is to generate a more detailed description in the following format:

    1. **Task Summary:** 

    2. **Problem-Solving Actions oriented task breakdown:** Offer a
    problem-solving approach for tackling this task effectively. 
    What strategies or actions can be taken to ensure the successful 
    implementation of {title}. How can the error
    handling process be enhanced to provide a seamless user experience?

    """


def summarize_task_breakdown(title, task_description):
    formatted_prompt = prompt_text_description_summarize_task.format(
        title=title, task_description=task_description
    )
    response = get_response_from_gpt3_5(formatted_prompt)
    print(f"Response from AI: {response}")
    return response


prompt_image_generation_task = """
    You are an image generation AI assistant. You are tasked with generating an image based on the following input text description:
    {task_description}

    The generation prompt should use {image_style} style. 

    features to add to the prompt text description:
    1. The entire image description should be divided into 3 parts: Part 1 describes the exact elements to add in the image with their colors, sizes, and positions. 
        Part 2 describes the style of the image. 
        Part 3 describes the atmosphere of the image.
    2. USE The following art movements to describe the style of the image: {image_style}
    3. Use the following prompt as an example of what the prompt should look like. 
    {prompt_example}

    Output format = return in an output format like this in a JSON array:
            {
                "text": "Mahatma Gandhi standing on the moon's surface with a space rover nearby.",
                "weight": 0.25
            },
            {
                "text": "Indian flag prominently waving in the background, symbolizing India's presence on the moon.",
                "weight": 0.25
            },
            {
                "text": "The moon's craters and texture are visible, adding to the lunar ambiance.",
                "weight": 0.5
            },
            {
                "text": "Gandhi is wearing his iconic round glasses and dhoti, but with a space helmet for protection.",
                "weight": 0.5
            }
"""


def image_prompt_generation_task(task_description, image_style, prompt_example):
    formatted_prompt = prompt_image_generation_task.format(
        task_description=task_description,
        image_style=image_style,
        prompt_example=prompt_example,
    )
    response = get_response_from_gpt3_5(formatted_prompt)
    print(f"Response from AI: {response}")
    return response


if __name__ == "__main__":
    prompt = """
    Craft a narrative script for a 1-minute documentary video focusing {topic}. The script should have a narrative style, where each scene, lasting 5 seconds, is clearly outlined with comprehensive details on the topic. The script should also indicate the appropriate background music or sounds to be used in conjunction with the voice-over narration.

    At specific time intervals within each voice-over detailed Narration, indicate when to incorporate sounds and transition between images.

    For this project, please adhere to the following guidelines:

    Develop three separate timelines: 1st Timeline for background sounds/music and 2nd timeline for another for voice-over detailed narration, along with a third for image/visual cues detailing the information about the image source (either from Bing search or AI-generated images).
    Include sounds in only 1/3rd of the scenes, focusing on the ones with the most impact.
    The voice-over narration should be detailed and comprehensive, with a focus on the topic.
    For the sound timeline, specify the scene_number, sound_search_keyword, and the start and end time of the sound segment.
    Similarly, in the voice-over timeline, mention the scene_number, voice_over text, and its respective start and end time.
    In the visual timeline, provide the scene number, keywords for Bing_image_search, prompts for AI image generation, and the timeline for image display.
    Please present the response in a compressed JSON format.
    Provide 5 second intervals for each scene, with a total of 12 scenes.
    """
    topic = "on the life of Mahatma Gandhi"
    formatted_prompt = prompt.format(topic = topic)

    response = get_response_from_gpt4(formatted_prompt)
    print(f"Response: {response}")



def return_empty_social_media_posts(prompt_data_list):
    return [
        (key, data) for key, data in prompt_data_list 
        if data.get('post_states') 
        and "PROMPT_CREATED" in data.get('post_states')
        and "INITIAL_ARTIFACTS_CREATED" not in data.get('post_states')
    ]



def get_json_from_result(result, retry_prompt):
    MAX_AI_RETRIES = 3
    retries = 0
    
    while retries < MAX_AI_RETRIES:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            retries += 1
            if retries == MAX_AI_RETRIES:
                raise json.JSONDecodeError("Max retries reached, failed to decode JSON")
                
            retry_prompt_filled = retry_prompt.format(result=result)
            result = get_response_from_gpt3_5(retry_prompt_filled)


def get_ai_result_with_retry(initial_prompt, retry_prompt):
    result = get_response_from_gpt4(initial_prompt)
    result_json = get_json_from_result(result, retry_prompt)
    return result_json






