"""Tests for the APIs lab FastAPI application."""

from api_demo import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Health endpoint should return healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_users():
    """Users list endpoint should return an array of users."""
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user_not_found():
    """Nonexistent user lookup should return a 404 response."""
    response = client.get("/users/999")
    assert response.status_code == 404

