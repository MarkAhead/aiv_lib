from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_channel_name(youtube_client):
    """Fetch the authenticated YouTube channel's name and ID."""
    try:
        request = youtube_client.channels().list(part="snippet", mine=True)
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            channel = response["items"][0]
            channel_name = channel["snippet"]["title"]
            channel_id = channel["id"]
            print(f"Authenticated as: {channel_name} || (ID: {channel_id})")
            return channel_name, channel_id
        else:
            print("Error: Could not fetch channel details.")
            return None, None
    except Exception as e:
        print(f"Error fetching channel details: {e}")
        return None, None
    



def upload_video(youtube_client, video_path, title, description, privacy_status="public"):
    """Uploads a video to YouTube."""
    try:
        request = youtube_client.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["Shorts", "YouTubeAPI"],
                    "categoryId": "22"
                },
                "status": {"privacyStatus": privacy_status}
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        print(f"✅ Video uploaded successfully! Video ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ Error uploading video: {e}")

