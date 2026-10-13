# Backend (FastAPI + Firebase Admin)

## Setup
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Download service-account.json from Firebase Console >
# Project Settings > Service accounts > Generate new private key
# Save as backend/service-account.json (gitignored)
uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`
- Protected: `GET /api/protected` with `Authorization: Bearer <Firebase ID token>`

## Voice (English + Hindi, zero typing)
- `GET /api/voice/languages` — supported langs + UI strings
- `POST /api/voice/transcribe` — multipart `file` (webm, max 10MB) + `language=en|hi`; Gemini primary, Sarvam fallback via `VOICE_PRIMARY`
- `POST /api/voice/structure` — `{"transcript","language"}` → complaint fields (Gemini or heuristic)
- `POST /api/complaints` (authed) — saves to Firestore `complaints`
- Env: `GOOGLE_API_KEY=`, `SARVAM_API_KEY=`, `VOICE_PRIMARY=gemini`
