---
title: API Gateways Practical Lab
slug: api-gateways-lab
level: intermediate
estimated_time: 25 minutes
prerequisites:
  - API Gateways
unlocks:
  - JWTs
related_topics:
  - APIs
  - JWTs
code_lab: ../../../labs/02-api-gateways/gateway_demo.py
official_sources:
  - OpenAPI
academic_sources: []
last_verified: 2026-06-09
---

# Practical Lab

## Goal

Build a simple gateway-style routing layer and service simulation using FastAPI.

## What You Will Build

A simulated API gateway that forwards internal routes and applies a simple access policy.

## Requirements

- Python 3.11+
- FastAPI
- uvicorn

## Files

- `labs/02-api-gateways/gateway_demo.py`
- `labs/02-api-gateways/test_gateway_demo.py`
- `labs/02-api-gateways/notebook.ipynb`

## Run the Example

```bash
cd labs/02-api-gateways
python gateway_demo.py
```

Then open `http://127.0.0.1:8000/gateway/items`.

## Expected Output

The gateway returns a forwarded service response and demonstrates request routing.

## Exercises

- Add a rate limit header to the gateway.
- Add service discovery simulation.
- Add logging for backend routing decisions.

## Troubleshooting

- If the service fails to start, ensure `uvicorn` is installed.
- If the route returns 404, confirm the gateway path matches the client request.

## Related Topics

- [APIs](../01-apis/concept.md)
- [JWTs](../03-jwts/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [JWTs](../03-jwts/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Rate Limiting](../07-rate-limiting/concept.md)


