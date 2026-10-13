# GoogleHackathon — Next.js + FastAPI + Firebase

```
.
├── frontend/  Next.js 16 App Router + TS + Tailwind + Firebase client (Auth/Firestore/Storage)
├── backend/   FastAPI + firebase-admin (ID-token verify + Firestore)
├── firestore.rules / storage.rules / firebase.json
```

## 1. Firebase console (required)
1. console.firebase.google.com > Create project
2. Firestore Database > Create > test mode
3. Authentication > Email/Password + Google
4. Storage > Get started
5. Project Settings > Your apps > Web `</>` > copy config → `frontend/.env.local`
6. Project Settings > Service accounts > Generate key → save as `backend/service-account.json`

## 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # fill values
npm run dev  # http://localhost:3000
```

## 3. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000  # http://localhost:8000/docs
```

Frontend calls backend via `NEXT_PUBLIC_API_URL` + `Authorization: Bearer <Firebase ID token>`.
