#!/bin/bash

PACKAGE_NAME="aiv-lib"  # Replace with your package name
PACKAGE_VERSION="0.1"  # Version to delete
REPOSITORY_NAME="aiv-lib"  # Replace with your repository name
LOCATION="asia-south1"  # Replace with your repository location

set -e  # Exit immediately if a command exits with a non-zero status.

# Cleanup and build
echo "Cleaning up old build artifacts..."
rm -rf dist/ build/ *.egg-info

echo "Building distribution files..."
python setup.py sdist bdist_wheel

# Ensure dist directory is not empty
if [ ! "$(ls -A dist/)" ]; then
  echo "Build failed: No files found in dist/"
  exit 1
fi

# Authenticate with Google Cloud
echo "Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q '.'; then
  echo "No active account found. Logging in..."
  gcloud auth application-default login
fi

# Install dependencies and upload
echo "Installing dependencies..."
pip install --quiet --upgrade keyring keyrings.google-artifactregistry-auth



# Check if the version exists
EXISTS=$(gcloud artifacts versions list \
    --package="$PACKAGE_NAME" \
    --repository="$REPOSITORY_NAME" \
    --location="$LOCATION" \
    --filter="version=$PACKAGE_VERSION" \
    --format="value(version)")

if [ "$EXISTS" == "$PACKAGE_VERSION" ]; then
    echo "Version $PACKAGE_VERSION exists. Deleting..."
    gcloud artifacts versions delete \
        "$PACKAGE_VERSION" \
        --package="$PACKAGE_NAME" \
        --repository="$REPOSITORY_NAME" \
        --location="$LOCATION" \
        --quiet
    echo "Version $PACKAGE_VERSION deleted successfully."
else
    echo "Version $PACKAGE_VERSION does not exist. Skipping deletion."
fi


echo "Uploading package to Artifact Registry..."
twine upload --repository-url https://asia-south1-python.pkg.dev/socialmediabot-398507/aiv-lib/ dist/*

echo "Package upload complete!"




pip install 
