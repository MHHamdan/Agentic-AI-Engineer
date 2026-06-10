---
title: REST vs GraphQL Math and Theory Foundation
slug: rest-vs-graphql-math-foundation
level: intermediate
estimated_time: 30 minutes
prerequisites:
  - APIs
unlocks:
  - API design evaluation
related_topics:
  - REST vs GraphQL
  - APIs
code_lab: ../../../labs/05-rest-vs-graphql/rest_vs_graphql_demo.py
official_sources:
  - GraphQLSpec
  - OpenAPI
academic_sources: []
last_verified: 2026-06-09
---

# Math and Theory Foundation

## Core Formula or Model

Compare payload size and request count for REST vs GraphQL.

- REST cost = number of endpoints × request size
- GraphQL cost = query complexity × response size

## Intuition

REST often requires multiple endpoints for related data. GraphQL allows one request to fetch precisely requested fields.

## Step-by-Step Example

1. A client needs user and order details.
2. REST may require two requests with two responses.
3. GraphQL can fetch both sets in one query.
4. Response size depends on fields selected, so GraphQL can reduce over-fetching.

## Engineering Interpretation

GraphQL is powerful for clients that need composite views. REST is more predictable and easier to cache.

## Limitations

- GraphQL queries must be controlled to avoid costly execution.
- REST over-fetching is often simpler to handle than GraphQL complexity.

## Related Topics

- [API Gateways](../02-api-gateways/concept.md)
- [APIs](../01-apis/concept.md)

## References

The GraphQL specification explains query execution and field selection semantics. [GraphQLSpec]


## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [APIs](../01-apis/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Webhooks](../04-webhooks/concept.md)


