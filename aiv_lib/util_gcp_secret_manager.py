from google.cloud import secretmanager
from google.auth import default
import os
import json


# Constants
VERSION_ID = "latest"  # Constant for the version

client = None
project_id = None

def get_client():
    global client, project_id

    if client is None:
        client = secretmanager.SecretManagerServiceClient()

    if project_id is None:
        # Try Application Default Credentials to detect project id
        try:
            _, detected_project_id = default()
            if detected_project_id:
                project_id = detected_project_id
        except Exception:
            # Ignore; fall through to other detection methods
            pass

        # Check common environment variables
        if project_id is None:
            for env_var in ("GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT", "GCP_PROJECT", "PROJECT_ID"):
                env_val = os.environ.get(env_var)
                if env_val:
                    project_id = env_val
                    break

        # Try to read from service account json file
        if project_id is None:
            creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                try:
                    with open(creds_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        project_id = data.get("project_id") or data.get("projectId")
                except Exception:
                    # Ignore; we'll validate below
                    pass

    if project_id is None:
        raise RuntimeError(
            "Unable to determine Google Cloud project_id for Secret Manager. "
            "Set GOOGLE_CLOUD_PROJECT or ensure credentials include project_id."
        )

    return client, project_id

def get_secret_value(secret_id, version_id=VERSION_ID):
    """Fetch the secret value from Google Cloud Secret Manager."""
    client, project_id = get_client()
    # Build the full resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    print("name of the secret: " + name)
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
