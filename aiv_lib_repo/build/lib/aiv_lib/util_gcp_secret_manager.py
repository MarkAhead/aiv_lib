import json
from google.cloud import secretmanager
from .util_ConfigManager import get_google_cred_path

# Constants
VERSION_ID = "latest"  # Constant for the version
client = None
gcred_json = None

def load_credentials(cred_path):
    """Load Google Cloud credentials from the given path."""
    with open(cred_path, 'r') as f:
        return json.load(f)

def initialize_secret_manager_client():
    """Initialize the Secret Manager client using the provided service account credentials."""
    global client, gcred_json
    
    # Get the credential path
    cred_path = get_google_cred_path()
    print(f"Credential Path: {cred_path}")

    # Load credentials
    gcred_json = load_credentials(cred_path)

    # Initialize the Secret Manager client
    client = secretmanager.SecretManagerServiceClient.from_service_account_json(cred_path)

def get_secret_value(secret_id, version_id=VERSION_ID):
    """Fetch the secret value from Google Cloud Secret Manager."""
    global gcred_json, client

    project_id = gcred_json['project_id']

    # Build the full resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version and get the secret value
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

initialize_secret_manager_client()

def main():
    # Define the secret ID and fetch the secret value
    secret_id = "list_of_accounts"  # Replace with your actual secret ID
    secret_value = get_secret_value(secret_id)

    print("Fetched Secret: " + secret_value)

if __name__ == "__main__":
    main()
