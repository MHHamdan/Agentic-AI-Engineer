"""Tests for the API gateway lab demonstration."""

from fastapi.testclient import TestClient
from gateway_demo import app

client = TestClient(app)

def test_gateway_status():
    """Gateway status endpoint should return online status."""
    response = client.get("/gateway/status")
    assert response.status_code == 200
    assert response.json()["gateway"] == "online"

def test_gateway_list_items():
    """Gateway list endpoint should return a list of items."""
    response = client.get("/gateway/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_internal_list_items():
    """Internal service endpoint should also return a list of items."""
    response = client.get("/internal/items")
    assert response.status_code == 200
    assert len(response.json()) >= 1

