from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_URL
from .firebase import is_ready, init_firebase
from .auth import get_current_user
from .routes.voice import router as voice_router
from .routes.complaints import router as complaints_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield


app = FastAPI(title="GoogleHackathon API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)
app.include_router(complaints_router)

@app.get("/health")
def health():
    init_firebase()
    return {"status": "ok", "firebase_ready": is_ready()}

@app.get("/api/protected")
def protected(user=Depends(get_current_user)):
    return {"uid": user.get("uid"), "email": user.get("email"), "message": "authed OK"}
