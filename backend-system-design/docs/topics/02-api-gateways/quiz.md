---
title: API Gateways Quiz
slug: api-gateways-quiz
level: intermediate
estimated_time: 10 minutes
prerequisites:
  - API Gateways
unlocks:
  - JWTs
related_topics:
  - API Gateways
code_lab: ../../../labs/02-api-gateways/gateway_demo.py
official_sources:
  - OpenAPI
academic_sources: []
last_verified: 2026-06-09
---

# Quiz

## Multiple Choice

1. What is a primary purpose of an API gateway?
   - A) Database management
   - B) Request routing and security enforcement
   - C) Front-end rendering
   - D) Local caching only

2. Which is a valid failure mode for a gateway?
   - A) Poor query parsing
   - B) Gateway outage affecting all services
   - C) Client-side CSS errors
   - D) Incompatible database schema

## Short Answer

1. What is one tradeoff of centralizing logic in an API gateway?
2. Why should a gateway avoid implementing business domain logic?

## Code Review Questions

1. How would you simulate route selection in `gateway_demo.py`?
2. Suggest one metric that should be tracked at the gateway.

## System Design Questions

1. Explain how an API gateway can support multiple backend services.
2. Describe why an API gateway is useful in a microservices environment.

## Answers

<details>
<summary>Show answers</summary>

1. B
2. B

Short answer examples:
- A tradeoff is a single point of failure and potential bottleneck.
- A gateway should remain thin to avoid coupling and keep service logic separate.

Code review examples:
- Simulate route selection using a routing table or path-based dispatch.
- Track gateway response time or authentication failure rate.

</details>

## Navigation

- Home: [System Engineering Tutorials](../../index.md)
- Learning Path: [Full roadmap](../../learning-path.md)
- Topic Index: [All topics](../../topic-index.md)
- Previous Topic: [JWTs](../03-jwts/concept.md)
- Topic Pages: [Concept](concept.md) | [Foundation](foundation.md) | [Math Foundation](math-foundation.md) | [Lab](lab.md) | [Quiz](quiz.md)
- Next Topic: [Rate Limiting](../07-rate-limiting/concept.md)



