import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from ..db.db_standalone import fetch_youtube_profile, save_youtube_profile
from ..db.db_account_metadata import create_account_document
from .channel import get_channel_name
from ..db.model import AccountType

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
CLIENT_SECRET_FILE = os.environ.get("YOUTUBE_PUBLISHER_DESKTOP_CRED")


def authenticate_account():
    """
    Perform Google OAuth authentication (launching browser flow) 
    and return brand-new credentials. This is typically only used
    when registering a brand-new YouTube account.
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    return credentials

def revalidate_credentials():
    credentials_obj = authenticate_account()
    youtube_client = build("youtube", "v3", credentials=credentials_obj)
    channel_name, channel_id = get_channel_name(youtube_client)
    print(f"Fetched channel name '{channel_name}' from YouTube API and channel id '{channel_id}'")

    create_account_document(channel_id, channel_name, AccountType.YOUTUBE)

def register_youtube_account():
    """
    Register a new YouTube account in Firestore by performing 
    a full OAuth flow (browser-based) and storing the resulting credentials.
    """
    credentials_obj = authenticate_account()
    youtube_client = build("youtube", "v3", credentials=credentials_obj)

    channel_name, channel_id = get_channel_name(youtube_client)
    print(f"Fetched channel name '{channel_name}' from YouTube API and channel id '{channel_id}'")

    create_account_document(channel_id, channel_name, AccountType.YOUTUBE)
    print(f"Created account metadata document for {channel_id} with username '{channel_name}'")

    # Save the new credentials in Firestore
    save_youtube_profile(channel_id, json.loads(credentials_obj.to_json()))
    print(f"Saved credentials to Firestore for {channel_id} with username '{channel_name}'")

    return channel_id


def authenticate_youtube(channel_id):
    """
    Retrieve stored credentials for the given channel_id. If they are
    invalid but have a refresh token, refresh them. If no credentials
    exist, prompt the caller to register the account first.
    """
    if not channel_id:
        raise Exception("Channel ID is required")

    print("Authenticating YouTube with channel ID:", channel_id)

    # 1. Attempt to fetch credentials from Firestore
    token_data = fetch_youtube_profile(channel_id)
    if not token_data:
        # No stored credentials -> must register
        raise Exception("No credentials found. Please register the account first.")

    print("Fetched token data from Firestore.")
    credentials_obj = Credentials.from_authorized_user_info(token_data, SCOPES)

    # 2. If credentials have expired but we have a refresh token, refresh them
    if not credentials_obj.valid:
        if credentials_obj.refresh_token:
            print("Credentials are expired. Attempting to refresh using refresh token...")
            credentials_obj.refresh(Request())
        else:
            raise Exception("Stored credentials are invalid, and no refresh token is available. "
                            "Please re-register the account.")

    # 3. Build the YouTube client with the (possibly refreshed) credentials
    youtube_client = build("youtube", "v3", credentials=credentials_obj)
    print("YouTube client successfully built with valid credentials.")

    # 4. Persist updated credentials if they have changed (e.g., refresh token usage).
    #    This ensures the new access token/expiration is saved back to Firestore.
    save_youtube_profile(channel_id, json.loads(credentials_obj.to_json()))
    print("Updated credentials saved to Firestore.")

    return youtube_client


if __name__ == "__main__":
    # Example usage:
    # 1. For a brand new account (no saved tokens), you must first register:
    #    channel_id = register_youtube_account()
    #
    # 2. In subsequent runs or different scripts, you can use:
    #    youtube_client = authenticate_youtube(channel_id)

    channel_id = 'UC-9-kyTW8ZkZNDHQJ6FgpwQ'
    youtube_client = authenticate_youtube(channel_id)
    # Now you can use `youtube_client` to interact with the YouTube Data API.
