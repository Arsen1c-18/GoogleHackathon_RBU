"""Minimal contract tests: voice-assisted complaint lodging + health only."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_200():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_voice_languages_200():
    r = client.get("/api/voice/languages")
    assert r.status_code == 200
    body = r.json()
    assert "supported" in body
    assert set(body["supported"]) == {"en", "hi"}


def test_voice_structure_requires_transcript():
    r = client.post("/api/voice/structure", json={"transcript": ""})
    assert r.status_code == 400


def test_voice_structure_heuristic():
    r = client.post(
        "/api/voice/structure",
        json={"transcript": "road is broken near my house", "language": "en"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "structured" in body


def test_complaints_reject_without_creds():
    # No service-account in CI: expect 503 hint; with creds but no token: 401.
    r = client.post(
        "/api/complaints", json={"transcript_raw": "x", "language": "en"}
    )
    assert r.status_code in (401, 503), f"-> {r.status_code}: {r.text[:200]}"
