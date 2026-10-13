from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..firebase import get_db
from ..auth import get_current_user
from ..voice import normalize_lang
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


class ComplaintIn(BaseModel):
    transcript_raw: str
    language: str = "en"
    audio_url: str | None = None
    title: str | None = None
    category: str | None = None
    location: str | None = None
    description_en: str | None = None


@router.post("")
def create_complaint(body: ComplaintIn, user=Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Firestore not configured")
    if not body.transcript_raw.strip():
        raise HTTPException(400, "transcript_raw is required (voice-only flow)")
    lang = normalize_lang(body.language)
    doc = {
        "transcript_raw": body.transcript_raw,
        "language": lang,
        "audio_url": body.audio_url,
        "title": body.title or body.transcript_raw[:80],
        "category": body.category or "general",
        "location": body.location or "",
        "description_en": body.description_en or body.transcript_raw,
        "uid": user.get("uid"),
        "status": "filed",
        "createdAt": SERVER_TIMESTAMP,
    }
    _, ref = db.collection("complaints").add(doc)
    return {"id": ref.id, **{k: v for k, v in doc.items() if k != "createdAt"}}


@router.get("")
def list_complaints(limit: int = 20, user=Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Firestore not configured")
    docs = (
        db.collection("complaints")
        .where("uid", "==", user.get("uid"))
        .order_by("createdAt", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]
