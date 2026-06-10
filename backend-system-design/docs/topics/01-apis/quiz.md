---
title: APIs Quiz
slug: apis-quiz
level: beginner
estimated_time: 10 minutes
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

# Quiz

## Multiple Choice

1. Which HTTP method is typically used to retrieve a resource?
   - A) POST
   - B) GET
   - C) DELETE
   - D) PUT

2. What is an important reason to use API versioning?
   - A) Faster response times
   - B) Backward compatibility
   - C) Less documentation
   - D) Reduced memory usage

## Short Answer

1. Explain why input validation is important for APIs.
2. Describe one example of a common API mistake.

## Code Review Questions

1. How would you add an endpoint for creating a user in `api_demo.py`?
2. What response code should you return for a missing resource?

## System Design Questions

1. Describe how an API can support both web and mobile clients.
2. Explain how an API contract helps distributed teams work together.

## Answers

<details>
<summary>Show answers</summary>

1. B
2. B

Short answer examples:
- Validation prevents malformed input, injection, and unexpected server errors.
- A common mistake is exposing implementation details or failing to version endpoints.

Code review examples:
- Add `@app.post("/users")` to create a user.
- Return 404 for missing resources.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [Home](../../index.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [REST vs GraphQL](../05-rest-vs-graphql/concept.md)



