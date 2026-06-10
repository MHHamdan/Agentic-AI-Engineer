---
title: APIs Practical Lab
slug: apis-lab
level: beginner
estimated_time: 20 minutes
prerequisites:
  - APIs
unlocks:
  - API Gateways
related_topics:
  - APIs
code_lab: ../../../labs/01-apis/api_demo.py
official_sources:
  - RFC9110
academic_sources: []
last_verified: 2026-06-09
---

# Practical Lab

## Goal

Build and run a simple REST API using FastAPI.

## What You Will Build

A user service with endpoints for listing users, fetching a user, and health checks.

## Requirements

- Python 3.11+
- FastAPI
- uvicorn

## Files

- `labs/01-apis/api_demo.py`
- `labs/01-apis/test_api_demo.py`
- `labs/01-apis/notebook.ipynb`

## Run the Example

```bash
cd labs/01-apis
python api_demo.py
```

Then open `http://127.0.0.1:8000/users` in a browser or use curl.

## Expected Output

JSON responses for user data and a status check from `/health`.

## Exercises

- Add POST support for new users.
- Add query parameters for filtering results.
- Add basic authentication for protected endpoints.

## Troubleshooting

- If dependencies are missing, run `pip install -r requirements.txt`.
- If port 8000 is in use, change `uvicorn` port in `api_demo.py`.

## Related Topics

- [API Gateways](../02-api-gateways/concept.md)
- [REST vs GraphQL](../05-rest-vs-graphql/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Home](../../index.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [REST vs GraphQL](../05-rest-vs-graphql/concept.md)


