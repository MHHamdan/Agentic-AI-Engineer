---
title: Webhooks Practical Lab
slug: webhooks-lab
level: intermediate
estimated_time: 25 minutes
prerequisites:
  - Webhooks
unlocks:
  - Event-driven architecture
related_topics:
  - APIs
  - JWTs
code_lab: ../../../labs/04-webhooks/webhook_demo.py
official_sources:
  - WebhooksGitHub
academic_sources: []
last_verified: 2026-06-09
---

# Practical Lab

## Goal

Build a webhook receiver and validate an incoming event.

## What You Will Build

A FastAPI listener that accepts webhook posts and verifies a shared signature.

## Requirements

- Python 3.11+
- FastAPI
- uvicorn

## Files

- `labs/04-webhooks/webhook_demo.py`
- `labs/04-webhooks/test_webhook_demo.py`
- `labs/04-webhooks/notebook.ipynb`

## Run the Example

```bash
cd labs/04-webhooks
python webhook_demo.py
```

Then POST a sample event to `http://127.0.0.1:8000/webhook`.

## Expected Output

A 200 response for valid webhook events and a 400 response for invalid signatures.

## Exercises

- Add retry support for failed deliveries.
- Add asynchronous processing for event payloads.
- Add a verification log for webhook deliveries.

## Troubleshooting

- If a request returns 400, confirm the signature header matches the payload.
- If the server does not start, ensure `uvicorn` is installed.

## Related Topics

- [APIs](../01-apis/concept.md)
- [REST vs GraphQL](../05-rest-vs-graphql/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [REST vs GraphQL](../05-rest-vs-graphql/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)


