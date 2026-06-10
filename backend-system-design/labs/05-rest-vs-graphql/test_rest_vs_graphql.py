"""Tests for the REST and GraphQL lab demonstration."""

from fastapi.testclient import TestClient
from rest_vs_graphql_demo import app

client = TestClient(app)

def test_rest_list_users():
    """The REST list users endpoint should return a list."""
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_rest_get_user():
    """The REST user endpoint should return the requested user."""
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_graphql_users_query():
    """A GraphQL users query should return user data."""
    query = {"query": "{ users { id name email } }"}
    response = client.post("/graphql", json=query)
    assert response.status_code == 200
    assert response.json()["data"]["users"][0]["name"] == "Alice"

