import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_PATH", "./service-account.json"
)
FIRESTORE_EMULATOR_HOST = os.getenv("FIRESTORE_EMULATOR_HOST", "")

# Voice assistance (English + Hindi, zero typing)
# Keys stay server-side. Frontend never sees these.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
VOICE_PRIMARY = os.getenv("VOICE_PRIMARY", "gemini")  # gemini | sarvam
VOICE_SUPPORTED_LANGS = ["en", "hi"]
LANG_TO_BCP47 = {"en": "en-IN", "hi": "hi-IN"}
