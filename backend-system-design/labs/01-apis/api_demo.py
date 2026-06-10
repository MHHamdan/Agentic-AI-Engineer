"""APIs lab demonstration with FastAPI user endpoints."""

from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    """Represents a single user entity in the API."""

    id: int
    name: str
    email: str

users_db = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
]

@app.get("/health")
def health_check():
    """Return the health status for the API service."""
    return {"status": "healthy"}

@app.get("/users", response_model=List[User])
def list_users():
    """Return a list of users from the in-memory store."""
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """Return a single user by identifier or raise 404."""
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run("api_demo:app", host="127.0.0.1", port=8000, reload=False)
