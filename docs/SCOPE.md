# Scope — GoogleHackathon_RBU (trimmed)

Kept scope only. The 7-module Hospital Intelligence PRDs were deleted.

## Keep

1. **Facial recognition login** (to build)
   - Base: `frontend/src/app/(auth)/login/` (Google + Email via Firebase Auth today).
   - Plan: `FaceEnroll.tsx` / `FaceLogin.tsx` + `POST /api/face/enroll|verify`
     + `faceProfiles/{uid}` + `signInWithCustomToken`. Google stack only (MediaPipe).
2. **Voice-assisted complaint lodging** (Firestore + Storage backed)
   - Frontend: `frontend/src/app/complain/`, `frontend/src/components/voice/VoiceComplaint.tsx`,
     `frontend/src/lib/voice.ts` (en/hi, zero typing).
   - Audio persistence: raw webm uploaded direct to Firebase Storage
     `complaints/{uid}/<stamp>-<rand>.webm` via `lib/storage.ts:uploadComplaintAudio`
     (owner-only per `storage.rules`, <10 MB); download URL saved as `audio_url`
     on the Firestore `complaints` doc. Upload is best-effort — a failed upload
     still files the transcript, never drops data. Existing docs untouched (create-only).
   - Backend: `backend/app/voice.py` (Gemini primary, Sarvam fallback, heuristic),
     `backend/app/routes/voice.py`, `backend/app/routes/complaints.py`
     (`ComplaintIn.audio_url` accepted, returned on list).
3. **Firebase + Google technologies only**
   - Frontend: `src/lib/firebase-client.ts`, `api.ts` (ID-token header), `storage.ts`,
     `AuthProvider.tsx`.
   - Backend: `app/firebase.py` (Admin SDK), `app/auth.py` (ID-token verify), `app/config.py`.
   - Root: `firebase.json`, `firestore.rules` (`complaints/{id}`), `storage.rules`.

## Deleted

- `docs/PRD*.md`, `docs/CHECKLIST.md` and all 7-module code:
  backend `command|inventory|billing|staff|tasks|patients|ai|audit_read|items` routes + `app/audit.py`,
  frontend `/command|/inventory|/billing|/staff|/patients|/audit|/ai` pages + `lib/mocks.ts`
  + `components/data.tsx` (demo-data helpers) + `lib/firestore.ts` (`exampleItems` demo).

## Verify

- Backend: `pytest` (keeper-only `tests/test_contracts.py`), `uvicorn app.main:app` boots with no keys.
- Frontend: `npm run build` with backend down.
