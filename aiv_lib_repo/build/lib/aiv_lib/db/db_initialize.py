import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from ..util_ConfigManager import get_google_cred_path


# Initialize the Firebase Admin SDK
cred = credentials.Certificate(get_google_cred_path())
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()