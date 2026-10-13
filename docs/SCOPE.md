# Scope — GoogleHackathon_RBU (trimmed)

Kept scope only. The 7-module Hospital Intelligence PRDs were deleted.

## Keep

1. **Facial recognition login** (to build)
   - Base: `frontend/src/app/(auth)/login/` (Google + Email via Firebase Auth today).
   - Plan: `FaceEnroll.tsx` / `FaceLogin.tsx` + `POST /api/face/enroll|verify`
     + `faceProfiles/{uid}` + `signInWithCustomToken`. Google stack only (MediaPipe).
2. **Voice-assisted complaint lodging** (already built, keep as-is)
   - Frontend: `frontend/src/app/complain/`, `frontend/src/components/voice/VoiceComplaint.tsx`,
     `frontend/src/lib/voice.ts` (en/hi, zero typing).
   - Backend: `backend/app/voice.py` (Gemini primary, Sarvam fallback, heuristic),
     `backend/app/routes/voice.py`, `backend/app/routes/complaints.py`.
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
