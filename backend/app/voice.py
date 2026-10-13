"""Voice provider abstraction: Gemini primary, Sarvam fallback.

English + Hindi only. Zero-typing flow:
  audio (webm) -> transcript -> structured complaint -> Firestore.
Keys never leave the backend.
"""
from __future__ import annotations

import httpx

from .config import (
    GOOGLE_API_KEY,
    SARVAM_API_KEY,
    VOICE_PRIMARY,
    VOICE_SUPPORTED_LANGS,
    LANG_TO_BCP47,
)

SUPPORTED_LANGS = VOICE_SUPPORTED_LANGS

UI_STRINGS = {
    "en": {
        "tap_to_speak": "Tap mic and speak your complaint",
        "listening": "Listening… tap stop when done",
        "confirm": "You said:",
        "say_yes": 'Say "Yes" or tap Submit to file it',
        "submitted": "Complaint filed successfully",
    },
    "hi": {
        "tap_to_speak": "माइक दबाएँ और अपनी शिकायत बोलें",
        "listening": "सुन रहे हैं… हो जाए तो रोकें",
        "confirm": "आपने कहा:",
        "say_yes": '"हाँ" बोलें या जमा करें दबाएँ',
        "submitted": "शिकायत सफलतापूर्वक दर्ज हो गई",
    },
}


def normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()[:2]
    return lang if lang in SUPPORTED_LANGS else "en"


def bcp47(lang: str) -> str:
    return LANG_TO_BCP47.get(normalize_lang(lang), "en-IN")


def transcribe_with_gemini(audio_bytes: bytes, lang: str) -> dict:
    """Transcribe via Gemini. Raises on missing key/failure so caller can fall back."""
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not configured")
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = (
        "Transcribe this audio complaint verbatim. "
        f"Language: {bcp47(lang)}. "
        "Return only the transcription, no extra text."
    )
    resp = model.generate_content(
        [
            prompt,
            {"mime_type": "audio/webm", "data": audio_bytes},
        ]
    )
    text = (getattr(resp, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Gemini returned empty transcription")
    return {"text": text, "provider": "gemini", "language": normalize_lang(lang)}


def transcribe_with_sarvam(audio_bytes: bytes, lang: str) -> dict:
    """Transcribe via Sarvam saarika-v2 (good Hindi backup)."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY not configured")
    # Sarvam speech-to-text endpoint; keep thin so SDK swap is easy later.
    resp = httpx.post(
        "https://api.sarvam.ai/speech-to-text",
        headers={"api-subscription-key": SARVAM_API_KEY},
        files={"file": ("complaint.webm", audio_bytes, "audio/webm")},
        data={"language_code": bcp47(lang), "model": "saarika-v2"},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    text = (
        data.get("transcript")
        or data.get("text")
        or data.get("transcripts", [{}])[0].get("transcript", "")
    ).strip()
    if not text:
        raise RuntimeError(f"Sarvam returned empty transcription: {data}")
    return {"text": text, "provider": "sarvam", "language": normalize_lang(lang)}


def transcribe_with_fallback(audio_bytes: bytes, lang: str) -> dict:
    """Primary -> backup. Order controlled by VOICE_PRIMARY env."""
    lang = normalize_lang(lang)
    order = (
        ["gemini", "sarvam"] if VOICE_PRIMARY == "gemini" else ["sarvam", "gemini"]
    )
    errors: dict[str, str] = {}
    for provider in order:
        try:
            if provider == "gemini":
                return transcribe_with_gemini(audio_bytes, lang)
            return transcribe_with_sarvam(audio_bytes, lang)
        except Exception as e:  # noqa: BLE001 - fall through to backup
            errors[provider] = str(e)
    raise RuntimeError(f"All voice providers failed: {errors}")


def structure_complaint(transcript: str, lang: str) -> dict:
    """Turn free speech into complaint fields. Uses Gemini if key present,
    else keyword fallback so /structure works without billing."""
    lang = normalize_lang(lang)
    if GOOGLE_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                "Extract a civic complaint as JSON with keys: "
                "title, category, location, description_en. "
                f"User language: {bcp47(lang)}. "
                "Always include description_en in English even if input is Hindi. "
                "Return ONLY valid JSON.\n\nTranscript:\n" + transcript
            )
            resp = model.generate_content(prompt)
            import json

            return {
                "structured": json.loads((resp.text or "{}").strip()),
                "provider": "gemini",
            }
        except Exception:
            pass  # fall through to heuristic
    # Heuristic fallback: keeps endpoint usable in dev without keys.
    return {
        "structured": {
            "title": transcript[:80],
            "category": "general",
            "location": "",
            "description_en": transcript,
        },
        "provider": "heuristic",
    }
