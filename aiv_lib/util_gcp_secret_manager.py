from google.cloud import secretmanager
from google.auth import default


# Constants
VERSION_ID = "latest"  # Constant for the version

client = secretmanager.SecretManagerServiceClient()
_, project_id = default()

def get_secret_value(secret_id, version_id=VERSION_ID):
    """Fetch the secret value from Google Cloud Secret Manager."""
    
    # Build the full resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version and get the secret value
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def main():
    # Define the secret ID and fetch the secret value
    secret_id = "list_of_accounts"  # Replace with your actual secret ID
    secret_value = get_secret_value(secret_id)

    print("Fetched Secret: " + secret_value)

if __name__ == "__main__":
    main()
