---
title: REST vs GraphQL Practical Lab
slug: rest-vs-graphql-lab
level: intermediate
estimated_time: 35 minutes
prerequisites:
  - REST vs GraphQL
unlocks:
  - API design comparison
related_topics:
  - APIs
  - API Gateways
code_lab: ../../../labs/05-rest-vs-graphql/rest_vs_graphql_demo.py
official_sources:
  - GraphQLSpec
  - OpenAPI
academic_sources: []
last_verified: 2026-06-09
---

# Practical Lab

## Goal

Build a FastAPI application that exposes both REST and GraphQL interfaces for the same data model.

## What You Will Build

A service with REST endpoints and a GraphQL schema for fetching user data.

## Requirements

- Python 3.11+
- FastAPI
- uvicorn
- strawberry-graphql

## Files

- `labs/05-rest-vs-graphql/rest_vs_graphql_demo.py`
- `labs/05-rest-vs-graphql/test_rest_vs_graphql.py`
- `labs/05-rest-vs-graphql/notebook.ipynb`

## Run the Example

```bash
cd labs/05-rest-vs-graphql
python rest_vs_graphql_demo.py
```

Then open `http://127.0.0.1:8000/docs` for the REST API and use `http://127.0.0.1:8000/graphql` for GraphQL queries.

## Expected Output

The app returns user JSON from REST endpoints and GraphQL query responses for user data.

## Exercises

- Add mutations for user creation.
- Add GraphQL query complexity limits.
- Add caching for the REST endpoint.

## Troubleshooting

- If GraphQL fails to start, ensure `strawberry-graphql` is installed.
- If REST routes return 404, confirm the route path and method.

## Related Topics

- [API Gateways](../02-api-gateways/concept.md)
- [Webhooks](../04-webhooks/concept.md)


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [APIs](../01-apis/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Webhooks](../04-webhooks/concept.md)


