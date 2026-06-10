---
title: REST vs GraphQL Quiz
slug: rest-vs-graphql-quiz
level: intermediate
estimated_time: 10 minutes
prerequisites:
  - REST vs GraphQL
unlocks:
  - API design decisions
related_topics:
  - REST vs GraphQL
code_lab: ../../../labs/05-rest-vs-graphql/rest_vs_graphql_demo.py
official_sources:
  - GraphQLSpec
  - OpenAPI
academic_sources: []
last_verified: 2026-06-09
---

# Quiz

## Multiple Choice

1. GraphQL is primarily designed to solve which problem?
   - A) SQL query optimization
   - B) Over-fetching and under-fetching of data
   - C) CSS layout issues
   - D) Browser compatibility

2. Which REST feature helps with caching responses?
   - A) HTTP verbs
   - B) GraphQL schema
   - C) SQL joins
   - D) Custom query language

## Short Answer

1. Describe one advantage of REST.
2. Describe one advantage of GraphQL.

## Code Review Questions

1. How would you support a GraphQL query in `rest_vs_graphql_demo.py`?
2. What is one way to protect GraphQL from expensive queries?

## System Design Questions

1. When would you prefer REST over GraphQL?
2. When is GraphQL a better fit than REST?

## Answers

<details>
<summary>Show answers</summary>

1. B
2. A

Short answer examples:
- REST advantage: easier caching and simpler client interactions.
- GraphQL advantage: precise data fetching in one request.

Code review examples:
- Expose a `/graphql` endpoint with a schema and resolvers.
- Use query depth limits or persisted queries.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [APIs](../01-apis/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Webhooks](../04-webhooks/concept.md)



