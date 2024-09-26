import hashlib
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from .util_ConfigManager import get_config_value
import os

FIRE_STORE_KEY_PATH = os.path.join(get_config_value('python_space'), get_config_value('autopomodoro_FIRE_STORE_KEY'))


# Initialize the Firebase Admin SDK
cred = credentials.Certificate(FIRE_STORE_KEY_PATH)
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

# define an enum for activity types
class ActivityType:
    WORK = 'WORK'
    FAP = 'FAP'
    SWIM = 'SWIM'
    EXERCISE = 'EXERCISE'
    BIKE_RIDE = 'BIKE_RIDE'
    OUTSIDE_FOOD = 'OUTSIDE_FOOD'


def push_health_data_to_firestore(combined_data):
    # Iterate over each combined_data entry
    for date, entry in combined_data.items():
        # Check if a document exists for the date
        doc_ref = db.collection('health_store').document(date)
        if doc_ref.get().exists:
            print(f"Skipping data for date: {date}. Document already exists.")
            continue

        # Push the combined_data to Firestore
        doc_ref.set(entry)
        print(f"Data pushed for date: {date}")


def fetch_and_print_health_store_data():
    # Reference to the health_store collection
    health_store_ref = db.collection('health_store')
    
    # Fetch all documents from the collection
    docs = health_store_ref.stream()
    
    # Iterate over each document and print its data
    for doc in docs:
        print(f"Document ID: {doc.id}")
        
        # Extract the document data
        doc_data = doc.to_dict()
        
        # Check if there are activities in the document data
        if 'activities' in doc_data:
            for activity in doc_data['activities']:
                # Check if the activity name is one of the specified ones
                if activity['activityName'] in ['Swim']:
                    print(f"Activity: {activity['activityName']}, Calories: {activity['calories']}")
                    update_activity_store(doc.id, activity['activityName'])
                if activity['activityName'] in ['Sport', 'Workout']:
                    print(f"Activity: {activity['activityName']}, Calories: {activity['calories']}")
                    update_activity_store(doc.id, activity['activityName'])

        print("------------------------------------")

def update_activity_store(id, activityName):
    activity_store_ref = db.collection('activity_store').document(id)
    activity_store_doc_snapshot = activity_store_ref.get()
    
    if activity_store_doc_snapshot.exists:
        activity_store_data = activity_store_doc_snapshot.to_dict()
        activities = activity_store_data.get('activities', [])

        # Define a mapping for activityName to the new activity type
        activity_mapping = {
            'Sport': 'EXERCISE',
            'Workout': 'EXERCISE',
            'Swim': 'SWIMMING'
        }

        # Get the new activity type based on activityName
        new_activity_type = activity_mapping.get(activityName)

        # Check if the new activity type is not already in the activities list
        if new_activity_type and not any(activity['type'] == new_activity_type for activity in activities):
            # Add the new activity type with a count of 1
            activities.append({'type': new_activity_type, 'count': 1})
            # Update the activity_store_data with the modified activities list
            activity_store_data['activities'] = activities
            # Update the document in Firestore
            activity_store_ref.set(activity_store_data)

        print(activity_store_data)


def fetch_all_activity_data():
    pomodoro_ref = db.collection('activity_store')
    docs = pomodoro_ref.stream()
    pomodoro_data = []
    for doc in docs:
        pomodoro_data.append(doc.to_dict())
    return pomodoro_data

import json

def fetch_all_activity_data():
    pomodoro_ref = db.collection('activity_store')
    docs = pomodoro_ref.stream()
    pomodoro_data = []
    for doc in docs:
        pomodoro_data.append(doc.to_dict())
    
    # Convert the list of dictionaries to JSON
    json_data = json.dumps(pomodoro_data, indent=4)
    
    # Print the JSON data
    print(json_data)
    
    return pomodoro_data

def fetch_all_collections():
    # Get all collections
    collections = db.collections()
    
    # Extract the collection names
    collection_names = [collection.id for collection in collections]
    
    # Print the collection names
    print(collection_names)
    
    return collection_names


def fetch_all_video_posts_data():
    prompt_ref = db.collection('social_prompt_store')
    docs = prompt_ref.stream()
    video_post_data = []
    for doc in docs:
        video_post_data.append((doc.id, doc.to_dict()))
    return video_post_data

def fetch_specific_video_post_data(key):
    prompt_ref = db.collection('social_prompt_store').document(key)
    video_post_data = prompt_ref.get().to_dict()
    return video_post_data


def push_video_posts_data_to_firestore(video_post_data):
    key = video_post_data['key']
    doc_ref = db.collection('social_prompt_store').document(key)

    # Deserialize the JSON string into a Python dictionary
    if isinstance(video_post_data, str):
        video_post_data = json.loads(video_post_data)

    # Push the combined_data to Firestore
    cleaned_data = remove_none_values(video_post_data)
    print(cleaned_data)
    doc_ref.set(cleaned_data)
    print(f"Data pushed for key: {key}")


def remove_none_values(data):
    print(type(data))  # Add this line
    print(data)  # Add this line
    if isinstance(data, dict):
        return {k: remove_none_values(v) for k, v in data.items() if v is not None}
    return data

def fetch_and_print_selected_data():
    # Define the collections you want to fetch
    selected_collections = ['weekly_activity_store', 'activity_store']
    
    all_data = {}

    # Iterate over selected collections
    for collection_name in selected_collections:
        collection = db.collection(collection_name)
        docs = collection.stream()
        
        # Extract data from each document in the collection
        all_data[collection_name] = [doc.to_dict() for doc in docs]

    # Convert the data to JSON format
    json_data = json.dumps(all_data)
    
    # Write the JSON data to a file
    with open('selected_firestore_data.json', 'w') as file:
        file.write(json_data)
        prompt =  """
                \n\n\n
                I have provided data for my last week and each day's activity.
  
        Work signifies the time spent on business-related activities.
        Fap signifies the time spent on regressive masturbation activities.
        Swim signifies the time spent on swimming activities.
        Excercise signifies the time spent on workout activities.
        I am learning to ride a bike and BIKE_RIDE signifies the time spent on bike riding activities.
        OUTSIDE_FOOD signifies the number of times I ate outside food.


              I have also provided data for my last week and each day's activity.
                I want you to analyze the data and provide me with a summary of my activity.
                Along with graphs and charts.
            convert into outline markdown
            
        """
        file.write(prompt)


    print("Data written to selected_firestore_data.json")


# fun String.sha256(): String {
#    return MessageDigest.getInstance("SHA-256")
#        .digest(this.toByteArray(Charsets.UTF_8))
#        .joinToString("") { "%02x".format(it) } }
#
def get_hash_key(data):
    hash_result = hashlib.sha256(data.encode("utf-8"))
    hash_key = hash_result.hexdigest()
    return hash_key



def update_work_activity_count(date):
    # Reference to the document for the specified date in the activity_store collection
    activity_store_ref = db.collection('activity_store').document(date)
    activity_store_doc_snapshot = activity_store_ref.get()
    
    if activity_store_doc_snapshot.exists:
        # If the document exists, fetch its data
        activity_store_data = activity_store_doc_snapshot.to_dict()
        activities = activity_store_data.get('activities', [])
        
        # Check if there's an existing 'WORK' activity
        work_activity = next((activity for activity in activities if activity['type'] == 'WORK'), None)
        
        if work_activity:
            # If found, increment its count
            work_activity['count'] += 1
        else:
            # If not found, add a new 'WORK' activity with count 1
            activities.append({'type': ActivityType.WORK, 'count': 1})
        
        # Update the activity_store_data with the modified activities list
        activity_store_data['activities'] = activities
        # Update the document in Firestore
        activity_store_ref.set(activity_store_data)
    else:
        # If the document does not exist, create a new one with a 'WORK' activity count of 1
        activity_store_ref.set({'activities': [{'type': 'WORK', 'count': 1}], 'date' : date})

    print(f"Updated work activity for date: {date}")

def fetch_activity_count_by_date(activity_type, specific_date):
    """
    Fetches the count of a specified activity type from the 'activity_store' collection for a specific date.

    Args:
    activity_type (str): The type of activity to fetch the count for.
    specific_date (str): The specific date in the format 'YYYY-MM-DD' to fetch the activity count for.

    Returns:
    int: The count of the specified activity type for the given date. Returns 0 if not found.
    """
    # Reference to the document for the specified date in the 'activity_store' collection
    activity_store_ref = db.collection('activity_store').document(specific_date)
    activity_store_doc_snapshot = activity_store_ref.get()
    
    if activity_store_doc_snapshot.exists:
        # If the document exists, fetch its data
        activity_store_data = activity_store_doc_snapshot.to_dict()
        activities = activity_store_data.get('activities', [])
        
        # Search for the specified activity type
        for activity in activities:
            if activity['type'] == activity_type.upper():
                return activity.get('count', 0)
                
    # Return 0 if the activity type is not found or the document does not exist
    return 0

def push_notes_to_firestore(notes_data):
    hash_key = notes_data['hash']
    doc_ref = db.collection('notes_store').document(hash_key)

    # Push the combined_data to Firestore
    cleaned_data = remove_none_values(notes_data)
    print(cleaned_data)
    doc_ref.set(cleaned_data)
    print(f"Data pushed for key: {hash_key}")
    
def push_tasks_to_firestore(task_data):
    hash_key = task_data['hash']
    doc_ref = db.collection('tasks_store').document(hash_key)

    # Push the combined_data to Firestore
    cleaned_data = remove_none_values(task_data)
    print(cleaned_data)
    doc_ref.set(cleaned_data)
    print(f"Data pushed for key: {hash_key}")


if __name__ == '__main__':
    # update_work_activity_count('2021-09-01')
    pass
