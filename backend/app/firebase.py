import os
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

from .config import FIREBASE_SERVICE_ACCOUNT_PATH, FIREBASE_STORAGE_BUCKET

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
        options = {"storageBucket": FIREBASE_STORAGE_BUCKET} if FIREBASE_STORAGE_BUCKET else None
        firebase_admin.initialize_app(cred, options) if options else firebase_admin.initialize_app(cred)
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

def get_bucket():
    """Firebase Storage bucket, or None when not configured (no bucket = no crash)."""
    init_firebase()
    if not firebase_admin._apps:
        return None
    try:
        return storage.bucket()
    except Exception:
        return None

def is_ready() -> bool:
    return bool(firebase_admin._apps)
