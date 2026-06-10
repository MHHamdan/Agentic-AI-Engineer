"""JWT lab demonstration with token issuance and verification."""

from datetime import datetime, timedelta

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET_KEY = "change-me-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

app = FastAPI(title="JWT Demo")
security = HTTPBearer()
security_dependency = Security(security)

class TokenResponse(BaseModel):
    """Response schema for an issued access token."""

    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    """Represents a user identity for authentication."""

    username: str

users = {"alice": "wonderland", "bob": "builder"}

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT with an expiration claim."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token", response_model=TokenResponse)
def login(username: str, password: str):
    """Validate credentials and return an access token."""
    if users.get(username) != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username})
    return {"access_token": token}

def verify_token(
    credentials: HTTPAuthorizationCredentials = security_dependency,
) -> str:
    """Verify the provided JWT and return the authenticated username."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
            )
        return username
    except JWTError as error:
        raise HTTPException(
            status_code=401,
            detail="Token validation failed",
        ) from error

@app.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    """Return a protected message for valid authenticated requests."""
    return {"message": "Access granted", "user": username}

if __name__ == "__main__":
    uvicorn.run("jwt_demo:app", host="127.0.0.1", port=8000, reload=False)
