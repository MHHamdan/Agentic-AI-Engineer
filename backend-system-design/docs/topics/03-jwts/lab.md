---
title: JWT Practical Lab
slug: jwts-lab
level: intermediate
estimated_time: 25 minutes
prerequisites:
  - JWTs
unlocks:
  - API security implementation
related_topics:
  - API Gateways
  - APIs
code_lab: ../../../labs/03-jwts/jwt_demo.py
official_sources:
  - JWT7519
academic_sources: []
last_verified: 2026-06-09
---

# Practical Lab

## Goal

Build a FastAPI app that generates and validates JWTs.

## What You Will Build

A token issuance endpoint and a protected resource endpoint.

## Requirements

- Python 3.11+
- FastAPI
- uvicorn
- python-jose

## Files

- `labs/03-jwts/jwt_demo.py`
- `labs/03-jwts/test_jwt_demo.py`
- `labs/03-jwts/notebook.ipynb`

## Run the Example

```bash
cd labs/03-jwts
python jwt_demo.py
```

Then open `http://127.0.0.1:8000/docs` to explore the token issuance path.

## Expected Output

A JSON Web Token is returned from `/token` and a protected response is available at `/protected` when a valid token is provided.

## Exercises

- Add a refresh token endpoint.
- Add an `audience` claim check.
- Add token revocation using a denylist.

## Troubleshooting

- If `python-jose` is missing, run `pip install python-jose`.
- If token validation fails, check the signing secret and algorithm.

## Related Topics

- [API Gateways](../02-api-gateways/concept.md)
- [Webhooks](../04-webhooks/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Long Polling vs WebSockets](../06-long-polling-vs-websockets/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [API Gateways](../02-api-gateways/concept.md)


