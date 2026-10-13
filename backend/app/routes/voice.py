from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..voice import (
    SUPPORTED_LANGS,
    UI_STRINGS,
    bcp47,
    normalize_lang,
    structure_complaint,
    transcribe_with_fallback,
)

router = APIRouter(prefix="/api/voice", tags=["voice"])

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB cap for hackathon demo


@router.get("/languages")
def languages():
    return {
        "supported": SUPPORTED_LANGS,
        "bcp47": {lang: bcp47(lang) for lang in SUPPORTED_LANGS},
        "strings": UI_STRINGS,
    }


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form("en"),
):
    lang = normalize_lang(language)
    audio = await file.read()
    if not audio:
        raise HTTPException(400, "Empty audio upload")
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio too large (max 10 MB)")
    try:
        return transcribe_with_fallback(audio, lang)
    except RuntimeError as e:
        raise HTTPException(502, str(e))


@router.post("/structure")
async def structure(body: dict):
    transcript = (body.get("transcript") or "").strip()
    lang = normalize_lang(body.get("language", "en"))
    if not transcript:
        raise HTTPException(400, "transcript is required")
    result = structure_complaint(transcript, lang)
    return {"language": lang, **result}
