from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as fb_auth

from .firebase import init_firebase

bearer = HTTPBearer(auto_error=False)

async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    init_firebase()
    if not firebase_admin._apps:
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured. Add backend/service-account.json",
        )
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer ID token from frontend Firebase Auth",
        )
    try:
        decoded = fb_auth.verify_id_token(creds.credentials)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
