"""Webhook lab demonstration for validating incoming signed events."""

import hashlib
import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

app = FastAPI(title="Webhook Demo")
SECRET = b"secret-hook-key"

class WebhookEvent(BaseModel):
    """Schema for webhook event payloads."""

    event_type: str
    resource_id: int
    payload: dict

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify the webhook signature against the shared secret."""
    expected = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
):
    """Receive and validate a webhook request payload."""
    body = await request.body()
    if not x_hub_signature_256 or not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=400, detail="Invalid signature")
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run("webhook_demo:app", host="127.0.0.1", port=8000, reload=False)
