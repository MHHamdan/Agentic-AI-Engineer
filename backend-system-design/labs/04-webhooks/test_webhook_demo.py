"""Tests for the webhook lab receiver and signature validation."""

import hashlib
import hmac

from fastapi.testclient import TestClient
from webhook_demo import SECRET, app

client = TestClient(app)

def make_signature(payload: bytes) -> str:
    """Create a signature for the webhook payload."""
    return hmac.new(SECRET, payload, hashlib.sha256).hexdigest()

def test_webhook_valid_signature():
    """A webhook with a valid signature should be accepted."""
    payload = b'{"event_type":"update","resource_id":1}'
    signature = make_signature(payload)
    response = client.post(
        "/webhook",
        data=payload,
        headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "received"

def test_webhook_invalid_signature():
    """A webhook with an invalid signature should be rejected."""
    response = client.post(
        "/webhook",
        data=b'{"event_type":"update","resource_id":1}',
        headers={"X-Hub-Signature-256": "invalid"},
    )
    assert response.status_code == 400

