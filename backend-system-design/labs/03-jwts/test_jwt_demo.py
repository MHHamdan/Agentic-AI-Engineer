"""Tests for the JWT lab authentication flow."""

from fastapi.testclient import TestClient
from jwt_demo import app

client = TestClient(app)

def test_token_and_protected_route():
    """Generate a valid token and access a protected route."""
    response = client.post(
        "/token",
        params={"username": "alice", "password": "wonderland"},
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token

    protected = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert protected.status_code == 200
    assert protected.json()["user"] == "alice"

def test_token_invalid():
    """Reject invalid credentials with an unauthorized response."""
    response = client.post("/token", params={"username": "alice", "password": "wrong"})
    assert response.status_code == 401

