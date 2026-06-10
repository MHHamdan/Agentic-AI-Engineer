"""REST and GraphQL lab demonstrating both API styles side by side."""

from typing import List

import strawberry
import uvicorn
from fastapi import FastAPI, HTTPException
from strawberry.fastapi import GraphQLRouter

app = FastAPI(title="REST vs GraphQL Demo")

class UserType:
    """Represents a user stored in the demo data model."""

    def __init__(self, id: int, name: str, email: str):
        """Initialize a user data model instance."""
        self.id = id
        self.name = name
        self.email = email

users = [
    UserType(id=1, name="Alice", email="alice@example.com"),
    UserType(id=2, name="Bob", email="bob@example.com"),
]

@app.get("/users")
def list_users():
    """Return a list of users in the REST API."""
    return [user.__dict__ for user in users]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Return a specific user by ID in the REST API."""
    for user in users:
        if user.id == user_id:
            return user.__dict__
    raise HTTPException(status_code=404, detail="User not found")

@strawberry.type
class User:
    """GraphQL type for a user object."""

    id: int
    name: str
    email: str

@strawberry.type
class Query:
    """GraphQL query root for user data."""

    @strawberry.field
    def users(self) -> List[User]:
        """Return all users through the GraphQL API."""
        return [User(id=user.id, name=user.name, email=user.email) for user in users]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("rest_vs_graphql_demo:app", host="127.0.0.1", port=8000, reload=False)
