import os
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

from .config import FIREBASE_SERVICE_ACCOUNT_PATH

_initialized = False

def init_firebase():
    global _initialized
    if _initialized:
        return
    if firebase_admin._apps:
        _initialized = True
        return
    # Emulator or no-creds local dev: skip init, routes will 503 with hint
    if os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
        cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        _initialized = True
    else:
        print(
            f"[firebase] No service account at {FIREBASE_SERVICE_ACCOUNT_PATH}. "
            "Run with real creds for Firestore/Auth. /health still works."
        )

def get_db():
    init_firebase()
    if not firebase_admin._apps:
        return None
    return firestore.client()

def is_ready() -> bool:
    return bool(firebase_admin._apps)
