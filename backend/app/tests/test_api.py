# backend/app/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system_health():
    """Verifies gateway health checks."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_unauthorized_endpoints():
    """Asserts that secure endpoints require valid JWT headers."""
    response = client.post("/api/v1/predict/", json={
        "track_name": "Test Track",
        "artist_name": "Test Artist",
        "genre": "pop",
        "beats_per_minute": 120.0,
        "energy": 80.0,
        "danceability": 70.0,
        "loudness_db": -5.0,
        "acousticness": 10.0,
        "valence": 60.0
    })
    # Must reject without Bearer Authorization header
    assert response.status_code == 401
